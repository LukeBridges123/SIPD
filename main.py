"""
SIPD - Spatial Iterated Prisoner's Dilemma

Main entry point for the simulation.
"""

import asyncio
import pygame
import sys
import random
from strategies import always_defect, always_cooperate, tit_for_tat, pavlov, revenger, prisoners_dilemma, tf2t
from grid import Grid
from ui import DEFAULT_THEME, SimulatorUI


class SimulationState:
    """Manages the simulation state and parameters"""

    # Default parameter values
    DEFAULT_GRID_ROWS = 50
    DEFAULT_GRID_COLS = 50
    DEFAULT_ROUNDS = 1000
    DEFAULT_NOISE = 0.0
    DEFAULT_MUTATION = 0.0
    DEFAULT_SPEED = 10  # steps per second

    def __init__(self):
        self.strategies = [always_cooperate, always_defect, tit_for_tat, pavlov, revenger, tf2t]
        self.colors = {
            "Always cooperate": (46, 204, 113),    # Emerald green
            "Always defect": (231, 76, 60),         # Alizarin red
            "Tit-for-tat": (52, 152, 219),          # Peter river blue
            "Pavlov": (243, 156, 18),               # Orange
            "Revenger": (155, 89, 182),             # Amethyst purple
            "Tit-for-two-tats": (26, 188, 156)      # Turquoise
        }

        # Simulation parameters
        self.reset_parameters()

        # State tracking
        self.seed = None
        self.step_count = 0
        self.board = None
        self.paused = True  # Start paused
        self.last_auto_step = 0

        self.new_simulation(new_seed=True)

    def reset_parameters(self):
        """Reset all parameters to defaults"""
        self.grid_rows = self.DEFAULT_GRID_ROWS
        self.grid_cols = self.DEFAULT_GRID_COLS
        self.rounds = self.DEFAULT_ROUNDS
        self.noise = self.DEFAULT_NOISE
        self.mutation_rate = self.DEFAULT_MUTATION
        self.auto_step_delay = int(1000 / self.DEFAULT_SPEED)

    def new_simulation(self, new_seed=True):
        """Start a new simulation, optionally with a new random seed"""
        if new_seed:
            self.seed = random.randint(0, 2**32 - 1)

        random.seed(self.seed)
        self.board = Grid(
            strategies=self.strategies,
            rows=self.grid_rows,
            cols=self.grid_cols,
            game=prisoners_dilemma,
            rounds=self.rounds,
            noise=self.noise,
            mutation_rate=self.mutation_rate
        )
        self.board.populate_randomly()
        self.step_count = 0

    def update_live_params(self):
        """Update parameters that can change without restart"""
        self.board.mutation_rate = self.mutation_rate
        # Note: noise requires recomputing matchup table, so it needs restart

    def step(self):
        """Advance simulation by one generation"""
        self.board.update_grid()
        self.step_count += 1


async def main():
    """Main event loop"""
    sim = SimulationState()
    ui = SimulatorUI(sim, DEFAULT_THEME)

    running = True
    pending_restart = False  # Track if we need to restart after param changes

    while running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                ui.handle_resize(event.w, event.h)
                ui.window = pygame.display.set_mode(
                    (ui.window_width, ui.window_height),
                    pygame.RESIZABLE
                )

            elif event.type == pygame.KEYDOWN:
                # Check if any parameter is being edited
                done, _changed, needs_restart = ui.handle_param_text_input(event)
                if done:
                    if needs_restart:
                        pending_restart = True
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    sim.step()
                elif event.key == pygame.K_p:
                    sim.paused = not sim.paused
                elif event.key == pygame.K_r:
                    sim.new_simulation(new_seed=False)
                    ui.resize_window_to_fit_grid()
                    pending_restart = False
                elif event.key == pygame.K_n:
                    sim.new_simulation(new_seed=True)
                    ui.resize_window_to_fit_grid()
                    pending_restart = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check for double-click on parameters first
                    if event.type == pygame.MOUSEBUTTONDOWN and hasattr(event, 'button') and event.button == 1:
                        # Track double-clicks (pygame doesn't have built-in double-click detection)
                        # So we'll just check on single click if enough time has passed
                        click_time = pygame.time.get_ticks()
                        if hasattr(ui, '_last_click_time') and hasattr(ui, '_last_click_pos'):
                            time_diff = click_time - ui._last_click_time
                            pos_diff = ((mouse_pos[0] - ui._last_click_pos[0])**2 +
                                      (mouse_pos[1] - ui._last_click_pos[1])**2)**0.5
                            if time_diff < 400 and pos_diff < 10:  # Double-click detected
                                ui.handle_param_double_click(mouse_pos)
                                ui._last_click_time = 0  # Reset to prevent triple-click
                                continue
                        ui._last_click_time = click_time
                        ui._last_click_pos = mouse_pos

                    # Check main buttons
                    if ui.btn_step.is_clicked(mouse_pos, True):
                        sim.step()
                    elif ui.btn_play.is_clicked(mouse_pos, True):
                        sim.paused = not sim.paused
                    elif ui.btn_restart_same.is_clicked(mouse_pos, True):
                        sim.new_simulation(new_seed=False)
                        ui.resize_window_to_fit_grid()
                        pending_restart = False
                    elif ui.btn_new_seed.is_clicked(mouse_pos, True):
                        sim.new_simulation(new_seed=True)
                        ui.resize_window_to_fit_grid()
                        pending_restart = False
                    elif ui.btn_reset.is_clicked(mouse_pos, True):
                        ui.reset_params_to_defaults()
                        pending_restart = True  # Params changed, need restart
                    else:
                        # Check parameter controls
                        changed, needs_restart = ui.handle_param_click(mouse_pos)
                        if needs_restart:
                            pending_restart = True

        # Update hover states
        ui.update_controls(mouse_pos)

        # Auto-step when not paused
        if not sim.paused and current_time - sim.last_auto_step >= sim.auto_step_delay:
            sim.step()
            sim.last_auto_step = current_time

        ui.draw()

        # Draw restart pending indicator if needed
        if pending_restart:
            indicator_text = ui.theme.font_small.render(
                "Parameters changed - press R or N to apply",
                True, (220, 180, 80)
            )
            ui.window.blit(indicator_text, (ui.padding, ui.window_height - ui.bottom_panel_height + 40))
            pygame.display.flip()

        await asyncio.sleep(0)
        ui.clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())

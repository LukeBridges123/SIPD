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
from ui import DEFAULT_THEME, SimulatorUI, StatsUI
from ui.components import Button


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

        # Census history for time series
        self.census_history = []  # List of {strategy_name: percentage} dicts

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

        # Reset and record initial census
        self.census_history = []
        self.record_census()

    def update_live_params(self):
        """Update parameters that can change without restart"""
        self.board.mutation_rate = self.mutation_rate
        # Note: noise requires recomputing matchup table, so it needs restart

    def step(self):
        """Advance simulation by one generation"""
        self.board.update_grid()
        self.step_count += 1
        self.record_census()

    def record_census(self):
        """Record current census to history"""
        census = self.board.get_census_percentages()
        self.census_history.append(census)

    def get_current_census(self):
        """Get current census percentages"""
        return self.board.get_census_percentages()


# Screen modes
SCREEN_SIMULATOR = 0
SCREEN_STATS = 1


async def main():
    """Main event loop"""
    sim = SimulationState()
    sim_ui = SimulatorUI(sim, DEFAULT_THEME)
    stats_ui = StatsUI(sim, DEFAULT_THEME)

    # Current screen
    current_screen = SCREEN_SIMULATOR

    # Create screen toggle button (in bottom panel)
    btn_stats = Button(
        sim_ui.window_width - 200, sim_ui.window_height - sim_ui.bottom_panel_height + 60,
        90, 28, "Stats", (80, 100, 120), (100, 130, 160)
    )

    def update_stats_button_position():
        """Update stats button position after window/grid changes"""
        btn_stats.rect.x = sim_ui.window_width - 200
        btn_stats.rect.y = sim_ui.window_height - sim_ui.bottom_panel_height + 60

    running = True
    pending_restart = False  # Track if we need to restart after param changes

    while running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                sim_ui.handle_resize(event.w, event.h)
                sim_ui.window = pygame.display.set_mode(
                    (sim_ui.window_width, sim_ui.window_height),
                    pygame.RESIZABLE
                )
                update_stats_button_position()

            elif event.type == pygame.KEYDOWN:
                # S key toggles stats view
                if event.key == pygame.K_s:
                    current_screen = SCREEN_STATS if current_screen == SCREEN_SIMULATOR else SCREEN_SIMULATOR
                    btn_stats.text = "Grid" if current_screen == SCREEN_STATS else "Stats"
                    continue

                # ESC returns to simulator from stats, or quits from simulator
                if event.key == pygame.K_ESCAPE:
                    if current_screen == SCREEN_STATS:
                        current_screen = SCREEN_SIMULATOR
                        btn_stats.text = "Stats"
                    else:
                        running = False
                    continue

                # These controls work in both views
                if event.key == pygame.K_SPACE:
                    sim.step()
                elif event.key == pygame.K_p:
                    sim.paused = not sim.paused
                elif event.key == pygame.K_r:
                    sim.new_simulation(new_seed=False)
                    sim_ui.resize_window_to_fit_grid()
                    update_stats_button_position()
                    pending_restart = False
                elif event.key == pygame.K_n:
                    sim.new_simulation(new_seed=True)
                    sim_ui.resize_window_to_fit_grid()
                    update_stats_button_position()
                    pending_restart = False

                # Parameter editing only in simulator view
                if current_screen == SCREEN_SIMULATOR:
                    done, _changed, needs_restart = sim_ui.handle_param_text_input(event)
                    if done and needs_restart:
                        pending_restart = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check stats toggle button (works in both views)
                    if btn_stats.is_clicked(mouse_pos, True):
                        current_screen = SCREEN_STATS if current_screen == SCREEN_SIMULATOR else SCREEN_SIMULATOR
                        btn_stats.text = "Grid" if current_screen == SCREEN_STATS else "Stats"
                        continue

                    # Simulator-specific button handling
                    if current_screen == SCREEN_SIMULATOR:
                        # Check for double-click on parameters first
                        click_time = pygame.time.get_ticks()
                        if hasattr(sim_ui, '_last_click_time') and hasattr(sim_ui, '_last_click_pos'):
                            time_diff = click_time - sim_ui._last_click_time
                            pos_diff = ((mouse_pos[0] - sim_ui._last_click_pos[0])**2 +
                                      (mouse_pos[1] - sim_ui._last_click_pos[1])**2)**0.5
                            if time_diff < 400 and pos_diff < 10:  # Double-click detected
                                sim_ui.handle_param_double_click(mouse_pos)
                                sim_ui._last_click_time = 0  # Reset to prevent triple-click
                                continue
                        sim_ui._last_click_time = click_time
                        sim_ui._last_click_pos = mouse_pos

                        # Check main buttons
                        if sim_ui.btn_step.is_clicked(mouse_pos, True):
                            sim.step()
                        elif sim_ui.btn_play.is_clicked(mouse_pos, True):
                            sim.paused = not sim.paused
                        elif sim_ui.btn_restart_same.is_clicked(mouse_pos, True):
                            sim.new_simulation(new_seed=False)
                            sim_ui.resize_window_to_fit_grid()
                            update_stats_button_position()
                            pending_restart = False
                        elif sim_ui.btn_new_seed.is_clicked(mouse_pos, True):
                            sim.new_simulation(new_seed=True)
                            sim_ui.resize_window_to_fit_grid()
                            update_stats_button_position()
                            pending_restart = False
                        elif sim_ui.btn_reset.is_clicked(mouse_pos, True):
                            sim_ui.reset_params_to_defaults()
                            pending_restart = True  # Params changed, need restart
                        else:
                            # Check parameter controls
                            changed, needs_restart = sim_ui.handle_param_click(mouse_pos)
                            if needs_restart:
                                pending_restart = True

        # Update hover states
        btn_stats.update(mouse_pos)
        if current_screen == SCREEN_SIMULATOR:
            sim_ui.update_controls(mouse_pos)

        # Auto-step when not paused
        if not sim.paused and current_time - sim.last_auto_step >= sim.auto_step_delay:
            sim.step()
            sim.last_auto_step = current_time

        # Draw current screen
        if current_screen == SCREEN_SIMULATOR:
            sim_ui.draw()

            # Draw restart pending indicator if needed
            if pending_restart:
                indicator_text = sim_ui.theme.font_small.render(
                    "Parameters changed - press R or N to apply",
                    True, (220, 180, 80)
                )
                sim_ui.window.blit(indicator_text, (sim_ui.padding, sim_ui.window_height - sim_ui.bottom_panel_height + 40))

        else:  # Stats screen
            # Draw stats on same window
            sim_ui.window.fill(DEFAULT_THEME.BG_COLOR)
            stats_ui.draw(sim_ui.window, sim_ui.window_width, sim_ui.window_height, sim_ui.bottom_panel_height)

            # Draw bottom panel (simplified version for stats view)
            panel_y = sim_ui.window_height - sim_ui.bottom_panel_height
            pygame.draw.rect(sim_ui.window, DEFAULT_THEME.PANEL_COLOR, (0, panel_y, sim_ui.window_width, sim_ui.bottom_panel_height))
            pygame.draw.line(sim_ui.window, (60, 60, 65), (0, panel_y), (sim_ui.window_width, panel_y), 2)

            # Generation counter
            gen_text = DEFAULT_THEME.font_title.render(f"Generation: {sim.step_count}", True, DEFAULT_THEME.TEXT_COLOR)
            sim_ui.window.blit(gen_text, (sim_ui.padding, panel_y + 15))

            # Status indicator
            status = "PAUSED" if sim.paused else "RUNNING"
            status_color = (180, 180, 60) if sim.paused else (60, 180, 100)
            status_text = DEFAULT_THEME.font_medium.render(status, True, status_color)
            sim_ui.window.blit(status_text, (sim_ui.padding + 220, panel_y + 18))

            # Controls help for stats view
            controls_text = DEFAULT_THEME.font_small.render(
                "S: Toggle View | SPACE: Step | P: Play/Pause | R: Restart | ESC: Back",
                True, DEFAULT_THEME.TEXT_DIM_COLOR
            )
            sim_ui.window.blit(controls_text, (sim_ui.padding, panel_y + 95))

        # Draw stats toggle button (in both views)
        btn_stats.draw(sim_ui.window, DEFAULT_THEME.font_medium)

        pygame.display.flip()
        await asyncio.sleep(0)
        sim_ui.clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())

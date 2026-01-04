"""
Simulator UI - Main visualization screen for SIPD simulation.

Handles all rendering and UI interaction for the cellular automaton simulator.
"""

import pygame
from .theme import UITheme
from .components import Button, ParameterControl


class SimulatorUI:
    """UI for the main simulation screen"""

    def __init__(self, sim_state, theme):
        """Initialize the simulator UI

        Args:
            sim_state: SimulationState instance
            theme: UITheme instance
        """
        pygame.init()

        self.sim = sim_state
        self.theme = theme
        self.clock = pygame.time.Clock()

        # Layout parameters from theme
        self.cell_size = theme.CELL_SIZE
        self.sidebar_width = theme.SIDEBAR_WIDTH
        self.bottom_panel_height = theme.BOTTOM_PANEL_HEIGHT
        self.padding = theme.PADDING

        # Calculate initial window size
        self.update_window_size()

        # Create window
        self.window = pygame.display.set_mode(
            (self.window_width, self.window_height),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("Spatial Iterated Prisoner's Dilemma")

        # Create buttons and controls
        self.create_buttons()
        self.create_parameter_controls()

    def update_window_size(self):
        """Calculate window dimensions based on grid size"""
        grid_width = self.sim.grid_cols * self.cell_size
        grid_height = self.sim.grid_rows * self.cell_size

        self.window_width = grid_width + self.sidebar_width + self.padding * 3
        self.window_height = grid_height + self.bottom_panel_height + self.padding * 2

        # Minimum size
        self.window_width = max(self.window_width, 650)
        self.window_height = max(self.window_height, 550)

    def create_buttons(self):
        """Create UI buttons"""
        button_y = self.window_height - self.bottom_panel_height + 60
        button_width = 90
        button_height = 28
        button_spacing = 10
        start_x = self.padding

        self.btn_step = Button(
            start_x, button_y, button_width, button_height,
            "Step", (70, 130, 80), (90, 160, 100)
        )
        self.btn_play = Button(
            start_x + button_width + button_spacing, button_y, button_width, button_height,
            "Play", (70, 100, 140), (90, 120, 170)
        )
        self.btn_restart_same = Button(
            start_x + (button_width + button_spacing) * 2, button_y, button_width, button_height,
            "Restart", (140, 100, 70), (170, 120, 90)
        )
        self.btn_new_seed = Button(
            start_x + (button_width + button_spacing) * 3, button_y, button_width, button_height,
            "New Seed", (100, 70, 140), (130, 90, 170)
        )

        self.buttons = [self.btn_step, self.btn_play, self.btn_restart_same, self.btn_new_seed]

    def create_parameter_controls(self):
        """Create parameter adjustment controls"""
        sidebar_x = self.window_width - self.sidebar_width - self.padding
        control_width = self.sidebar_width - 35

        # These positions will be updated in draw_sidebar
        self.param_grid_rows = ParameterControl(
            sidebar_x + 15, 0, control_width,
            "Rows", self.sim.grid_rows, 10, 200, 10,
            "{:.0f}", requires_restart=True, is_integer=True
        )
        self.param_grid_cols = ParameterControl(
            sidebar_x + 15, 0, control_width,
            "Cols", self.sim.grid_cols, 10, 200, 10,
            "{:.0f}", requires_restart=True, is_integer=True
        )
        self.param_rounds = ParameterControl(
            sidebar_x + 15, 0, control_width,
            "Rounds", self.sim.rounds, 10, 10000, 100,
            "{:.0f}", requires_restart=True, is_integer=True
        )
        self.param_noise = ParameterControl(
            sidebar_x + 15, 0, control_width,
            "Noise", self.sim.noise * 100, 0, 50, 0.1,
            "{:.1f}%", requires_restart=True, is_integer=False
        )
        self.param_mutation = ParameterControl(
            sidebar_x + 15, 0, control_width,
            "Mutation", self.sim.mutation_rate * 100, 0, 50, 0.1,
            "{:.1f}%", requires_restart=False, is_integer=False
        )
        self.param_speed = ParameterControl(
            sidebar_x + 15, 0, control_width,
            "Speed", 1000 / self.sim.auto_step_delay if self.sim.auto_step_delay > 0 else 10, 1, 50, 1,
            "{:.0f}/s", requires_restart=False, is_integer=True
        )

        self.param_controls = [
            self.param_grid_rows, self.param_grid_cols, self.param_rounds,
            self.param_noise, self.param_mutation, self.param_speed
        ]

        # Create reset button in bottom panel
        button_y = self.window_height - self.bottom_panel_height + 60
        button_width = 90
        self.btn_reset = Button(
            self.window_width - button_width - self.padding, button_y,
            button_width, 28,
            "Reset", (100, 80, 60), (130, 100, 80)
        )

    def resize_window_to_fit_grid(self):
        """Resize window to fit the current grid size"""
        self.update_window_size()
        self.window = pygame.display.set_mode(
            (self.window_width, self.window_height),
            pygame.RESIZABLE
        )
        self.create_buttons()
        self.create_parameter_controls()

    def handle_resize(self, new_width, new_height):
        """Handle window resize event"""
        self.window_width = max(new_width, 650)
        self.window_height = max(new_height, 550)

        # Recalculate cell size to fit grid in available space
        # Use actual board dimensions, not parameter values
        available_width = self.window_width - self.sidebar_width - self.padding * 3
        available_height = self.window_height - self.bottom_panel_height - self.padding * 2

        self.cell_size = min(
            available_width // self.sim.board.cols,
            available_height // self.sim.board.rows
        )
        self.cell_size = max(2, self.cell_size)  # Minimum cell size

        # Recreate buttons with new positions
        self.create_buttons()
        self.create_parameter_controls()

    def sync_params_to_sim(self):
        """Sync UI parameter values back to simulation"""
        self.sim.grid_rows = int(self.param_grid_rows.value)
        self.sim.grid_cols = int(self.param_grid_cols.value)
        self.sim.rounds = int(self.param_rounds.value)
        self.sim.noise = self.param_noise.value / 100.0
        self.sim.mutation_rate = self.param_mutation.value / 100.0
        self.sim.auto_step_delay = int(1000 / self.param_speed.value) if self.param_speed.value > 0 else 1000

    def handle_param_click(self, mouse_pos):
        """Handle clicks on parameter controls. Returns (changed, needs_restart)"""
        for ctrl in self.param_controls:
            changed, needs_restart = ctrl.handle_click(mouse_pos)
            if changed:
                self.sync_params_to_sim()

                if not needs_restart:
                    # Live update for mutation rate and speed
                    self.sim.update_live_params()

                return changed, needs_restart
        return False, False

    def handle_param_double_click(self, mouse_pos):
        """Handle double-click to start editing a parameter"""
        for ctrl in self.param_controls:
            if ctrl.handle_double_click(mouse_pos):
                return True
        return False

    def handle_param_text_input(self, event):
        """Handle text input for parameter editing. Returns (done, changed, needs_restart)"""
        for ctrl in self.param_controls:
            if ctrl.editing:
                done, changed, needs_restart = ctrl.handle_text_input(event)
                if done and changed:
                    self.sync_params_to_sim()
                    if not needs_restart:
                        self.sim.update_live_params()
                return done, changed, needs_restart
        return False, False, False

    def reset_params_to_defaults(self):
        """Reset all parameters to default values"""
        # Import here to avoid circular dependency
        from main import SimulationState

        self.sim.reset_parameters()

        # Update UI controls to match
        self.param_grid_rows.value = self.sim.grid_rows
        self.param_grid_cols.value = self.sim.grid_cols
        self.param_rounds.value = self.sim.rounds
        self.param_noise.value = self.sim.noise * 100
        self.param_mutation.value = self.sim.mutation_rate * 100
        self.param_speed.value = SimulationState.DEFAULT_SPEED

        self.sim.update_live_params()

    def _draw_grid(self):
        """Draw the simulation grid"""
        # Use the board's actual dimensions for drawing, not the parameter values
        # (parameters may have changed but not yet applied via restart)
        actual_rows = self.sim.board.rows
        actual_cols = self.sim.board.cols

        grid_width = actual_cols * self.cell_size
        grid_height = actual_rows * self.cell_size

        # Center grid in available space
        available_width = self.window_width - self.sidebar_width - self.padding * 3
        grid_x = self.padding + (available_width - grid_width) // 2
        grid_y = self.padding

        # Draw grid background
        pygame.draw.rect(
            self.window, (20, 20, 25),
            (grid_x - 2, grid_y - 2, grid_width + 4, grid_height + 4),
            border_radius=4
        )

        # Draw cells
        for i in range(actual_rows):
            for j in range(actual_cols):
                color = self.sim.colors[self.sim.board.strategy_name_at(i, j)]
                pygame.draw.rect(
                    self.window, color,
                    (grid_x + j * self.cell_size, grid_y + i * self.cell_size,
                     self.cell_size, self.cell_size)
                )

    def _draw_sidebar(self):
        """Draw the right sidebar with legend and parameters"""
        sidebar_x = self.window_width - self.sidebar_width - self.padding
        sidebar_y = self.padding
        sidebar_height = self.window_height - self.bottom_panel_height - self.padding

        # Sidebar background
        pygame.draw.rect(
            self.window, self.theme.PANEL_COLOR,
            (sidebar_x, sidebar_y, self.sidebar_width, sidebar_height),
            border_radius=8
        )

        # Title
        title = self.theme.font_title.render("Strategies", True, self.theme.TEXT_COLOR)
        self.window.blit(title, (sidebar_x + 15, sidebar_y + 12))

        # Strategy legend
        legend_y = sidebar_y + 45
        legend_item_height = 26
        square_size = 14

        for strategy_name, color in self.sim.colors.items():
            # Color square
            pygame.draw.rect(
                self.window, color,
                (sidebar_x + 15, legend_y, square_size, square_size),
                border_radius=3
            )

            # Strategy name
            text = self.theme.font_small.render(strategy_name, True, self.theme.TEXT_COLOR)
            self.window.blit(text, (sidebar_x + 36, legend_y + 1))

            legend_y += legend_item_height

        # Divider
        legend_y += 8
        pygame.draw.line(
            self.window, (80, 80, 85),
            (sidebar_x + 15, legend_y), (sidebar_x + self.sidebar_width - 15, legend_y)
        )

        # Parameters section title
        legend_y += 12
        params_title = self.theme.font_medium.render("Parameters", True, self.theme.TEXT_COLOR)
        self.window.blit(params_title, (sidebar_x + 15, legend_y))
        legend_y += 25

        # Seed display (not editable)
        seed_text = self.theme.font_small.render(f"Seed: {self.sim.seed % 100000:05d}", True, self.theme.TEXT_DIM_COLOR)
        self.window.blit(seed_text, (sidebar_x + 15, legend_y))
        legend_y += 22

        # Update parameter control positions and draw them
        control_spacing = 24
        for ctrl in self.param_controls:
            ctrl.update_positions(sidebar_x + 15, legend_y)
            ctrl.draw(self.window, self.theme.font_small, self.theme.font_tiny)
            legend_y += control_spacing

        # Note about restart
        legend_y += 8
        note = self.theme.font_tiny.render("* requires restart", True, (140, 120, 80))
        self.window.blit(note, (sidebar_x + 15, legend_y))

    def _draw_bottom_panel(self):
        """Draw the bottom control panel"""
        panel_y = self.window_height - self.bottom_panel_height

        # Panel background
        pygame.draw.rect(
            self.window, self.theme.PANEL_COLOR,
            (0, panel_y, self.window_width, self.bottom_panel_height)
        )

        # Top border
        pygame.draw.line(
            self.window, (60, 60, 65),
            (0, panel_y), (self.window_width, panel_y), 2
        )

        # Generation counter (prominent)
        gen_text = self.theme.font_title.render(f"Generation: {self.sim.step_count}", True, self.theme.TEXT_COLOR)
        self.window.blit(gen_text, (self.padding, panel_y + 15))

        # Status indicator
        status = "PAUSED" if self.sim.paused else "RUNNING"
        status_color = (180, 180, 60) if self.sim.paused else (60, 180, 100)
        status_text = self.theme.font_medium.render(status, True, status_color)
        self.window.blit(status_text, (self.padding + 220, panel_y + 18))

        # Controls help
        controls_text = self.theme.font_small.render(
            "SPACE: Step | P: Play/Pause | R: Restart | N: New Seed | Double-click values to edit",
            True, self.theme.TEXT_DIM_COLOR
        )
        self.window.blit(controls_text, (self.padding, panel_y + 95))

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)
            button.draw(self.window, self.theme.font_medium)

        # Draw reset button
        self.btn_reset.update(mouse_pos)
        self.btn_reset.draw(self.window, self.theme.font_medium)

        # Update play button text based on state
        self.btn_play.text = "Pause" if not self.sim.paused else "Play"

    def draw(self):
        """Draw the complete UI"""
        self.window.fill(self.theme.BG_COLOR)
        self._draw_grid()
        self._draw_sidebar()
        self._draw_bottom_panel()
        pygame.display.flip()

    def update_controls(self, mouse_pos):
        """Update hover states for all interactive elements"""
        for button in self.buttons:
            button.update(mouse_pos)
        for ctrl in self.param_controls:
            ctrl.update(mouse_pos)

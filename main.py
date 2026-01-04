import asyncio
import pygame
import sys
import random
from strategies import always_defect, always_cooperate, tit_for_tat, pavlov, revenger, prisoners_dilemma, tf2t
from grid import Grid


class Button:
    """Simple clickable button for pygame"""
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def draw(self, surface, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=4)
        pygame.draw.rect(surface, (60, 60, 60), self.rect, 1, border_radius=4)

        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed


class ParameterControl:
    """A parameter with +/- buttons and text input support"""
    def __init__(self, x, y, width, label, value, min_val, max_val, step, format_str="{}", requires_restart=False, is_integer=False):
        self.x = x
        self.y = y
        self.width = width
        self.label = label
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.format_str = format_str
        self.requires_restart = requires_restart
        self.is_integer = is_integer

        # Text input state
        self.editing = False
        self.text_input = ""

        # Button dimensions
        btn_size = 18
        btn_margin = 5

        # Position buttons at the right side
        self.btn_minus = pygame.Rect(x + width - btn_size * 2 - btn_margin, y, btn_size, btn_size)
        self.btn_plus = pygame.Rect(x + width - btn_size, y, btn_size, btn_size)

        # Value display area (for double-click to edit)
        self.value_rect = pygame.Rect(x + 70, y, width - 115, 20)

        self.minus_hovered = False
        self.plus_hovered = False
        self.value_hovered = False

    def update_positions(self, x, y):
        """Update control position"""
        self.x = x
        self.y = y
        btn_size = 18
        btn_margin = 5
        self.btn_minus = pygame.Rect(x + self.width - btn_size * 2 - btn_margin, y, btn_size, btn_size)
        self.btn_plus = pygame.Rect(x + self.width - btn_size, y, btn_size, btn_size)
        self.value_rect = pygame.Rect(x + 70, y, self.width - 115, 20)

    def draw(self, surface, font_label, font_btn):
        # Draw label
        label_text = font_label.render(f"{self.label}:", True, (180, 180, 180))
        surface.blit(label_text, (self.x, self.y + 2))

        # Draw value (either as text input or display)
        if self.editing:
            # Draw input box
            pygame.draw.rect(surface, (70, 70, 80), self.value_rect, border_radius=3)
            pygame.draw.rect(surface, (100, 150, 200), self.value_rect, 2, border_radius=3)

            # Draw cursor and text
            input_text = font_label.render(self.text_input + "|", True, (220, 220, 220))
            surface.blit(input_text, (self.value_rect.x + 4, self.value_rect.y + 2))
        else:
            # Draw value display with hover effect
            if self.value_hovered:
                pygame.draw.rect(surface, (55, 55, 60), self.value_rect, border_radius=3)

            display_val = self.format_str.format(self.value)
            value_text = font_label.render(display_val, True, (200, 200, 200) if self.value_hovered else (180, 180, 180))
            surface.blit(value_text, (self.value_rect.x + 4, self.value_rect.y + 2))

        # Draw minus button
        minus_color = (80, 80, 90) if self.minus_hovered else (60, 60, 70)
        pygame.draw.rect(surface, minus_color, self.btn_minus, border_radius=3)
        minus_text = font_btn.render("-", True, (200, 200, 200))
        minus_rect = minus_text.get_rect(center=self.btn_minus.center)
        surface.blit(minus_text, minus_rect)

        # Draw plus button
        plus_color = (80, 80, 90) if self.plus_hovered else (60, 60, 70)
        pygame.draw.rect(surface, plus_color, self.btn_plus, border_radius=3)
        plus_text = font_btn.render("+", True, (200, 200, 200))
        plus_rect = plus_text.get_rect(center=self.btn_plus.center)
        surface.blit(plus_text, plus_rect)

        # Restart indicator
        if self.requires_restart:
            indicator = font_btn.render("*", True, (180, 140, 60))
            surface.blit(indicator, (self.x + self.width + 3, self.y))

    def update(self, mouse_pos):
        self.minus_hovered = self.btn_minus.collidepoint(mouse_pos)
        self.plus_hovered = self.btn_plus.collidepoint(mouse_pos)
        self.value_hovered = self.value_rect.collidepoint(mouse_pos)

    def start_editing(self):
        """Start text input mode"""
        self.editing = True
        # Initialize with current value (without formatting)
        if self.is_integer:
            self.text_input = str(int(self.value))
        else:
            self.text_input = str(self.value)

    def handle_text_input(self, event):
        """Handle keyboard input for text editing. Returns (done, changed, needs_restart)"""
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            # Finish editing and apply value
            try:
                new_val = float(self.text_input)
                if self.is_integer:
                    new_val = int(new_val)

                # Clamp to valid range
                new_val = max(self.min_val, min(self.max_val, new_val))

                if new_val != self.value:
                    self.value = new_val
                    self.editing = False
                    return True, True, self.requires_restart
                else:
                    self.editing = False
                    return True, False, False
            except ValueError:
                # Invalid input, cancel
                self.editing = False
                return True, False, False

        elif event.key == pygame.K_ESCAPE:
            # Cancel editing
            self.editing = False
            return True, False, False

        elif event.key == pygame.K_BACKSPACE:
            self.text_input = self.text_input[:-1]
            return False, False, False

        elif event.unicode.isprintable() and (event.unicode.isdigit() or event.unicode in '.-'):
            # Only allow digits, decimal point, and minus sign
            self.text_input += event.unicode
            return False, False, False

        return False, False, False

    def handle_click(self, mouse_pos):
        """Returns True if value changed, and whether it requires restart"""
        if self.btn_minus.collidepoint(mouse_pos):
            new_val = self.value - self.step
            if new_val >= self.min_val:
                self.value = round(new_val, 4)  # Avoid float precision issues
                return True, self.requires_restart
        elif self.btn_plus.collidepoint(mouse_pos):
            new_val = self.value + self.step
            if new_val <= self.max_val:
                self.value = round(new_val, 4)
                return True, self.requires_restart
        return False, False

    def handle_double_click(self, mouse_pos):
        """Handle double-click on value to start editing"""
        if self.value_rect.collidepoint(mouse_pos):
            self.start_editing()
            return True
        return False


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


class GameUI:
    """Handles all UI rendering and interaction"""

    # Color scheme
    BG_COLOR = (30, 30, 35)
    PANEL_COLOR = (45, 45, 50)
    TEXT_COLOR = (220, 220, 220)
    TEXT_DIM_COLOR = (140, 140, 140)
    ACCENT_COLOR = (52, 152, 219)

    def __init__(self, sim_state):
        pygame.init()
        pygame.font.init()

        self.sim = sim_state
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_title = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 26)
        self.font_medium = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        self.font_tiny = pygame.font.Font(None, 16)

        # Layout parameters
        self.cell_size = 8
        self.sidebar_width = 220
        self.bottom_panel_height = 120
        self.padding = 15

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
        self.sim.reset_parameters()

        # Update UI controls to match
        self.param_grid_rows.value = self.sim.grid_rows
        self.param_grid_cols.value = self.sim.grid_cols
        self.param_rounds.value = self.sim.rounds
        self.param_noise.value = self.sim.noise * 100
        self.param_mutation.value = self.sim.mutation_rate * 100
        self.param_speed.value = SimulationState.DEFAULT_SPEED

        self.sim.update_live_params()

    def draw_grid(self):
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

    def draw_sidebar(self):
        """Draw the right sidebar with legend and parameters"""
        sidebar_x = self.window_width - self.sidebar_width - self.padding
        sidebar_y = self.padding
        sidebar_height = self.window_height - self.bottom_panel_height - self.padding

        # Sidebar background
        pygame.draw.rect(
            self.window, self.PANEL_COLOR,
            (sidebar_x, sidebar_y, self.sidebar_width, sidebar_height),
            border_radius=8
        )

        # Title
        title = self.font_title.render("Strategies", True, self.TEXT_COLOR)
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
            text = self.font_small.render(strategy_name, True, self.TEXT_COLOR)
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
        params_title = self.font_medium.render("Parameters", True, self.TEXT_COLOR)
        self.window.blit(params_title, (sidebar_x + 15, legend_y))
        legend_y += 25

        # Seed display (not editable)
        seed_text = self.font_small.render(f"Seed: {self.sim.seed % 100000:05d}", True, self.TEXT_DIM_COLOR)
        self.window.blit(seed_text, (sidebar_x + 15, legend_y))
        legend_y += 22

        # Update parameter control positions and draw them
        control_spacing = 24
        for ctrl in self.param_controls:
            ctrl.update_positions(sidebar_x + 15, legend_y)
            ctrl.draw(self.window, self.font_small, self.font_tiny)
            legend_y += control_spacing

        # Note about restart
        legend_y += 8
        note = self.font_tiny.render("* requires restart", True, (140, 120, 80))
        self.window.blit(note, (sidebar_x + 15, legend_y))

    def draw_bottom_panel(self):
        """Draw the bottom control panel"""
        panel_y = self.window_height - self.bottom_panel_height

        # Panel background
        pygame.draw.rect(
            self.window, self.PANEL_COLOR,
            (0, panel_y, self.window_width, self.bottom_panel_height)
        )

        # Top border
        pygame.draw.line(
            self.window, (60, 60, 65),
            (0, panel_y), (self.window_width, panel_y), 2
        )

        # Generation counter (prominent)
        gen_text = self.font_title.render(f"Generation: {self.sim.step_count}", True, self.TEXT_COLOR)
        self.window.blit(gen_text, (self.padding, panel_y + 15))

        # Status indicator
        status = "PAUSED" if self.sim.paused else "RUNNING"
        status_color = (180, 180, 60) if self.sim.paused else (60, 180, 100)
        status_text = self.font_medium.render(status, True, status_color)
        self.window.blit(status_text, (self.padding + 220, panel_y + 18))

        # Controls help
        controls_text = self.font_small.render(
            "SPACE: Step | P: Play/Pause | R: Restart | N: New Seed | Double-click values to edit",
            True, self.TEXT_DIM_COLOR
        )
        self.window.blit(controls_text, (self.padding, panel_y + 95))

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)
            button.draw(self.window, self.font_medium)

        # Draw reset button
        self.btn_reset.update(mouse_pos)
        self.btn_reset.draw(self.window, self.font_medium)

        # Update play button text based on state
        self.btn_play.text = "Pause" if not self.sim.paused else "Play"

    def draw(self):
        """Draw the complete UI"""
        self.window.fill(self.BG_COLOR)
        self.draw_grid()
        self.draw_sidebar()
        self.draw_bottom_panel()
        pygame.display.flip()

    def update_controls(self, mouse_pos):
        """Update hover states for all interactive elements"""
        for button in self.buttons:
            button.update(mouse_pos)
        for ctrl in self.param_controls:
            ctrl.update(mouse_pos)


async def main():
    sim = SimulationState()
    ui = GameUI(sim)

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
            indicator_text = ui.font_small.render(
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

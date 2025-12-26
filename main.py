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


class SimulationState:
    """Manages the simulation state and parameters"""
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
        self.grid_rows = 50
        self.grid_cols = 50
        self.rounds = 1000
        self.noise = 0.0
        self.mutation_rate = 0.0

        # State tracking
        self.seed = None
        self.step_count = 0
        self.board = None
        self.paused = True  # Start paused
        self.auto_step_delay = 100  # ms between auto-steps
        self.last_auto_step = 0

        self.new_simulation(new_seed=True)

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

        # Create buttons
        self.create_buttons()

    def update_window_size(self):
        """Calculate window dimensions based on grid size"""
        grid_width = self.sim.grid_cols * self.cell_size
        grid_height = self.sim.grid_rows * self.cell_size

        self.window_width = grid_width + self.sidebar_width + self.padding * 3
        self.window_height = grid_height + self.bottom_panel_height + self.padding * 2

        # Minimum size
        self.window_width = max(self.window_width, 650)
        self.window_height = max(self.window_height, 500)

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

    def handle_resize(self, new_width, new_height):
        """Handle window resize event"""
        self.window_width = max(new_width, 650)
        self.window_height = max(new_height, 500)

        # Recalculate cell size to fit grid in available space
        available_width = self.window_width - self.sidebar_width - self.padding * 3
        available_height = self.window_height - self.bottom_panel_height - self.padding * 2

        self.cell_size = min(
            available_width // self.sim.grid_cols,
            available_height // self.sim.grid_rows
        )
        self.cell_size = max(2, self.cell_size)  # Minimum cell size

        # Recreate buttons with new positions
        self.create_buttons()

    def draw_grid(self):
        """Draw the simulation grid"""
        grid_width = self.sim.grid_cols * self.cell_size
        grid_height = self.sim.grid_rows * self.cell_size

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
        for i in range(self.sim.grid_rows):
            for j in range(self.sim.grid_cols):
                color = self.sim.colors[self.sim.board.strategy_name_at(i, j)]
                pygame.draw.rect(
                    self.window, color,
                    (grid_x + j * self.cell_size, grid_y + i * self.cell_size,
                     self.cell_size, self.cell_size)
                )

    def draw_sidebar(self):
        """Draw the right sidebar with legend and info"""
        sidebar_x = self.window_width - self.sidebar_width - self.padding
        sidebar_y = self.padding

        # Sidebar background
        pygame.draw.rect(
            self.window, self.PANEL_COLOR,
            (sidebar_x, sidebar_y, self.sidebar_width, self.window_height - self.bottom_panel_height - self.padding),
            border_radius=8
        )

        # Title
        title = self.font_title.render("Strategies", True, self.TEXT_COLOR)
        self.window.blit(title, (sidebar_x + 15, sidebar_y + 15))

        # Strategy legend
        legend_y = sidebar_y + 55
        legend_item_height = 32
        square_size = 16

        for strategy_name, color in self.sim.colors.items():
            # Color square
            pygame.draw.rect(
                self.window, color,
                (sidebar_x + 15, legend_y, square_size, square_size),
                border_radius=3
            )

            # Strategy name
            text = self.font_medium.render(strategy_name, True, self.TEXT_COLOR)
            self.window.blit(text, (sidebar_x + 40, legend_y))

            legend_y += legend_item_height

        # Divider
        legend_y += 10
        pygame.draw.line(
            self.window, (80, 80, 85),
            (sidebar_x + 15, legend_y), (sidebar_x + self.sidebar_width - 15, legend_y)
        )

        # Simulation info
        info_y = legend_y + 15
        info_items = [
            f"Seed: {self.sim.seed % 100000:05d}",  # Show last 5 digits
            f"Grid: {self.sim.grid_rows}×{self.sim.grid_cols}",
            f"Rounds: {self.sim.rounds}",
            f"Noise: {self.sim.noise*100:.1f}%",
            f"Mutation: {self.sim.mutation_rate*100:.1f}%"
        ]

        for item in info_items:
            text = self.font_small.render(item, True, self.TEXT_DIM_COLOR)
            self.window.blit(text, (sidebar_x + 15, info_y))
            info_y += 20

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
            "SPACE: Step | P: Play/Pause | R: Restart | N: New Seed | ESC: Quit",
            True, self.TEXT_DIM_COLOR
        )
        self.window.blit(controls_text, (self.padding, panel_y + 95))

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)
            button.draw(self.window, self.font_medium)

        # Update play button text based on state
        self.btn_play.text = "Pause" if not self.sim.paused else "Play"

    def draw(self):
        """Draw the complete UI"""
        self.window.fill(self.BG_COLOR)
        self.draw_grid()
        self.draw_sidebar()
        self.draw_bottom_panel()
        pygame.display.flip()


async def main():
    sim = SimulationState()
    ui = GameUI(sim)

    running = True
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
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    sim.step()
                elif event.key == pygame.K_p:
                    sim.paused = not sim.paused
                elif event.key == pygame.K_r:
                    sim.new_simulation(new_seed=False)
                elif event.key == pygame.K_n:
                    sim.new_simulation(new_seed=True)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if ui.btn_step.is_clicked(mouse_pos, True):
                        sim.step()
                    elif ui.btn_play.is_clicked(mouse_pos, True):
                        sim.paused = not sim.paused
                    elif ui.btn_restart_same.is_clicked(mouse_pos, True):
                        sim.new_simulation(new_seed=False)
                    elif ui.btn_new_seed.is_clicked(mouse_pos, True):
                        sim.new_simulation(new_seed=True)

        # Auto-step when not paused
        if not sim.paused and current_time - sim.last_auto_step >= sim.auto_step_delay:
            sim.step()
            sim.last_auto_step = current_time

        ui.draw()
        await asyncio.sleep(0)
        ui.clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())

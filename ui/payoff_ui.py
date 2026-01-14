"""
Payoff UI - Payoff matrix editor for SIPD.

Allows users to customize the game's payoff matrix.
"""

import pygame
from .theme import UITheme
from .components import Button


class PayoffCell:
    """A single cell in the payoff matrix with two editable values"""

    def __init__(self, x, y, width, height, p1_value, p2_value):
        self.rect = pygame.Rect(x, y, width, height)
        self.p1_value = p1_value  # Player 1's payoff
        self.p2_value = p2_value  # Player 2's payoff

        # Button dimensions
        btn_size = 20
        btn_margin = 4

        # Layout: [P1-] [P1 value] [P1+]  ,  [P2-] [P2 value] [P2+]
        # We'll position these in update_position

        self.p1_minus_rect = pygame.Rect(0, 0, btn_size, btn_size)
        self.p1_plus_rect = pygame.Rect(0, 0, btn_size, btn_size)
        self.p2_minus_rect = pygame.Rect(0, 0, btn_size, btn_size)
        self.p2_plus_rect = pygame.Rect(0, 0, btn_size, btn_size)

        self.hovered_btn = None  # Track which button is hovered

    def update_position(self, x, y, width, height):
        """Update cell position and recalculate button positions"""
        self.rect = pygame.Rect(x, y, width, height)

        btn_size = 20
        center_y = y + height // 2

        # P1 controls on left side of cell
        p1_center_x = x + width // 4
        self.p1_minus_rect = pygame.Rect(p1_center_x - 35, center_y - btn_size // 2, btn_size, btn_size)
        self.p1_plus_rect = pygame.Rect(p1_center_x + 15, center_y - btn_size // 2, btn_size, btn_size)

        # P2 controls on right side of cell
        p2_center_x = x + 3 * width // 4
        self.p2_minus_rect = pygame.Rect(p2_center_x - 35, center_y - btn_size // 2, btn_size, btn_size)
        self.p2_plus_rect = pygame.Rect(p2_center_x + 15, center_y - btn_size // 2, btn_size, btn_size)

    def update(self, mouse_pos):
        """Update hover state"""
        self.hovered_btn = None
        if self.p1_minus_rect.collidepoint(mouse_pos):
            self.hovered_btn = 'p1_minus'
        elif self.p1_plus_rect.collidepoint(mouse_pos):
            self.hovered_btn = 'p1_plus'
        elif self.p2_minus_rect.collidepoint(mouse_pos):
            self.hovered_btn = 'p2_minus'
        elif self.p2_plus_rect.collidepoint(mouse_pos):
            self.hovered_btn = 'p2_plus'

    def handle_click(self, mouse_pos):
        """Handle mouse click. Returns True if a value changed."""
        if self.p1_minus_rect.collidepoint(mouse_pos):
            self.p1_value = max(0, self.p1_value - 1)
            return True
        elif self.p1_plus_rect.collidepoint(mouse_pos):
            self.p1_value = min(99, self.p1_value + 1)
            return True
        elif self.p2_minus_rect.collidepoint(mouse_pos):
            self.p2_value = max(0, self.p2_value - 1)
            return True
        elif self.p2_plus_rect.collidepoint(mouse_pos):
            self.p2_value = min(99, self.p2_value + 1)
            return True
        return False

    def draw(self, window, font, font_small):
        """Draw the cell with its values and controls"""
        # Cell background
        pygame.draw.rect(window, (50, 50, 55), self.rect, border_radius=4)
        pygame.draw.rect(window, (70, 70, 75), self.rect, 1, border_radius=4)

        btn_color = (70, 70, 80)
        btn_hover_color = (90, 90, 100)
        text_color = (200, 200, 200)

        # P1 section
        p1_center_x = self.rect.x + self.rect.width // 4

        # P1 minus button
        color = btn_hover_color if self.hovered_btn == 'p1_minus' else btn_color
        pygame.draw.rect(window, color, self.p1_minus_rect, border_radius=3)
        minus_text = font_small.render("-", True, text_color)
        window.blit(minus_text, (self.p1_minus_rect.centerx - minus_text.get_width() // 2,
                                  self.p1_minus_rect.centery - minus_text.get_height() // 2))

        # P1 value
        p1_text = font.render(str(self.p1_value), True, (100, 180, 100))
        window.blit(p1_text, (p1_center_x - p1_text.get_width() // 2,
                              self.rect.centery - p1_text.get_height() // 2))

        # P1 plus button
        color = btn_hover_color if self.hovered_btn == 'p1_plus' else btn_color
        pygame.draw.rect(window, color, self.p1_plus_rect, border_radius=3)
        plus_text = font_small.render("+", True, text_color)
        window.blit(plus_text, (self.p1_plus_rect.centerx - plus_text.get_width() // 2,
                                 self.p1_plus_rect.centery - plus_text.get_height() // 2))

        # Comma separator
        comma_text = font.render(",", True, (150, 150, 150))
        window.blit(comma_text, (self.rect.centerx - comma_text.get_width() // 2,
                                  self.rect.centery - comma_text.get_height() // 2))

        # P2 section
        p2_center_x = self.rect.x + 3 * self.rect.width // 4

        # P2 minus button
        color = btn_hover_color if self.hovered_btn == 'p2_minus' else btn_color
        pygame.draw.rect(window, color, self.p2_minus_rect, border_radius=3)
        window.blit(minus_text, (self.p2_minus_rect.centerx - minus_text.get_width() // 2,
                                  self.p2_minus_rect.centery - minus_text.get_height() // 2))

        # P2 value
        p2_text = font.render(str(self.p2_value), True, (180, 100, 100))
        window.blit(p2_text, (p2_center_x - p2_text.get_width() // 2,
                              self.rect.centery - p2_text.get_height() // 2))

        # P2 plus button
        color = btn_hover_color if self.hovered_btn == 'p2_plus' else btn_color
        pygame.draw.rect(window, color, self.p2_plus_rect, border_radius=3)
        window.blit(plus_text, (self.p2_plus_rect.centerx - plus_text.get_width() // 2,
                                 self.p2_plus_rect.centery - plus_text.get_height() // 2))


class PayoffUI:
    """UI for editing the payoff matrix"""

    # Layout constants
    CELL_WIDTH = 160
    CELL_HEIGHT = 60
    HEADER_SIZE = 100  # Space for row/column headers
    PANEL_PADDING = 15

    def __init__(self, sim_state, theme):
        """Initialize the payoff UI

        Args:
            sim_state: SimulationState instance
            theme: UITheme instance
        """
        self.sim = sim_state
        self.theme = theme
        self.padding = theme.PADDING

        # Create cells for 2x2 matrix
        self.cells = [[None, None], [None, None]]
        self._create_cells()

        # Reset button
        self.btn_reset = Button(0, 0, 140, 28, "Reset to Default", (80, 80, 90), (100, 100, 110))

    def _create_cells(self):
        """Create PayoffCell objects from simulation state"""
        matrix = self.sim.payoff_matrix
        for row in range(2):
            for col in range(2):
                p1, p2 = matrix[row][col]
                self.cells[row][col] = PayoffCell(0, 0, self.CELL_WIDTH, self.CELL_HEIGHT, p1, p2)

    def _sync_from_sim(self):
        """Sync cell values from simulation state"""
        matrix = self.sim.payoff_matrix
        for row in range(2):
            for col in range(2):
                p1, p2 = matrix[row][col]
                self.cells[row][col].p1_value = p1
                self.cells[row][col].p2_value = p2

    def _sync_to_sim(self):
        """Sync cell values back to simulation state"""
        for row in range(2):
            for col in range(2):
                cell = self.cells[row][col]
                self.sim.payoff_matrix[row][col] = (cell.p1_value, cell.p2_value)

    def update(self, mouse_pos):
        """Update hover states"""
        for row in range(2):
            for col in range(2):
                self.cells[row][col].update(mouse_pos)
        self.btn_reset.update(mouse_pos)

    def handle_mouse_down(self, mouse_pos):
        """Handle mouse down events. Returns True if event was handled."""
        # Check reset button
        if self.btn_reset.is_clicked(mouse_pos, True):
            self.sim.reset_payoff_matrix()
            self._sync_from_sim()
            return True

        # Check cells
        for row in range(2):
            for col in range(2):
                if self.cells[row][col].handle_click(mouse_pos):
                    self._sync_to_sim()
                    return True

        return False

    def draw(self, window, window_width, window_height, bottom_panel_height):
        """Draw the payoff matrix editor

        Args:
            window: pygame surface to draw on
            window_width: current window width
            window_height: current window height
            bottom_panel_height: height of bottom panel (to avoid)
        """
        self._sync_from_sim()

        # Calculate content dimensions
        grid_width = 2 * self.CELL_WIDTH
        grid_height = 2 * self.CELL_HEIGHT
        panel_width = self.HEADER_SIZE + grid_width + self.PANEL_PADDING * 2
        panel_height = self.HEADER_SIZE + grid_height + self.PANEL_PADDING * 2 + 50  # Extra for button

        # Help text dimensions
        help_text_width = 220
        help_text_margin = 30

        # Check if there's room for help text
        total_content_width = panel_width
        show_help = False
        if panel_width + help_text_margin + help_text_width + self.padding * 2 < window_width:
            total_content_width = panel_width + help_text_margin + help_text_width
            show_help = True

        # Center the content horizontally
        content_left = (window_width - total_content_width) // 2
        content_left = max(self.padding, content_left)

        panel_left = content_left
        panel_top = 75

        # Draw title
        title = self.theme.font_title.render("Payoff Matrix", True, self.theme.TEXT_COLOR)
        window.blit(title, (panel_left, self.padding))

        # Subtitle
        subtitle = self.theme.font_small.render(
            "Configure payoffs for each outcome (Player 1, Player 2)",
            True, self.theme.TEXT_DIM_COLOR
        )
        window.blit(subtitle, (panel_left, self.padding + 35))

        # Background panel
        panel_rect = pygame.Rect(
            panel_left - 5, panel_top,
            panel_width, panel_height
        )
        pygame.draw.rect(window, self.theme.PANEL_COLOR, panel_rect, border_radius=8)

        # Grid origin (after headers)
        grid_left = panel_left + self.HEADER_SIZE
        grid_top = panel_top + self.HEADER_SIZE

        # Draw column headers
        col_labels = ["Defect", "Cooperate"]
        for col, label in enumerate(col_labels):
            text = self.theme.font_small.render(label, True, self.theme.TEXT_COLOR)
            x = grid_left + col * self.CELL_WIDTH + self.CELL_WIDTH // 2 - text.get_width() // 2
            y = panel_top + self.HEADER_SIZE - 30
            window.blit(text, (x, y))

        # Column header label
        p2_label = self.theme.font_tiny.render("Player 2", True, self.theme.TEXT_DIM_COLOR)
        window.blit(p2_label, (grid_left + grid_width // 2 - p2_label.get_width() // 2,
                               panel_top + 20))

        # Draw row headers
        row_labels = ["Defect", "Cooperate"]
        for row, label in enumerate(row_labels):
            text = self.theme.font_small.render(label, True, self.theme.TEXT_COLOR)
            x = panel_left + self.HEADER_SIZE - text.get_width() - 10
            y = grid_top + row * self.CELL_HEIGHT + self.CELL_HEIGHT // 2 - text.get_height() // 2
            window.blit(text, (x, y))

        # Row header label (rotated would be nice, but let's keep it simple)
        p1_label = self.theme.font_tiny.render("Player 1", True, self.theme.TEXT_DIM_COLOR)
        window.blit(p1_label, (panel_left + 10, grid_top + grid_height // 2 - p1_label.get_height() // 2))

        # Draw cells
        for row in range(2):
            for col in range(2):
                cell = self.cells[row][col]
                cell_x = grid_left + col * self.CELL_WIDTH
                cell_y = grid_top + row * self.CELL_HEIGHT
                cell.update_position(cell_x, cell_y, self.CELL_WIDTH, self.CELL_HEIGHT)
                cell.draw(window, self.theme.font_medium, self.theme.font_small)

        # Reset button
        self.btn_reset.rect.x = panel_left + 5
        self.btn_reset.rect.y = grid_top + grid_height + 15
        self.btn_reset.draw(window, self.theme.font_small)

        # Legend for colors
        legend_y = grid_top + grid_height + 50
        p1_legend = self.theme.font_tiny.render("Green = Player 1's payoff", True, (100, 180, 100))
        p2_legend = self.theme.font_tiny.render("Red = Player 2's payoff", True, (180, 100, 100))
        window.blit(p1_legend, (panel_left + 150, legend_y))
        window.blit(p2_legend, (panel_left + 150, legend_y + 18))

        # Help text
        if show_help:
            help_x = panel_left + panel_width + help_text_margin
            help_y = panel_top + 10
            help_lines = [
                "How the matrix works:",
                "",
                "Each cell shows what each",
                "player receives when they",
                "choose those moves.",
                "",
                "Default is Prisoner's Dilemma:",
                "  Mutual defect: (1, 1)",
                "  Mutual cooperate: (3, 3)",
                "  Temptation: 5, Sucker: 0",
                "",
                "Try other games:",
                "  Chicken: T > C > D > S",
                "  Stag Hunt: C > T > D > S",
                "",
                "Press R or N to apply",
                "changes to the simulation."
            ]

            for line in help_lines:
                text = self.theme.font_tiny.render(line, True, self.theme.TEXT_DIM_COLOR)
                window.blit(text, (help_x, help_y))
                help_y += 18

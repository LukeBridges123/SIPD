"""
Matchup UI - Strategy matchup table visualization for SIPD.

Shows how each strategy performs against every other strategy in a color-coded grid.
"""

import pygame
from .theme import UITheme


class MatchupUI:
    """UI for visualizing the strategy matchup table"""

    # Layout constants
    CELL_SIZE = 50  # Size of each cell in the grid
    MIN_CELL_SIZE = 35
    MAX_CELL_SIZE = 70
    HEADER_HEIGHT = 80  # Space for column headers (rotated text)
    LABEL_WIDTH = 120  # Space for row labels
    PANEL_PADDING = 15
    LEGEND_HEIGHT = 60

    def __init__(self, sim_state, theme):
        """Initialize the matchup UI

        Args:
            sim_state: SimulationState instance
            theme: UITheme instance
        """
        self.sim = sim_state
        self.theme = theme
        self.padding = theme.PADDING

        # Hover state
        self.hover_row = -1
        self.hover_col = -1

        # Cache for cell rects (populated during draw)
        self.cell_rects = []
        self.grid_origin = (0, 0)
        self.current_cell_size = self.CELL_SIZE

    def _get_num_strategies(self):
        """Get the number of strategies"""
        return len(self.sim.strategies)

    def _get_matchup_table(self):
        """Get the matchup table from the simulation's grid"""
        if self.sim.board is not None:
            return self.sim.board.matchups
        return None

    def _get_score_range(self, matchups):
        """Get min and max scores for color scaling"""
        if not matchups:
            return 0, 1

        all_scores = []
        for row in matchups:
            all_scores.extend(row)

        if not all_scores:
            return 0, 1

        return min(all_scores), max(all_scores)

    def _score_to_color(self, score, min_score, max_score):
        """Convert a score to a color on a green-grey-red gradient.

        Green = high score (good for the row strategy)
        Grey = median score
        Red = low score (bad for the row strategy)
        """
        if max_score == min_score:
            # All scores are the same
            return (128, 128, 128)

        # Normalize score to 0-1 range
        t = (score - min_score) / (max_score - min_score)

        # Color gradient: red (0) -> grey (0.5) -> green (1)
        if t < 0.5:
            # Red to grey
            t2 = t * 2  # 0 to 1
            r = int(200 - 72 * t2)  # 200 -> 128
            g = int(60 + 68 * t2)   # 60 -> 128
            b = int(60 + 68 * t2)   # 60 -> 128
        else:
            # Grey to green
            t2 = (t - 0.5) * 2  # 0 to 1
            r = int(128 - 82 * t2)  # 128 -> 46
            g = int(128 + 76 * t2)  # 128 -> 204
            b = int(128 - 15 * t2)  # 128 -> 113

        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    def _calculate_cell_size(self, available_width, available_height, num_strategies):
        """Calculate optimal cell size to fit the grid"""
        # Available space for the grid itself
        grid_width = available_width - self.LABEL_WIDTH - self.padding * 2
        grid_height = available_height - self.HEADER_HEIGHT - self.LEGEND_HEIGHT - self.padding * 2

        # Calculate cell size that fits
        cell_w = grid_width // num_strategies
        cell_h = grid_height // num_strategies
        cell_size = min(cell_w, cell_h)

        # Clamp to reasonable range
        return max(self.MIN_CELL_SIZE, min(self.MAX_CELL_SIZE, cell_size))

    def update(self, mouse_pos):
        """Update hover state based on mouse position"""
        self.hover_row = -1
        self.hover_col = -1

        # Check if mouse is over any cell
        for row_idx, row_rects in enumerate(self.cell_rects):
            for col_idx, rect in enumerate(row_rects):
                if rect.collidepoint(mouse_pos):
                    self.hover_row = row_idx
                    self.hover_col = col_idx
                    return

    def draw(self, window, window_width, window_height, bottom_panel_height):
        """Draw the matchup table visualization

        Args:
            window: pygame surface to draw on
            window_width: current window width
            window_height: current window height
            bottom_panel_height: height of bottom panel (to avoid)
        """
        matchups = self._get_matchup_table()
        num_strategies = self._get_num_strategies()

        # Available area for content
        available_height = window_height - bottom_panel_height - self.padding

        # Draw title (will be repositioned after centering calculation)
        title = self.theme.font_title.render("Strategy Matchup Table", True, self.theme.TEXT_COLOR)

        if matchups is None:
            window.blit(title, (self.padding, self.padding))
            no_data = self.theme.font_medium.render(
                "No matchup data available",
                True, self.theme.TEXT_DIM_COLOR
            )
            window.blit(no_data, (self.padding, 60))
            return

        # Calculate cell size
        self.current_cell_size = self._calculate_cell_size(
            window_width, available_height - 50, num_strategies
        )
        cell_size = self.current_cell_size

        # Get score range for color scaling
        min_score, max_score = self._get_score_range(matchups)

        # Calculate grid dimensions
        grid_width = num_strategies * cell_size
        grid_height = num_strategies * cell_size

        # Calculate panel dimensions
        panel_width = self.LABEL_WIDTH + grid_width + self.PANEL_PADDING * 2
        panel_height = self.HEADER_HEIGHT + grid_height + self.LEGEND_HEIGHT + self.PANEL_PADDING

        # Help text dimensions (for calculating available space)
        help_text_width = 200
        help_text_margin = 25

        # Check if there's room for help text
        total_content_width = panel_width
        show_help = False
        if panel_width + help_text_margin + help_text_width + self.padding * 2 < window_width:
            total_content_width = panel_width + help_text_margin + help_text_width
            show_help = True

        # Center the content horizontally
        content_left = (window_width - total_content_width) // 2
        content_left = max(self.padding, content_left)  # Don't go past left padding

        # Position panel and grid based on centered content
        panel_left = content_left
        grid_left = panel_left + self.LABEL_WIDTH + self.PANEL_PADDING - 5
        grid_top = 50 + self.HEADER_HEIGHT

        self.grid_origin = (grid_left, grid_top)

        # Draw title centered above panel
        window.blit(title, (panel_left, self.padding))

        # Background panel
        panel_rect = pygame.Rect(
            panel_left - 5, 45,
            panel_width,
            panel_height
        )
        pygame.draw.rect(window, self.theme.PANEL_COLOR, panel_rect, border_radius=8)

        # Draw column headers (strategy names at top, rotated)
        strategy_names = [str(s) for s in self.sim.strategies]

        for col_idx, name in enumerate(strategy_names):
            # Render text
            text_surface = self.theme.font_tiny.render(name, True, self.theme.TEXT_COLOR)
            # Rotate 45 degrees
            rotated = pygame.transform.rotate(text_surface, 45)
            # Position at top of column
            x = grid_left + col_idx * cell_size + cell_size // 2 - rotated.get_width() // 2
            y = 50 + self.HEADER_HEIGHT - rotated.get_height() - 5
            window.blit(rotated, (x, y))

        # Draw row labels and cells
        self.cell_rects = []

        for row_idx, row_scores in enumerate(matchups):
            row_rects = []

            # Row label (strategy name on left)
            label = self.theme.font_tiny.render(strategy_names[row_idx], True, self.theme.TEXT_COLOR)
            label_y = grid_top + row_idx * cell_size + (cell_size - label.get_height()) // 2
            window.blit(label, (panel_left, label_y))

            for col_idx, score in enumerate(row_scores):
                # Cell rectangle
                cell_rect = pygame.Rect(
                    grid_left + col_idx * cell_size,
                    grid_top + row_idx * cell_size,
                    cell_size,
                    cell_size
                )
                row_rects.append(cell_rect)

                # Cell color based on score
                color = self._score_to_color(score, min_score, max_score)

                # Draw cell
                pygame.draw.rect(window, color, cell_rect)
                pygame.draw.rect(window, (60, 60, 65), cell_rect, 1)

                # Highlight on hover
                if row_idx == self.hover_row and col_idx == self.hover_col:
                    pygame.draw.rect(window, (255, 255, 255), cell_rect, 2)

            self.cell_rects.append(row_rects)

        # Draw color scale legend
        legend_y = grid_top + grid_height + 15
        legend_x = grid_left

        # Legend title
        legend_title = self.theme.font_tiny.render("Score:", True, self.theme.TEXT_COLOR)
        window.blit(legend_title, (panel_left, legend_y + 5))

        # Color gradient bar
        gradient_width = min(200, grid_width)
        gradient_height = 20
        gradient_x = legend_x
        gradient_y = legend_y + 5

        for i in range(gradient_width):
            t = i / gradient_width
            # Interpolate through the color scale
            score = min_score + t * (max_score - min_score)
            color = self._score_to_color(score, min_score, max_score)
            pygame.draw.line(window, color, (gradient_x + i, gradient_y), (gradient_x + i, gradient_y + gradient_height))

        pygame.draw.rect(window, (80, 80, 85), (gradient_x, gradient_y, gradient_width, gradient_height), 1)

        # Min/max labels
        min_label = self.theme.font_tiny.render(f"{min_score}", True, self.theme.TEXT_DIM_COLOR)
        max_label = self.theme.font_tiny.render(f"{max_score}", True, self.theme.TEXT_DIM_COLOR)
        window.blit(min_label, (gradient_x, gradient_y + gradient_height + 3))
        window.blit(max_label, (gradient_x + gradient_width - max_label.get_width(), gradient_y + gradient_height + 3))

        # "Low" and "High" labels
        low_label = self.theme.font_tiny.render("(low)", True, self.theme.TEXT_DIM_COLOR)
        high_label = self.theme.font_tiny.render("(high)", True, self.theme.TEXT_DIM_COLOR)
        window.blit(low_label, (gradient_x + min_label.get_width() + 3, gradient_y + gradient_height + 3))
        window.blit(high_label, (gradient_x + gradient_width - max_label.get_width() - high_label.get_width() - 3, gradient_y + gradient_height + 3))

        # Draw tooltip for hovered cell
        if self.hover_row >= 0 and self.hover_col >= 0:
            self._draw_tooltip(window, matchups, strategy_names, window_width, window_height)

        # Instructions (only if there's room)
        if show_help:
            help_x = panel_left + panel_width + help_text_margin
            help_y = grid_top
            help_lines = [
                "Reading the table:",
                "",
                "Each cell shows how the",
                "row strategy scores when",
                "playing against the",
                "column strategy.",
                "",
                "Green = high score",
                "Red = low score",
                "",
                "Hover over a cell to",
                "see the exact score."
            ]

            for line in help_lines:
                text = self.theme.font_tiny.render(line, True, self.theme.TEXT_DIM_COLOR)
                window.blit(text, (help_x, help_y))
                help_y += 18

    def _draw_tooltip(self, window, matchups, strategy_names, window_width, window_height):
        """Draw tooltip showing detailed info for hovered cell"""
        row_name = strategy_names[self.hover_row]
        col_name = strategy_names[self.hover_col]
        score = matchups[self.hover_row][self.hover_col]

        # Build tooltip text
        line1 = f"{row_name}"
        line2 = f"vs {col_name}"
        line3 = f"Score: {score}"

        # Calculate tooltip size
        text1 = self.theme.font_small.render(line1, True, self.theme.TEXT_COLOR)
        text2 = self.theme.font_small.render(line2, True, self.theme.TEXT_DIM_COLOR)
        text3 = self.theme.font_medium.render(line3, True, (100, 200, 100))

        tooltip_width = max(text1.get_width(), text2.get_width(), text3.get_width()) + 20
        tooltip_height = text1.get_height() + text2.get_height() + text3.get_height() + 25

        # Position tooltip near mouse but keep on screen
        mouse_pos = pygame.mouse.get_pos()
        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] + 15

        # Keep on screen
        if tooltip_x + tooltip_width > window_width:
            tooltip_x = mouse_pos[0] - tooltip_width - 10
        if tooltip_y + tooltip_height > window_height:
            tooltip_y = mouse_pos[1] - tooltip_height - 10

        # Draw tooltip background
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        pygame.draw.rect(window, (50, 50, 55), tooltip_rect, border_radius=5)
        pygame.draw.rect(window, (80, 80, 85), tooltip_rect, 1, border_radius=5)

        # Draw tooltip text
        window.blit(text1, (tooltip_x + 10, tooltip_y + 8))
        window.blit(text2, (tooltip_x + 10, tooltip_y + 8 + text1.get_height() + 2))
        window.blit(text3, (tooltip_x + 10, tooltip_y + 8 + text1.get_height() + text2.get_height() + 8))

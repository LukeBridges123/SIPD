"""
Statistics UI - Census and time series visualization for SIPD.

Shows strategy population percentages and history over time.
"""

import pygame
from .theme import UITheme
from .components import Button


class StatsUI:
    """UI for the statistics/census view"""

    # Layout constants for census bars
    BAR_HEIGHT = 22
    BAR_SPACING = 4
    BAR_MAX_WIDTH = 300
    SECTION_TITLE_HEIGHT = 30  # Height for "Current Census" title
    PANEL_PADDING = 10  # Padding inside panels

    # Layout constants for time series
    CHART_MARGIN = 50  # Margin around chart for axes
    LEGEND_ITEM_HEIGHT = 18
    MIN_CHART_HEIGHT = 50
    MAX_CHART_HEIGHT = 250

    def __init__(self, sim_state, theme):
        """Initialize the stats UI

        Args:
            sim_state: SimulationState instance
            theme: UITheme instance
        """
        self.sim = sim_state
        self.theme = theme

        # Layout parameters
        self.padding = theme.PADDING

    def _get_num_strategies(self):
        """Get the number of strategies in the simulation"""
        return len(self.sim.colors)

    def _get_label_width(self):
        """Calculate label width based on longest strategy name"""
        strategy_names = list(self.sim.colors.keys())
        max_width = self.theme.get_max_text_width(strategy_names, self.theme.font_small)
        return max_width + 10  # Add some padding

    def _get_legend_width(self):
        """Calculate legend width based on longest strategy name (using tiny font)"""
        strategy_names = list(self.sim.colors.keys())
        max_width = self.theme.get_max_text_width(strategy_names, self.theme.font_tiny)
        return max_width + 24  # Add space for color square and padding

    def _get_census_section_height(self):
        """Calculate the total height needed for the census bars section"""
        num_strategies = self._get_num_strategies()
        bars_height = num_strategies * (self.BAR_HEIGHT + self.BAR_SPACING) - self.BAR_SPACING
        return self.SECTION_TITLE_HEIGHT + bars_height + self.PANEL_PADDING * 2

    def draw(self, window, window_width, window_height, bottom_panel_height):
        """Draw the statistics view

        Args:
            window: pygame surface to draw on
            window_width: current window width
            window_height: current window height
            bottom_panel_height: height of bottom panel (to avoid)
        """
        # Available area for stats (above bottom panel)
        available_height = window_height - bottom_panel_height - self.padding

        # Draw title
        title = self.theme.font_title.render("Population Statistics", True, self.theme.TEXT_COLOR)
        window.blit(title, (self.padding, self.padding))

        # Draw current census bars and get the bottom position
        census_bottom = self._draw_census_bars(window, window_width, available_height)

        # Draw time series chart below census section
        self._draw_time_series(window, window_width, available_height, census_bottom)

    def _draw_census_bars(self, window, window_width, available_height):
        """Draw horizontal bars showing current population percentages.

        Returns:
            The bottom y-coordinate of the census section (for positioning subsequent elements)
        """
        census = self.sim.get_current_census()

        # Calculate dynamic dimensions
        label_width = self._get_label_width()
        bar_max_width = min(self.BAR_MAX_WIDTH, window_width // 3)
        census_height = self._get_census_section_height()

        bar_area_top = 50
        bar_x = self.padding + label_width  # Leave room for labels

        # Percentage label width (e.g., "100.0%")
        pct_label_width = self.theme.get_text_width("100.0%", self.theme.font_small) + 8

        # Background panel - sized to fit content
        panel_rect = pygame.Rect(
            self.padding - 5, bar_area_top - self.PANEL_PADDING,
            bar_max_width + label_width + pct_label_width + self.PANEL_PADDING * 2,
            census_height + self.PANEL_PADDING
        )
        pygame.draw.rect(window, self.theme.PANEL_COLOR, panel_rect, border_radius=8)

        # Section title
        section_title = self.theme.font_medium.render("Current Census", True, self.theme.TEXT_COLOR)
        window.blit(section_title, (self.padding, bar_area_top))

        y = bar_area_top + self.SECTION_TITLE_HEIGHT

        for strategy_name, percentage in census.items():
            color = self.sim.colors.get(strategy_name, (150, 150, 150))

            # Strategy label (full name)
            label = self.theme.font_small.render(strategy_name, True, self.theme.TEXT_COLOR)
            window.blit(label, (self.padding, y + 2))

            # Bar background
            bar_bg_rect = pygame.Rect(bar_x, y, bar_max_width, self.BAR_HEIGHT)
            pygame.draw.rect(window, (60, 60, 65), bar_bg_rect, border_radius=3)

            # Bar fill
            bar_width = int((percentage / 100) * bar_max_width)
            if bar_width > 0:
                bar_rect = pygame.Rect(bar_x, y, bar_width, self.BAR_HEIGHT)
                pygame.draw.rect(window, color, bar_rect, border_radius=3)

            # Percentage label
            pct_text = self.theme.font_small.render(f"{percentage:.1f}%", True, self.theme.TEXT_COLOR)
            window.blit(pct_text, (bar_x + bar_max_width + 8, y + 2))

            y += self.BAR_HEIGHT + self.BAR_SPACING

        # Return bottom of census section for positioning time series
        return bar_area_top + census_height + self.PANEL_PADDING * 2

    def _draw_time_series(self, window, window_width, available_height, census_bottom):
        """Draw time series chart of population history

        Args:
            window: pygame surface to draw on
            window_width: current window width
            available_height: available height for content
            census_bottom: y-coordinate of the bottom of the census section
        """
        history = self.sim.census_history

        # Calculate dynamic dimensions
        legend_width = self._get_legend_width()
        num_strategies = self._get_num_strategies()

        # Chart positioning - below census section with some spacing
        chart_top = census_bottom + 20  # 20px gap after census section

        if len(history) < 2:
            # Not enough data to draw
            no_data = self.theme.font_medium.render(
                "Run simulation to see time series...",
                True, self.theme.TEXT_DIM_COLOR
            )
            window.blit(no_data, (self.padding, chart_top))
            return

        # Chart area dimensions
        chart_left = self.padding + self.CHART_MARGIN
        chart_width = window_width - 2 * self.padding - self.CHART_MARGIN - legend_width - 20
        chart_height = min(self.MAX_CHART_HEIGHT, available_height - chart_top - 50)

        if chart_width < 100 or chart_height < self.MIN_CHART_HEIGHT:
            return  # Not enough space

        # Calculate legend height based on number of strategies
        legend_height = num_strategies * self.LEGEND_ITEM_HEIGHT

        # Background panel - sized to fit content
        panel_height = max(chart_height + 70, legend_height + 60)
        panel_rect = pygame.Rect(
            self.padding - 5, chart_top - 30,
            chart_width + self.CHART_MARGIN + legend_width + 30, panel_height
        )
        pygame.draw.rect(window, self.theme.PANEL_COLOR, panel_rect, border_radius=8)

        # Section title
        section_title = self.theme.font_medium.render("Population Over Time", True, self.theme.TEXT_COLOR)
        window.blit(section_title, (self.padding, chart_top - 25))

        # Chart background
        chart_rect = pygame.Rect(chart_left, chart_top, chart_width, chart_height)
        pygame.draw.rect(window, (35, 35, 40), chart_rect)
        pygame.draw.rect(window, (70, 70, 75), chart_rect, 1)

        # Y-axis labels (0%, 50%, 100%)
        for pct, label_text in [(0, "0%"), (50, "50%"), (100, "100%")]:
            y = chart_top + chart_height - int((pct / 100) * chart_height)
            label = self.theme.font_tiny.render(label_text, True, self.theme.TEXT_DIM_COLOR)
            window.blit(label, (chart_left - 35, y - 6))
            # Grid line
            pygame.draw.line(window, (50, 50, 55), (chart_left, y), (chart_left + chart_width, y), 1)

        # X-axis label
        x_label = self.theme.font_tiny.render(f"Generation (0 - {len(history) - 1})", True, self.theme.TEXT_DIM_COLOR)
        window.blit(x_label, (chart_left + chart_width // 2 - 40, chart_top + chart_height + 8))

        # Draw lines for each strategy
        strategy_names = list(self.sim.colors.keys())

        for strategy_name in strategy_names:
            color = self.sim.colors[strategy_name]
            points = []

            for i, census in enumerate(history):
                x = chart_left + int((i / max(1, len(history) - 1)) * chart_width)
                pct = census.get(strategy_name, 0)
                y = chart_top + chart_height - int((pct / 100) * chart_height)
                points.append((x, y))

            # Draw line connecting points
            if len(points) >= 2:
                # If too many points, sample them
                if len(points) > chart_width:
                    step = len(points) // chart_width
                    points = points[::step]

                pygame.draw.lines(window, color, False, points, 2)

        # Legend (positioned to the right of the chart)
        legend_x = chart_left + chart_width + 15
        legend_y = chart_top + 10

        for i, (strategy_name, color) in enumerate(self.sim.colors.items()):
            # Small color square
            pygame.draw.rect(window, color, (legend_x, legend_y + i * self.LEGEND_ITEM_HEIGHT, 10, 10), border_radius=2)
            # Full strategy name
            label = self.theme.font_tiny.render(strategy_name, True, self.theme.TEXT_DIM_COLOR)
            window.blit(label, (legend_x + 14, legend_y + i * self.LEGEND_ITEM_HEIGHT - 2))

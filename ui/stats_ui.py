"""
Statistics UI - Census and time series visualization for SIPD.

Shows strategy population percentages and history over time.
"""

import pygame
from .theme import UITheme
from .components import Button


class StatsUI:
    """UI for the statistics/census view"""

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
        self.chart_margin = 50  # Margin around chart for axes

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

        # Draw current census bars
        self._draw_census_bars(window, window_width, available_height)

        # Draw time series chart
        self._draw_time_series(window, window_width, available_height)

    def _draw_census_bars(self, window, window_width, available_height):
        """Draw horizontal bars showing current population percentages"""
        census = self.sim.get_current_census()

        bar_area_top = 50
        bar_area_height = 200  # Increased to fit all 6 strategies
        bar_height = 22
        bar_spacing = 4
        bar_max_width = min(300, window_width // 3)
        label_width = 145  # Width for strategy name labels
        bar_x = self.padding + label_width  # Leave room for labels

        # Background panel
        panel_rect = pygame.Rect(
            self.padding - 5, bar_area_top - 10,
            bar_max_width + label_width + 70, bar_area_height + 20
        )
        pygame.draw.rect(window, self.theme.PANEL_COLOR, panel_rect, border_radius=8)

        # Section title
        section_title = self.theme.font_medium.render("Current Census", True, self.theme.TEXT_COLOR)
        window.blit(section_title, (self.padding, bar_area_top))

        y = bar_area_top + 30

        for strategy_name, percentage in census.items():
            color = self.sim.colors.get(strategy_name, (150, 150, 150))

            # Strategy label (full name, will fit in label_width)
            label = self.theme.font_small.render(strategy_name, True, self.theme.TEXT_COLOR)
            window.blit(label, (self.padding, y + 2))

            # Bar background
            bar_bg_rect = pygame.Rect(bar_x, y, bar_max_width, bar_height)
            pygame.draw.rect(window, (60, 60, 65), bar_bg_rect, border_radius=3)

            # Bar fill
            bar_width = int((percentage / 100) * bar_max_width)
            if bar_width > 0:
                bar_rect = pygame.Rect(bar_x, y, bar_width, bar_height)
                pygame.draw.rect(window, color, bar_rect, border_radius=3)

            # Percentage label
            pct_text = self.theme.font_small.render(f"{percentage:.1f}%", True, self.theme.TEXT_COLOR)
            window.blit(pct_text, (bar_x + bar_max_width + 8, y + 2))

            y += bar_height + bar_spacing

    def _draw_time_series(self, window, window_width, available_height):
        """Draw time series chart of population history"""
        history = self.sim.census_history

        if len(history) < 2:
            # Not enough data to draw
            no_data = self.theme.font_medium.render(
                "Run simulation to see time series...",
                True, self.theme.TEXT_DIM_COLOR
            )
            window.blit(no_data, (self.padding, 290))
            return

        # Chart area
        chart_left = self.padding + self.chart_margin
        chart_top = 280  # Moved down to account for taller census section
        legend_width = 130  # Space for legend on the right
        chart_width = window_width - 2 * self.padding - self.chart_margin - legend_width - 20
        chart_height = min(250, available_height - chart_top - 50)

        if chart_width < 100 or chart_height < 50:
            return  # Not enough space

        # Background panel
        panel_rect = pygame.Rect(
            self.padding - 5, chart_top - 30,
            chart_width + self.chart_margin + legend_width + 30, chart_height + 70
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
            pygame.draw.rect(window, color, (legend_x, legend_y + i * 18, 10, 10), border_radius=2)
            # Full strategy name
            label = self.theme.font_tiny.render(strategy_name, True, self.theme.TEXT_DIM_COLOR)
            window.blit(label, (legend_x + 14, legend_y + i * 18 - 2))

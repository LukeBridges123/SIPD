"""
Mix UI - Strategy weight configuration for SIPD.

Allows users to adjust the initial distribution of strategies before starting a simulation.
"""

import pygame
from .theme import UITheme
from .components import Button, StrategyWeightControl


class MixUI:
    """UI for configuring the initial strategy mix"""

    # Layout constants
    CONTROL_HEIGHT = 36
    CONTROL_SPACING = 8
    SECTION_TITLE_HEIGHT = 35
    PANEL_PADDING = 15

    def __init__(self, sim_state, theme):
        """Initialize the mix UI

        Args:
            sim_state: SimulationState instance
            theme: UITheme instance
        """
        self.sim = sim_state
        self.theme = theme
        self.padding = theme.PADDING

        # Create weight controls (will be positioned in draw)
        self.weight_controls = []
        self._create_controls()

        # Reset button
        self.btn_reset = Button(0, 0, 120, 28, "Reset to Equal", (80, 80, 90), (100, 100, 110))

        # Track if any slider is being dragged
        self.dragging = False

    def _create_controls(self):
        """Create weight controls for each strategy"""
        self.weight_controls = []
        for strategy_name, color in self.sim.colors.items():
            weight = self.sim.strategy_weights.get(strategy_name, 1.0)
            control = StrategyWeightControl(
                0, 0, 400, self.CONTROL_HEIGHT,
                strategy_name, color, weight
            )
            self.weight_controls.append(control)

    def _sync_weights_from_sim(self):
        """Sync control values from simulation state"""
        for ctrl in self.weight_controls:
            ctrl.weight = self.sim.strategy_weights.get(ctrl.strategy_name, 1.0)
            ctrl._update_rects()

    def _sync_weights_to_sim(self):
        """Sync control values back to simulation state"""
        for ctrl in self.weight_controls:
            self.sim.strategy_weights[ctrl.strategy_name] = ctrl.weight

    def _get_num_strategies(self):
        """Get the number of strategies"""
        return len(self.sim.colors)

    def _get_content_height(self):
        """Calculate height needed for all controls"""
        num = self._get_num_strategies()
        return (self.SECTION_TITLE_HEIGHT +
                num * (self.CONTROL_HEIGHT + self.CONTROL_SPACING) +
                self.PANEL_PADDING * 2 + 50)  # Extra for button

    def update(self, mouse_pos):
        """Update hover states"""
        for ctrl in self.weight_controls:
            ctrl.update(mouse_pos)
        self.btn_reset.update(mouse_pos)

    def handle_mouse_down(self, mouse_pos):
        """Handle mouse down events. Returns True if event was handled."""
        # Check reset button
        if self.btn_reset.is_clicked(mouse_pos, True):
            self.sim.reset_weights_to_equal()
            self._sync_weights_from_sim()
            return True

        # Check weight controls
        for ctrl in self.weight_controls:
            if ctrl.handle_mouse_down(mouse_pos):
                self.dragging = True
                self._sync_weights_to_sim()
                return True

        return False

    def handle_mouse_up(self):
        """Handle mouse up events"""
        self.dragging = False
        for ctrl in self.weight_controls:
            ctrl.handle_mouse_up()
        self._sync_weights_to_sim()

    def handle_mouse_motion(self, mouse_pos):
        """Handle mouse motion (for dragging sliders)"""
        if self.dragging:
            for ctrl in self.weight_controls:
                ctrl.update(mouse_pos)
            self._sync_weights_to_sim()

    def draw(self, window, window_width, window_height, bottom_panel_height):
        """Draw the mix configuration view

        Args:
            window: pygame surface to draw on
            window_width: current window width
            window_height: current window height
            bottom_panel_height: height of bottom panel (to avoid)
        """
        # Ensure controls match current strategies (in case strategies were added)
        if len(self.weight_controls) != len(self.sim.colors):
            self._create_controls()
        self._sync_weights_from_sim()

        # Available area for content
        available_height = window_height - bottom_panel_height - self.padding

        # Calculate control width (fixed max width for consistent appearance)
        control_width = min(500, window_width - self.padding * 4)

        # Panel dimensions
        panel_top = 75
        content_height = self._get_content_height()
        panel_width = control_width + self.PANEL_PADDING * 2

        # Help text dimensions
        help_text_width = 200
        help_text_margin = 35

        # Check if there's room for help text
        total_content_width = panel_width
        show_help = False
        if panel_width + help_text_margin + help_text_width + self.padding * 2 < window_width:
            total_content_width = panel_width + help_text_margin + help_text_width
            show_help = True

        # Center the content horizontally
        content_left = (window_width - total_content_width) // 2
        content_left = max(self.padding, content_left)  # Don't go past left padding

        # Position panel based on centered content
        panel_left = content_left

        # Draw title
        title = self.theme.font_title.render("Initial Strategy Mix", True, self.theme.TEXT_COLOR)
        window.blit(title, (panel_left, self.padding))

        # Subtitle/instructions
        subtitle = self.theme.font_small.render(
            "Adjust weights to control starting population distribution",
            True, self.theme.TEXT_DIM_COLOR
        )
        window.blit(subtitle, (panel_left, self.padding + 35))

        # Panel for controls
        panel_rect = pygame.Rect(
            panel_left - 5, panel_top,
            panel_width, content_height
        )
        pygame.draw.rect(window, self.theme.PANEL_COLOR, panel_rect, border_radius=8)

        # Section title
        section_title = self.theme.font_medium.render("Strategy Weights", True, self.theme.TEXT_COLOR)
        window.blit(section_title, (panel_left + 5, panel_top + 10))

        # Get percentages for display
        percentages = self.sim.get_weight_percentages()

        # Draw controls
        control_y = panel_top + self.SECTION_TITLE_HEIGHT + 10
        for ctrl in self.weight_controls:
            ctrl.width = control_width
            ctrl.slider_width = control_width - 200
            ctrl.value_x = panel_left + control_width - 45
            ctrl.update_position(panel_left + 5, control_y)

            pct = percentages.get(ctrl.strategy_name, 0)
            ctrl.draw(window, self.theme.font_small, self.theme.font_small, percentage=pct)

            control_y += self.CONTROL_HEIGHT + self.CONTROL_SPACING

        # Reset button
        self.btn_reset.rect.x = panel_left + 5
        self.btn_reset.rect.y = control_y + 10
        self.btn_reset.draw(window, self.theme.font_small)

        # Help text on the right side (only if there's room)
        if show_help:
            help_x = panel_left + panel_width + help_text_margin
            help_y = panel_top + 10
            help_lines = [
                "How weights work:",
                "",
                "Weights determine the relative",
                "probability of each strategy.",
                "",
                "Example: If Tit-for-tat has",
                "weight 3 and Always defect",
                "has weight 1, Tit-for-tat",
                "will appear 3x more often.",
                "",
                "Set weight to 0 to exclude",
                "a strategy entirely.",
                "",
                "Press R or N to apply the",
                "new mix to the simulation."
            ]

            for line in help_lines:
                text = self.theme.font_tiny.render(line, True, self.theme.TEXT_DIM_COLOR)
                window.blit(text, (help_x, help_y))
                help_y += 18

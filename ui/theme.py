"""
UI Theme and styling constants for SIPD.

Centralizes colors, fonts, and layout parameters.
"""

import pygame


class UITheme:
    """Theme class containing all visual styling for the application"""

    # Color scheme
    BG_COLOR = (30, 30, 35)
    PANEL_COLOR = (45, 45, 50)
    TEXT_COLOR = (220, 220, 220)
    TEXT_DIM_COLOR = (140, 140, 140)
    ACCENT_COLOR = (52, 152, 219)

    # Layout constants
    CELL_SIZE = 8
    SIDEBAR_WIDTH = 220
    BOTTOM_PANEL_HEIGHT = 120
    PADDING = 15

    # Font sizes
    FONT_TITLE_SIZE = 32
    FONT_LARGE_SIZE = 26
    FONT_MEDIUM_SIZE = 22
    FONT_SMALL_SIZE = 18
    FONT_TINY_SIZE = 16

    def __init__(self):
        """Initialize theme and fonts"""
        pygame.font.init()

        self.font_title = pygame.font.Font(None, self.FONT_TITLE_SIZE)
        self.font_large = pygame.font.Font(None, self.FONT_LARGE_SIZE)
        self.font_medium = pygame.font.Font(None, self.FONT_MEDIUM_SIZE)
        self.font_small = pygame.font.Font(None, self.FONT_SMALL_SIZE)
        self.font_tiny = pygame.font.Font(None, self.FONT_TINY_SIZE)

    def get_text_width(self, text, font=None):
        """Get the pixel width of text rendered in the given font.

        Args:
            text: The text to measure
            font: Font to use (defaults to font_small)

        Returns:
            Width in pixels
        """
        if font is None:
            font = self.font_small
        return font.size(text)[0]

    def get_max_text_width(self, texts, font=None):
        """Get the maximum width among a list of text strings.

        Args:
            texts: List of text strings to measure
            font: Font to use (defaults to font_small)

        Returns:
            Maximum width in pixels
        """
        if font is None:
            font = self.font_small
        return max(font.size(text)[0] for text in texts) if texts else 0

    def get_text_height(self, font=None):
        """Get the line height for a font.

        Args:
            font: Font to use (defaults to font_small)

        Returns:
            Height in pixels
        """
        if font is None:
            font = self.font_small
        return font.get_linesize()


# Default theme instance
DEFAULT_THEME = UITheme()

"""
UI Components for SIPD.

Reusable widgets: buttons, parameter controls, etc.
"""

import pygame


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

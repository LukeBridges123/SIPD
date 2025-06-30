import asyncio
import pygame
import sys
from strategies import always_defect, always_cooperate, tit_for_tat, pavlov, revenger, prisoners_dilemma, tf2t
from grid import Grid



pygame.init()
pygame.font.init()
clock = pygame.time.Clock()

# Initialize fonts for text rendering
font_large = pygame.font.Font(None, 28)
font_small = pygame.font.Font(None, 20)

# Define grid size
n, m = 50, 50

strategies = [always_cooperate, always_defect, tit_for_tat, pavlov, revenger, tf2t]
colors = {"Always cooperate" : (0, 255, 0), "Always defect": (255, 0, 0), "Tit-for-tat": (0, 0, 255), "Pavlov": (255, 150, 0),
          "Revenger": (150, 60, 150), "Tit-for-two-tats": (60, 150, 150)}
board = Grid(strategies=strategies, rows=n, cols=m, game=prisoners_dilemma, rounds=1000, noise=0, mutation_rate = 0)
board.populate_randomly()

# Step counter
step_count = 0

# Define the size of each square (slightly larger for better visibility)
square_size = 6

# Calculate grid dimensions
grid_width = m * square_size
grid_height = n * square_size

# UI panel height for displaying information (increased for more space)
ui_panel_height = 100

# Calculate total window size (wider for more breathing room)
window_width = max(grid_width, 600)  # Ensure minimum width of 600px
window_height = grid_height + ui_panel_height

# Create Pygame window
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Spatial Iterated Prisoner's Dilemma")


async def main():
    global step_count
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    board.update_grid()
                    step_count += 1
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

        # Fill background
        window.fill((255, 255, 255))

        # Calculate grid offset to center it horizontally
        grid_offset_x = (window_width - grid_width) // 2

        # Draw the grid (centered horizontally)
        for i in range(n):
            for j in range(m):
                color = colors[board.strategy_name_at(i, j)]
                pygame.draw.rect(window, color,
                                 (grid_offset_x + j * square_size, i * square_size,
                                  square_size, square_size))

        # Draw UI panel background
        pygame.draw.rect(window, (240, 240, 240), (0, grid_height, window_width, ui_panel_height))
        
        # Draw border between grid and UI panel
        pygame.draw.line(window, (200, 200, 200), (0, grid_height), (window_width, grid_height), 2)
        
        # Display game information in the UI panel
        ui_y_start = grid_height + 15
        
        # Row 1: Generation counter
        step_text = font_large.render(f"Generation: {step_count}", True, (0, 0, 0))
        window.blit(step_text, (20, ui_y_start))
        
        # Row 2: Controls
        controls_text = font_small.render("Controls: SPACE = Next Generation | ESC = Quit", True, (100, 100, 100))
        window.blit(controls_text, (20, ui_y_start + 35))
        
        # Row 3: Game parameters (for future expansion)
        params_text = font_small.render(f"Grid: {n}×{m} | Rounds: 1000 | Noise: 0% | Mutation: 0%", True, (120, 120, 120))
        window.blit(params_text, (20, ui_y_start + 55))

        pygame.display.update()
        await asyncio.sleep(0)
        clock.tick(60)

    pygame.quit()
    sys.exit()

asyncio.run(main())
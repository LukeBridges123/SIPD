import asyncio
import pygame
import sys
from strategies import always_defect, always_cooperate, tit_for_tat, pavlov, revenger, prisoners_dilemma, tf2t
from grid import Grid



pygame.init()
clock = pygame.time.Clock()
# Define grid size
n, m = 100, 500

strategies = [always_cooperate, always_defect, tit_for_tat, pavlov]
colors = {"Always cooperate" : (0, 255, 0), "Always defect": (255, 0, 0), "Tit-for-tat": (0, 0, 255), "Pavlov": (255, 150, 0)}
board = Grid(strategies=strategies, rows=n, cols=m, game=prisoners_dilemma, rounds=1000, noise=0, mutation_rate = 0)
board.populate_randomly()

# Define the size of each square
square_size = 1

# Calculate window size
window_width = m * square_size
window_height = n * square_size

# Create Pygame window
window = pygame.display.set_mode((window_width, window_height))


async def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    board.update_grid()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

        window.fill((255, 255, 255))

        for i in range(n):
            for j in range(m):
                color = colors[board.strategy_name_at(i, j)]
                pygame.draw.rect(window, color,
                                 (j * square_size, i * square_size,
                                  square_size, square_size))

        pygame.display.update()
        await asyncio.sleep(0)
        clock.tick(60)

    pygame.quit()
    sys.exit()

asyncio.run(main())
from strategies import *
import random

class Grid:
    def __init__(self, strategies: list[Strategy], rows: int, cols: int, game: Game, rounds: int, noise: float = 0,
                 mutation_rate: float = 0):
        if rows < 3 or cols < 3:
            raise ValueError("Board too small")
        if len(strategies) < 1:
            raise ValueError("Empty list of strategies")
        self.rows = rows
        self.cols = cols
        # implicitly, this fills the board with copies of strategy 0.
        # this can be changed with populate_randomly and set_grid.
        self.board = [[0 for i in range(cols)] for j in range(rows)]
        self.strategies = strategies
        self.matchups = compute_matchup_table(strategies, game, rounds, noise=noise)
        self.mutation_rate = mutation_rate

    def __str__(self):
        string_rep = ""
        for i in range(self.rows):
            for j in range(self.cols):
                string_rep += self.strategies[self.board[i][j]].get_symbol() + ' '
            string_rep += "\n"
        return string_rep

    def populate_randomly(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.board[i][j] = random.randrange(0, len(self.strategies))

    def strategy_name_at(self, row: int, col: int):
        if row >= self.rows or col >= self.cols:
            raise ValueError("Invalid grid index")
        return str(self.strategies[self.board[row][col]])

    def strategy_number_at(self, row: int, col: int):
        if row >= self.rows or col >= self.cols:
            raise ValueError("Invalid grid index")
        return self.board[row][col]

    def find_total_score(self, row: int, col: int):
        total = 0
        curr_strategy_matchups = self.matchups[self.board[row][col]]
        up = (row - 1) % self.rows
        down = (row + 1) % self.rows
        left = (col - 1) % self.cols
        right = (col + 1) % self.cols

        # go clockwise starting with the top cell: so up, up-right, right, and so on
        total += curr_strategy_matchups[self.board[up][col]]
        total += curr_strategy_matchups[self.board[up][right]]
        total += curr_strategy_matchups[self.board[row][right]]
        total += curr_strategy_matchups[self.board[down][right]]
        total += curr_strategy_matchups[self.board[down][col]]
        total += curr_strategy_matchups[self.board[down][left]]
        total += curr_strategy_matchups[self.board[row][left]]
        total += curr_strategy_matchups[self.board[up][left]]

        return total

    def get_max_of_neighbors(self, score_grid: list[list[int]], row: int, col: int):
        up = (row - 1) % self.rows
        down = (row + 1) % self.rows
        left = (col - 1) % self.cols
        right = (col + 1) % self.cols

        directions = [(up, col), (up, right), (row, right), (down, right), (down, col), (down, left), (row, left), (up, left)]
        current_max_score = score_grid[row][col]
        current_best_strategy = self.strategy_number_at(row, col)
        for (i, j) in directions:
            if score_grid[i][j] > current_max_score:
                current_max_score = score_grid[i][j]
                current_best_strategy = self.strategy_number_at(i, j)
            elif score_grid[i][j] == current_max_score and self.strategy_number_at(i, j) == self.strategy_number_at(row, col):
                # favor current strategy in ties
                current_best_strategy = self.strategy_number_at(row, col)
        return current_best_strategy

    def update_grid(self):
        score_grid = [[0 for i in range(self.cols)] for j in range(self.rows)]
        new_board = [[0 for i in range(self.cols)] for j in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                score_grid[row][col] = self.find_total_score(row, col)
        for row in range(self.rows):
            for col in range(self.cols):
                if random.random() < self.mutation_rate:
                    new_board[row][col] = random.randrange(0, len(self.strategies))
                else:
                    new_board[row][col] = self.get_max_of_neighbors(score_grid, row, col)
        self.board = new_board

from typing import Callable, Dict
import random


class Game:
    def __init__(self, payoff_matrix: list[list[tuple[int, int]]]):
        self.payoff_matrix = payoff_matrix

    def play_one_round(self, move1, move2):
        if move1 >= len(self.payoff_matrix):
            raise ValueError("Invalid move for player 1")
        if move2 >= len(self.payoff_matrix[move1]):
            raise ValueError("Invalid move for player 2")
        return self.payoff_matrix[move1][move2]

    def num_moves(self):
        return len(self.payoff_matrix)


class Strategy:
    # strategy function should be of the form: strategy(my_history, opponent_history)
    def __init__(self, round_strategy: Callable[[list[int], list[int]], int], name: str, symbol: str):
        self.round_strategy = round_strategy
        self.name = name
        self.symbol = symbol

    def __str__(self):
        return self.name

    def get_symbol(self):
        return self.symbol


# table[i][j] = payoff for strategy i if it plays against strategy j
def compute_matchup_table(strategies: list[Strategy], game: Game, rounds: int, noise: float = 0)-> list[list[int]]:
    matchups = [[0 for i in range(len(strategies))] for j in range(len(strategies))]
    for i in range(len(strategies)):
        for j in range(i, len(strategies)):
            matchups[i][j], matchups[j][i] = play_iterated_game(strategies[i], strategies[j], game, rounds, noise)
    return matchups


def play_iterated_game(player1: Strategy, player2: Strategy, game: Game, rounds: int, noise: float = 0):
    player1_history = []
    player2_history = []
    player1_total = 0
    player2_total = 0
    for i in range(rounds):
        move1 = player1.round_strategy(player1_history, player2_history)
        if random.random() < noise:
            move1 = random.randrange(game.num_moves())
        move2 = player2.round_strategy(player2_history, player1_history)
        if random.random() < noise:
            move2 = random.randrange(game.num_moves())
        payoff = game.play_one_round(move1, move2)
        player1_history.append(move1)
        player2_history.append(move2)
        player1_total += payoff[0]
        player2_total += payoff[1]
    return player1_total, player2_total


def build_strategy_function_from_lookup(lookup: Dict[tuple[tuple[int], tuple[int]], int],
                                        memory_length: int, default_move: int = 0):
    print(lookup.keys())
    for my_moves, opponents_moves in lookup.keys():
        if len(my_moves) != memory_length or len(opponents_moves) != memory_length:
            raise ValueError("Invalid strategy: given history is not the right length")

    def new_strategy(my_history: list[int], opponent_history: list[int]):
        if len(my_history) < memory_length:
            return default_move
        my_last_moves = tuple(my_history[-memory_length:])
        opponents_last_moves = tuple(opponent_history[-memory_length:])
        if (my_last_moves, opponents_last_moves) in lookup:
            return lookup[(my_last_moves, opponents_last_moves)]
        else:
            return default_move
    return new_strategy

# 0 = "defect", 1 = "cooperate"
# matrix[i][j][k] = payoff player k receives when player 1 plays move i and player 2 plays move j

prisoners_dilemma = Game([[(1, 1), (5, 0)],
                          [(0, 5), (3, 3)]])


def always_defect_strategy(my_history: list[int], opponent_history: list[int]) -> int:
    return 0
always_defect = Strategy(always_defect_strategy, "Always defect", "D")


def always_cooperate_strategy(my_history: list[int], opponent_history: list[int]) -> int:
    return 1

always_cooperate = Strategy(always_cooperate_strategy, "Always cooperate", "C")

def tft_strategy(my_history: list[int], opponent_history: list[int]) -> int:
    if len(my_history) == 0 or len(opponent_history) == 0:
        return 1
    return opponent_history[-1]


tit_for_tat = Strategy(tft_strategy, "Tit-for-tat", "T")


def pavlov_strategy(my_history: list[int], opponent_history: list[int]) -> int:
    if len(my_history) == 0 or len(opponent_history) == 0:
        return 1
    # if opponent cooperates (plays 1), keep doing what you're doing; otherwise, switch
    return my_history[-1] ^ (1 ^ opponent_history[-1])


pavlov = Strategy(pavlov_strategy, "Pavlov", "P")


def revenger_strategy(my_history: list[int], opponent_history: list[int]) -> int:
    if len(my_history) == 0 or len(opponent_history) == 0:
        return 1
    # if either you or your opponent just defected, defect yourself; otherwise cooperate.
    # in other words, cooperate until your opponent defects, and keep defecting forever afterwards.
    if my_history[-1] == 0 or opponent_history[-1] == 0:
        return 0
    return 1


revenger = Strategy(revenger_strategy, "Revenger", "R")

def tit_for_two_tats_strategy(my_history: list[int], opponent_history: list[int]) -> int:
    if len(my_history) < 2 or len(opponent_history) < 2:
        return 1
    if opponent_history[-1] == 0 and opponent_history[-1] == 0:
        return 0
    return 1

tf2t = Strategy(tit_for_two_tats_strategy, "Tit-for-two-tats", "2")

tft_lookup = {((0,), (0,)): 0,
              ((0,), (1,)): 1,
              ((1,), (0,)): 0,
              ((1,), (1,)): 1}
new_tft_strategy = build_strategy_function_from_lookup(tft_lookup, 1, 1)
new_tft = Strategy(new_tft_strategy, "New tit-for-tat", "A")

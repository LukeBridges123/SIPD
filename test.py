from strategies import always_defect, always_cooperate, tit_for_tat, pavlov, revenger, prisoners_dilemma, tf2t, new_tft
from grid import Grid

strategies = [always_cooperate, always_defect, new_tft]
test = Grid(strategies=strategies, rows=10, cols=50, game=prisoners_dilemma, rounds=1000, noise=0)
test.populate_randomly()
print(test)
for i in range(30):
    test.update_grid()
    print(test)
#https://fivethirtyeight.com/features/can-you-systematically-solve-a-friday-crossword/

from functools import lru_cache

strategies = {"aggressive": [(0.3, 0), (0.3, 1), (0.4, 3)],
              "conservative": [(0.1, 0), (0.8, 1), (0.1, 3)],
              "waste": [(1.0, 0)]}

GOAL = 3

@lru_cache()
def eval_pos(points, moves_remaining):
    assert moves_remaining > 0

    if points > GOAL:
        return 0.0, None

    best_prob = 0
    best_strat = None

    for strat in strategies:
        cum_prob = 0
        for prob, pts in strategies[strat]:
            if moves_remaining == 1:
                if points + pts == GOAL:
                    cum_prob += prob
            else:
                cum_prob += prob * eval_pos(points + pts, moves_remaining - 1)[0]
        
        if cum_prob > best_prob:
                best_prob = cum_prob
                best_strat = strat

    return best_prob, best_strat


if __name__ == "__main__":
    print(eval_pos(0, 3))

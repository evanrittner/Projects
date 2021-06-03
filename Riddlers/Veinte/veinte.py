#https://fivethirtyeight.com/features/are-you-smarter-than-a-fourth-grader/

import functools


END_NUM = 20
MIN_INCR = 1
MAX_INCR = 4


class Move:
    def __init__(self, prev, new, outcome):
        self.prev = prev       # the number the previous player said
        self.new = new         # the number the current player should say
        self.outcome = outcome # the final outcome (number of addl. rounds guaranteed)

    def __repr__(self): 
        return f"Move({self.prev}, {self.new}, {self.outcome})"


# explanation of output: 
# eval_round(3) -> [1, 2, 0]
# the first person to start the round of three will advance to 1 additional round
# the second will advance to 2 additional rounds (i.e. win the whole game)
# the third person will be eliminated in the round of three

@functools.lru_cache()
def eval_round(round):
    if round == 1:
        return [0]
    
    # the goals for this round's players: in-order final scores, if player who
    # says "20" is the last in this list (so the eliminated player is first)
    # i.e. rnd 3: [0, 1, 2] -> player who says "20" wins, prev. advances once, etc.
    goals = [0] + [1 + pos for pos in eval_round(round - 1)]
    
    # lookup: what is your outcome if you force the next player to lose / win / etc.
    # your eventual outcome in this list is at the index of the next player's outcome
    forced_outcomes = [0] * round
    for i in range(round):
        forced_outcomes[goals[i]] = goals[i - 1]

    strats = dict()
    for prev_num in range(END_NUM - MIN_INCR, 0, -1):
        options = set()
        for incr in range(MIN_INCR, MAX_INCR + 1):
            new_num = prev_num + incr

            if new_num == END_NUM:
                my_outcome = goals[-1] # if you say "20"

            elif new_num not in strats.keys(): # we can't force the next player to go to an invalid count
                continue

            else:
                next_outcome = strats[new_num].outcome # the next player's outcome if you make this move
                my_outcome = forced_outcomes[next_outcome]
            
            options.add(Move(prev_num, prev_num + incr, my_outcome))
        
        # best strat for us here is option guaranteeing us the best (max) outcome
        if options:
            strats[prev_num] = max(options, key=lambda m: m.outcome)


    # because first player to move always starts with "1", the outcome of the 
    # strat when the previous player said "1" is the outcome for the second player.
    # the outcomes for the other players can be determined from this and "goals" list above
    try:
        index_2nd = goals.index(strats[1].outcome)
    except KeyError as e:
        raise RuntimeError("invalid configuration of min/max increments and ending number") from e
    
    results = [0] * round
    for i in range(round):
        results[(i + 1) % round] = goals[(i + index_2nd) % round]

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 4

    print(n, eval_round(n))

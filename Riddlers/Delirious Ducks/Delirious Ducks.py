#https://fivethirtyeight.com/features/can-you-track-the-delirious-ducks/

import math
import random


class Game:
    def __init__(self, size=3, num=2, dim=2):
        self.size = size
        self.num_ducks = num
        self.dimension = dim
        
        self.middle = math.floor((self.size - 1) / 2)
        self.reset()
    

    def reset(self):
        self.ducks = [[self.middle] * self.dimension] * self.num_ducks
    

    def step(self):
        # for each duck, enumerate the directions it could move, then pick one
        for d_index in range(self.num_ducks):
            directions = []
            for axis_index in range(self.dimension): # each dimension has two potential directions to move in
                # check if we can move 'backward' in this dimension
                if self.ducks[d_index][axis_index] is not 0:
                    directions.append(tuple(-1 if i == axis_index else 0 for i in range(self.dimension)))

                # check if we can move 'forward' in this dimension
                if self.ducks[d_index][axis_index] is not (self.size - 1):
                    directions.append(tuple(1 if i == axis_index else 0 for i in range(self.dimension)))
            
            move = random.choices(directions)[0]
            self.ducks[d_index] = [self.ducks[d_index][d] + move[d] for d in range(self.dimension)]


    def coincident(self):
        return all(d == self.ducks[0] for d in self.ducks)
    

    def trial(self, max_n=1000):
        self.reset()
        for i in range(max_n):
            self.step()
            if self.coincident():
                return i + 1
        return 0
    
def iterate(trials, size=3, num=2, dim=2, max_n=1000):
    g = Game(size, num, dim)

    total = 0
    for _ in range(trials):
        total += g.trial(max_n)

    return (total / trials)

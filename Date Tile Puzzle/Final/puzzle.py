#https://i.redd.it/hfm2esfo9b171.jpg

import numpy as np
from collections import deque


class Tile:
    __slots__ = ("shape", "transforms")

    def __init__(self, shape, transforms):
        self.shape = shape
        self.transforms = transforms


class ShapeIter:
    __slots__ = ("xy", "o", "xy_i", "o_i")

    def __init__(self, xy, o):
        self.xy = xy
        self.o = o

        self.xy_i = 0
        self.o_i = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.o_i += 1

        if self.o_i == len(self.o):
            self.o_i = 0
            self.xy_i += 1

            if self.xy_i == len(self.xy):
                raise StopIteration

        return (self.xy[self.xy_i], self.o[self.o_i])

    def reset(self, xy):
        self.xy = xy
        self.xy_i = 0
        self.o_i = 0


TRANSFORM = ( # D4 symmetry group
    np.array([[1, 0], [0, 1]]),   # rotation of 0
    np.array([[0, -1], [1, 0]]),  # rotation of 90
    np.array([[-1, 0], [0, -1]]), # rotation of 180
    np.array([[0, 1], [-1, 0]]),  # rotation of 270
    np.array([[1, 0], [0, -1]]),  # reflect across x
    np.array([[-1, 0], [0, 1]]),  # reflect across y
    np.array([[0, -1], [-1, 0]]), # reflect across main diag
    np.array([[0, 1], [1, 0]])    # reflect across other diag
)

TILE = (
    #               x-coordinates          y-coordinates          transformations
    Tile(np.array([[0, 1, 1, -1, -1],     [0, 0, 1, 0, -1]]),    (0, 1, 4, 6)),              # even Z
    Tile(np.array([[0, 1, 2, 0, 0],       [0, 0, 0, 1, 2]]),     (0, 1, 2, 3)),              # even L
    Tile(np.array([[0, 0, -1, 1, 2],      [0, 1, 0, 0, 0]]),     (0, 1, 2, 3, 4, 5, 6, 7)),  # flat T
    Tile(np.array([[0, 0, -2, -1, 1],     [0, 1, 0, 0, 1]]),     (0, 1, 2, 3, 4, 5, 6, 7)),  # uneven Z
    Tile(np.array([[0, 0, -1, -1, 1],     [0, 1, 0, 1, 0]]),     (0, 1, 2, 3, 4, 5, 6, 7)),  # 2x2 block + 1
    Tile(np.array([[0, -1, -1, 1, 1],     [0, 0, 1, 0, 1]]),     (0, 1, 2, 3)),              # U
    Tile(np.array([[0, -2, -1, 1, 1],     [0, 0, 0, 0, 1]]),     (0, 1, 2, 3, 4, 5, 6, 7)),  # uneven L
    Tile(np.array([[0, 0, -1, -1, 1, 1],  [0, 1, 0, 1, 0, 1]]),  (0, 1))                     # 2x3 block
)


def check_contiguous(grid):
    # Check two things: first, that there are no contiguous empty regions smaller than 5 squares
    # (since in that case, no tiles could fit), and second, that there is at least one contiguous 
    # empty region at least six tiles in size. The only 6-square tile is placed last, so unless 
    # the board is filled, there must be room for it.
    
    # algorithm: for each empty, unmarked square: mark it as visited, and traverse its empty, unmarked
    # neighbors, until there are no more, counting each. 'empty' deque holds tuples of (xy, region)
    # where 'region' is the identifier of the region that the square is a part of.

    offsets = [np.array([-1, 0]), np.array([1, 0]), np.array([0, -1]), np.array([0, 1])]

    regions = list() # list of integer region sizes
    marked = list() # list of tuples, each an (x, y) point
    empty = deque((xy, -1) for xy in np.argwhere(grid == 0))

    while empty:
        current = empty.popleft()

        if tuple(current[0]) in marked: # only need to check if marked for squares w/o region (others checked below)
            continue

        marked.append(tuple(current[0]))

        if current[1] == -1: # this is a new region
            region_num = len(regions)
            regions.append(1)

        else: # we are just continuing to explore an existing region
            region_num = current[1]
            regions[current[1]] += 1

        for off in offsets:
            new = current[0] + off
            # verify that new square to check is within bounds, empty, and unmarked
            if np.all(0 <= new) and np.all(new < 7) and not np.any(grid[new[0], new[1]]) and not tuple(new) in marked:
                empty.appendleft((new, region_num))

    return min(regions) >= 5 and max(regions) >= 6


def solve_date(month, day, find_all=False):
    # Set up base grid
    month -= 1
    day -= 1

    grid = np.full((7, 7), 0, dtype=np.int8)
    grid[0:2, 6] = -1
    grid[6, 3:7] = -1
    grid[(month // 6), (month % 6)] = -1
    grid[(day // 7 + 2), (day % 7)] = -1

    iterators = [ShapeIter(np.argwhere(grid == 0), TILE[i].transforms) for i in range(8)]

    current_index = 0
    while 0 <= current_index < 8:
        # Clear all points in the grid with the current index (+1)
        grid[grid == (current_index + 1)] = 0

        for (xy, o) in iterators[current_index]:
            shape = TRANSFORM[o] @ TILE[current_index].shape + xy.reshape(2,1)

            if np.all(0 <= shape) and np.all(shape < 7) and not np.any(grid[shape[0], shape[1]]):
                # all coords of transformed shape are within the grid and unoccupied (=> the shape fits)
                current_index += 1
                grid[shape[0], shape[1]] = current_index

                if current_index < 8:
                    # another check: does placing this shape leave any un-fillable areas?
                    # if so, remove it and continue searching this shape (instead of moving to the next)
                    if not check_contiguous(grid):
                        grid[grid == current_index] = 0
                        current_index -= 1
                        continue

                    # reset next iterator with new empty points
                    iterators[current_index].reset(np.argwhere(grid == 0))

                elif find_all:
                    print(grid)
                    grid[grid == current_index] = 0
                    current_index -= 1
                    continue
                
                break

        else: # tried all (xy, o) and none work
            current_index -= 1

    return grid


if __name__ == "__main__":
    import time
    start = time.perf_counter()
    print(solve_date(1, 22))
    print(time.perf_counter() - start)

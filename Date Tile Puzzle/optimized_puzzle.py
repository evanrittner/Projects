#https://i.redd.it/hfm2esfo9b171.jpg

import numpy as np


class Tile:
    def __init__(self, shape, transforms):
        self.shape = shape
        self.transforms = transforms


class ShapeIter:
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
    Tile(np.array([[0, 0, -1, -1, 1, 1],  [0, 1, 0, 1, 0, 1]]),  (0, 1)),                    # 2x3 block
    Tile(np.array([[0, 0, -2, -1, 1],     [0, 1, 0, 0, 1]]),     (0, 1, 2, 3, 4, 5, 6, 7)),  # uneven Z
    Tile(np.array([[0, 0, -1, -1, 1],     [0, 1, 0, 1, 0]]),     (0, 1, 2, 3, 4, 5, 6, 7)),  # 2x2 block + 1
    Tile(np.array([[0, -1, -1, 1, 1],     [0, 0, 1, 0, 1]]),     (0, 1, 2, 3)),              # U
    Tile(np.array([[0, -2, -1, 1, 1],     [0, 0, 0, 0, 1]]),     (0, 1, 2, 3, 4, 5, 6, 7))   # uneven L
)


def solve_date(month, day):
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
                    # reset next iterator with new empty points
                    iterators[current_index].reset(np.argwhere(grid == 0))
                
                break

        else: # tried all (xy, o) and none work
            current_index -= 1

    return grid


if __name__ == "__main__":
    import time
    start = time.perf_counter()
    print(solve_date(5, 29))
    print(time.perf_counter() - start)

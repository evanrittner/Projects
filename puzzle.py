#https://i.redd.it/hfm2esfo9b171.jpg

from itertools import product
import numpy as np

class Tile:
    def __init__(self, shape, transforms):
        self.shape = shape
        self.transforms = transforms

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


def base(month, day):
    assert (1 <= month <= 12) and (1 <= day <= 31)
    
    month -= 1
    day -= 1

    out = np.full((7, 7), 0)
    out[0:2, 6] = -1
    out[6, 3:7] = -1
    out[(month // 6), (month % 6)] = -1
    out[(day // 7 + 2), (day % 7)] = -1

    return out


def orientation(tile):
    for orientation, x, y in product(tile.transforms, range(7), range(7)):
        shape = TRANSFORM[orientation] @ tile.shape + np.array([[x], [y]])
        
        #check if all parts of the shape are within the edges
        if np.all(0 <= shape) and np.all(shape < 7):
            yield shape


def solve_date(month, day):
    reset = base(month, day)
    grid = reset.copy()

    for positions in product(*map(orientation, TILE)): 
        for index, position in enumerate(positions, 1):
            if np.any(grid[position[0], position[1]]): # if the location is not empty
                grid = reset.copy()
                break # this combination of positions will not work
            else:
                grid[position[0], position[1]] = index

        else: # made it through all 8 tiles w/o breaking -> finished
            return grid


if __name__ == "__main__":
    print(solve_date(5, 24))

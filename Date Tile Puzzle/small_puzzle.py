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
    Tile(np.array([[0, 0, -1], [0, -1, 0]]), (0, 1, 2, 3)), # short L
    Tile(np.array([[0, 0, 1, 2], [0, 1, 0, 0]]), (0, 1, 2, 3, 4, 5, 6, 7)), # long L
    Tile(np.array([[0, 0], [0, 1]]), (0, 1)) # 1x2 block
)

def orientation(tile):
    for orientation, x, y in product(tile.transforms, range(3), range(3)):
        shape = TRANSFORM[orientation] @ tile.shape + np.array([[x], [y]])
        
        #check if all parts of the shape are within the edges
        if np.all(0 <= shape) and np.all(shape < 3):
            yield shape


def solve():
    grid = np.full((3, 3), 0)

    for positions in product(*map(orientation, TILE)):
        for index, position in enumerate(positions, 1):
            if np.any(grid[position[0], position[1]]): # if the location is not empty
                grid[:, :] = 0 # reset grid
                break #this combination of positions will not work
            else:
                grid[position[0], position[1]] = index

                if index == 3:
                    return grid  # finished



if __name__ == "__main__":
    print(solve())

# Date Tile Puzzle

This project is based on [this image](Date%20Tile%20Puzzle/inspiration.jpg). As is the objective of the game, I wanted to solve the puzzle for evey day, plus the nonexistent ones, like February 31.

The output and most polished version of the scripts are in the directory `Final` (the rest of the files are tests and earlier drafts). `puzzle.py` contains the main logic to solve the puzzle for a given date; `make_img.py` takes the solution and creates the output images, and `main.py` coordinates the process, with multiprocessing, and basic logging. I ran this on a Raspberry Pi 3B+, which took a bit less than five hours to finish.

## Objective

For each date (of which there are 372: twelve months, 31 days), determine a way to place the eight tiles to solve the puzzle. Generate images (in two styles) to represent the solution.

## Solution

Brute-forcing this problem is actually infeasible. There are eight tiles, on a 7x7 grid, which leaves 49 possibilities for each, but the tiles can also be rotated and flipped. This increases the number of possible ways to place each tile by a factor of eight (the size of the group D4). This naiive solution would need to check a number of potential solutions on the order of `8^(7 * 7 * 8)`, which is approximately 10^345: too much, even for a relatively fast language like C++. (I tried using a bit of C++ in the solution to this problem, as I'm trying to learn it, but the speed it brought was offset by the fact that I am not very good at writing it. I stuck with a pure Python approach for the final solution, though heavily supported by the Numpy library, written primarily in C, for speed.)

My algorithm is as follows:

- Try to place the current shape (iterate through the open grid spaces, then the possible orientations).
- If it can be placed, make sure it doesn't create any small enclosed regions of open spaces that cannot be filled. If not, continue to the next shape.
- If none of the possible positions or orientations work, go back to the previous shape, and continue iterating through positions and orientations from where we left off.

To support being able to start iterating, then pausing and coming back, I wrote a simple `ShapeIter` class in `puzzle.py`, but besides that, the program is quite straightforward.

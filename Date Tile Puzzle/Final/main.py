import time
from itertools import product
import multiprocessing as mp

from puzzle import solve_date
from make_img import make_img


def run(date):
    month, day = date

    with open("date_puzzle_log.txt", "a", buffering=1) as log, open("grid_data.txt", "a", buffering=1) as data:
        
        start = time.time()

        log.write(f"\nStarting date {month}-{day} at {time.ctime(start)}\n")
        try:
            grid = solve_date(month, day)

            data.write(f"{month}-{day}\n")
            data.write(str(grid) + "\n")
            
        except:
            log.write(f"Error when processing {month}-{day} (duration {round(time.time() - start, 2)} sec). Continuing.\n")
            return

        if 0 in grid:
            log.write(f"Processing of {month}-{day} successful; no solution found. Duration {round(time.time() - start, 2)} sec.\n")
            return

        log.write(f"Processing of {month}-{day} successful; solution found. Duration {round(time.time() - start, 2)} sec. Proceeding to image generation.\n")

        try:
            make_img(grid, month, day)
        except:
            log.write(f"Error when creating image.\n")
        else:
            log.write(f"Image successfully created.\n")


if __name__ == "__main__":
    with mp.Pool(processes=4) as pool:
        pool.map(run, product(range(1, 13), range(1, 32)))

    with open("date_puzzle_log.txt", "a", buffering=1) as log:
        log.write(f"All dates complete (finished at {time.ctime(time.time())}).")

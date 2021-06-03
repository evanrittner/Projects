# resilient program to compute grid arrangements for all possible month-date 
# combinations (1-12, 1-31; incl Feb 31 etc)
#
# for each date, compute solution (or determine there is none), then render as 
# an image, and save it
#
# log progress and duration (after each date), and log errors (recover; if a
# run fails for whatever reason, skip to the next, but keep going)
#
# maybe send me a text with any errors, or when it's done (or milestones?)
#
# to be run on a raspberry pi

import time
from itertools import product

from optimized_puzzle import solve_date
from make_img import make_img
from send_text import Texter


with Texter() as text, open("date_puzzle_log.txt", "a", buffering=1) as log, open("grid_data.txt",  "a", buffering=1) as data:
    for (month, day) in product(range(1, 13), range(1, 32)):
        if month == 1 and day in range(1, 29):
            continue

        if day == 1:
            text.send(f"Starting month {month}")

        start = time.time()
        
        log.write(f"\nStarting date {month}-{day} at {time.ctime(start)}\n")
        try:
            grid = solve_date(month, day)

            data.write(f"{month}-{day}\n")
            data.write(str(grid) + "\n")
            
        except:
            log.write(f"Error when processing (duration {round(time.time() - start, 2)} sec). Continuing.\n")
            continue

        if 0 in grid:
            log.write(f"Processing successful; no solution found. Duration {round(time.time() - start, 2)} sec.\n")
            continue

        log.write(f"Processing succesful; solution found. Duration {round(time.time() - start, 2)} sec. Proceeding to image generation.\n")

        try:
            make_img(grid, month, day)
        except:
            log.write(f"Error when creating image.\n")
        else:
            log.write(f"Image successfully created.\n")

    log.write("All dates complete.\n")
    text.send("All dates complete")

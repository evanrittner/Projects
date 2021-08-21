# Script to run gen_array processes for multiple values of sigma

import os
import subprocess
from concurrent.futures import ProcessPoolExecutor


def task(num):
    subprocess.run(["./gen_array.out", f"{int(100 * num):03}.npy", str(num), "1000", "2000", "3000", "3000"])


if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=4) as executor:
        executor.map(task, [i / 100 for i in range(11, 26)])

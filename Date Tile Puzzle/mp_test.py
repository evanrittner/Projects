import multiprocessing as mp
import time

def f(x):
    time.sleep(0.1 * x)
    return x * x

if __name__ == "__main__":
    with mp.Pool(processes=4) as pool:
        start = time.perf_counter()
        for res in pool.map(f, range(25)):
            print(res)
        print(time.perf_counter() - start)

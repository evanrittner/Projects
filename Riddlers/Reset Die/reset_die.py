from itertools import product
import numpy as np


def partition(n):
    """Generate partitions of n"""
    yield [n]
    for i in range(n-1, 0, -1):
        for p in partition(n - i):
            if max(p) <= i:
                yield [i] + p


def freq_to_nums(freqs):
    """Go from a frequency representation (i.e. [3,2,1]) to a possible literal representation (i.e. [1,1,1,2,2,3])"""
    f = freqs.copy()
    i = 0
    while sum(f) > 0:
        if f[i] > 0:
            f[i] -= 1
            yield i + 1
        else:
            i += 1


def nums_to_freq(nums):
    """Go from a literal representation (i.e. [1,1,1,2,2,3]) to a frequency
    representation (i.e. [3,2,1]). In other words, return the count of each number."""
    counts = [nums.count(n) for n in set(nums)]
    return sorted(counts, reverse=True)


def direct_freqs(state, finals):
    """Return a list of probablities of transitioning (in one roll) from the given state to each state in finals"""
    nums = list(freq_to_nums(state))
    all_combs = product(nums, repeat=len(nums)) # all possible outcomes of rolling from the given state
    totals = [0] * len(finals)
    
    # go through each possible outcome, and categorize it into which final state it is
    for c in all_combs: 
        for final_i in range(len(finals)):
            if nums_to_freq(c) == finals[final_i]:
                totals[final_i] += 1
                break
    
    return [t / (sum(state) ** sum(state)) for t in totals] # divide by sum(state) ** sum(state) = n**n = len(all_combs)


def steps(n):
    """Solve for the solution: the average number of rolls from a normal die to a uniform one"""
    states = sorted(list(partition(n))) #states is a list of frequency representations
    M = np.array([direct_freqs(s, states) for s in states])
    t = np.linalg.inv(np.eye(len(states) - 1) - M[:-1, :-1]).sum(1) #i.e. t = (I - Q)^-1 * 1
    return t[0]



if __name__ == "__main__":
    print(steps(6))

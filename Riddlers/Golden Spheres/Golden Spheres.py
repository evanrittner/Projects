#https://fivethirtyeight.com/features/can-you-flip-the-magic-coin/


def d(subs):
        a = [sum(t) for t in subs]
        return max(a) - min(a)


def cga(subsets, vals, b_d, k):
        #Rule 1: finished a branch
        if not vals:
            diff = d(subsets)
            if diff < b_d:
                best = subsets
                b_d = diff
                if diff == 0:
                    return True
            return False
        
        #Rule 2
        t = sum(vals)
        s = max([sum(ss) for ss in subsets])
        if s - ((t - s)/(k - 1)) >= b_d:
            return False
        
        #Rule 3: recursion
        subs_sums = {sum(subsets[i]):i for i in range(k)} # [[3,2],[1,6],[5]] -> {5:0,7:1,5:3}
        for ss in sorted(list(set(subs_sums.keys()))): #(from above) ss=5; ss=7
            index = subs_sums[ss]
            new_subs = [subsets[index] + [vals[-1]]] + [subsets[(index + i)%k] for i in range(1,k)]
            if cga(new_subs,vals[:-1]):
                return True
        return False


def kpartition(values, k=3):
    values.sort()
    best = list()
    b_d = sum(values)
    
    cga([list() for _ in range(k)], values, b_d, k)
    return b_d,best


def find_soln(k=3):
    n = k + 1
    while True:
        soln = kpartition([i**4 for i in range(1, n)], k)
        if not soln[0]:
            return soln[1]
        else:
            n += 1

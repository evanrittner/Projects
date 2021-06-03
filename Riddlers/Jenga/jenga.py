#https://fivethirtyeight.com/features/can-you-win-riddler-jenga/

from random import random

class Jenga:
    def __init__(self, stack=None):
        if stack:
            self.stack = stack
        else:
            self.stack = [0.0]

    def add_block(self):
        self.stack.append(self.stack[-1] + random() - 0.5)

    def check(self):
        for base_i in range(len(self.stack) - 1):
            com = sum(self.stack[i] for i in range(base_i + 1, len(self.stack))) / (len(self.stack) - base_i - 1)
            if abs(self.stack[base_i] - com) > 0.5:
                return base_i
        else:
            return None

    @staticmethod
    def trial():
        i = 1
        j = Jenga()
        while j.check() is None:
            i += 1
            j.add_block()
        return i

    @staticmethod
    def many(n=1000):
        return sum(Jenga.trial() for _ in range(n)) / n

    @staticmethod
    def plot(block_height=0.3):
        import matplotlib.pyplot as plt
        from matplotlib.collections import PatchCollection
        from matplotlib.patches import Rectangle

        j = Jenga()
        while j.check() is None:
            j.add_block()
        tipping_point = j.check()   

        patches = list()
        for i in range(len(j.stack)):
            fc = "#a0a0a0" if i <= tipping_point else "#ff4d4d"
            patches.append(Rectangle((j.stack[i] - 0.5, i * block_height), 1, block_height, edgecolor="#000000", facecolor=fc))
        pc = PatchCollection(patches, match_original=True)

        fig, ax = plt.subplots()
        ax.axis(False)
        ax.axis("equal")
        xlim = max(map(abs, j.stack)) + 0.5
        ax.set_xlim((-xlim, xlim))
        ax.set_ylim((-0.75, len(j.stack) * block_height + 0.5))
        ax.plot([-xlim, xlim], [0, 0], color="k")

        ax.add_collection(pc)
        ax.annotate(str(len(j.stack)), (0, -0.3), fontsize="xx-large", fontweight="semibold")
        plt.show()

if __name__ == "__main__":
    for _ in range(3):
        Jenga.plot()

    print("The average number of blocks (based on 1000 trials) is", Jenga.many())

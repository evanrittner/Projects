import numpy as np
import matplotlib.pyplot as plt

from .veinte import eval_round

MAX = 1000

ary = np.empty((MAX, MAX))

for i in range(1, MAX + 1):
    data = np.array(eval_round(i), dtype=np.float64)

    if i == 1:
        ary[i - 1][0] = 255
        ary[i - 1][1:] = 0

    else:
        data *= 255 / (i - 1)
        ary[i - 1][:i] = data
        ary[i - 1][i:] = 0


ax = plt.subplot()
ax.imshow(ary, cmap='gray', vmin=0, vmax=255)
plt.axis("off")

plt.show()

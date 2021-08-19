import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

plt.rcParams["contour.negative_linestyle"] = "solid"

# Command line args: input filepath, output filepath, contour interval
assert len(sys.argv) == 4

Z = np.load(sys.argv[1])[::-1]
interval = float(sys.argv[3])

Z = gaussian_filter(Z, 10)

fig, ax = plt.subplots()

ax.imshow(Z, cmap="magma")
ax.contour(Z, np.arange(interval, np.max(Z) + interval, interval), colors="w", linewidths=0.25)

plt.axis("off")
plt.tight_layout()

plt.savefig(sys.argv[2], dpi=Z.shape[0]/4.5, bbox_inches="tight", pad_inches=0)

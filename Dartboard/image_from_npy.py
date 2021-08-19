import numpy as np
from math import floor
from matplotlib import cm
from PIL import Image


magma = cm.get_cmap("magma")
cmap = [np.array([min(255, floor(256 * rgba)) for rgba in magma(i)], dtype=np.uint8) for i in range(256)]


def gen_img(infp, outfp=None, resize=None):
    ary = np.load(infp)[::-1]
    ary /= np.max(ary)

    new = np.empty(ary.shape + (4,), np.uint8)

    for r in range(ary.shape[0]):
        for c in range(ary.shape[1]):
            new[r][c] = cmap[min(255, floor(256 * ary[r][c]))]

    if not outfp:
        outfp = infp[:-4] + ".png"
    
    if isinstance(resize, str):
        resize = int(resize)

    if resize:
        Image.fromarray(new).resize((resize, resize), Image.LANCZOS).save(outfp)
    else:
        Image.fromarray(new).save(outfp)


def process_all():
    import os

    for infp in os.listdir(r"Dartboard\data"):
        gen_img("Dartboard\\data\\" + infp, outfp=rf"Dartboard\images\{infp[:-4]}.png")


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        process_all()
    
    else:
        gen_img(*sys.argv[1:])

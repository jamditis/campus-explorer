"""Average sub-frames into one frame (motion blur), then delete the sub-frames.

    python3 tools/teaser/blend.py OUT.png SUB0.png SUB1.png ...
"""

import os
import sys

import numpy as np
from PIL import Image


def main(dst, srcs):
    acc = None
    for s in srcs:
        a = np.asarray(Image.open(s).convert("RGB"), dtype=np.float32)
        acc = a if acc is None else acc + a
    img = Image.fromarray(np.clip(acc / len(srcs) + 0.5, 0, 255).astype(np.uint8))
    tmp = dst + ".tmp.png"
    img.save(tmp)
    os.replace(tmp, dst)
    for s in srcs:
        os.remove(s)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])

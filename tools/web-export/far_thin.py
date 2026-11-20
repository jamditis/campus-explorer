"""Thin the far-field trees (far_trees.bin, from landcover.py) with distance from the campus centre.

A crown narrower than PX pixels (at the walk view's 68 degree field of view on a 1080 px screen) is grown to
that width, and only the share (old radius / new radius)^2 of such trees is kept, chosen by a hash of the
position: the covered area stays about the same and each far crown still reads as one small blob. With 4 px
that starts at about 1.7 km for a crown of the median 3.8 m radius. Fog (look.js) still leaves 56 % at the
skirt's corners, so nothing is dropped for fog. A second run changes nothing (kept crowns are already wide
enough), so build_web.sh runs it after every landcover run and on the published file.
  python3 far_thin.py FILE [PX]
Rows are float32 [x, y, z, crown radius, height] in three.js axes; trees.js draws a crown of radius r centred
h - 1.1 r over its ground point, 2.3 r tall, so a crown never grows past MAX_R_OF_H times the height.
"""
import math
import struct
import sys
import zlib

MAX_R_OF_H = 0.44


def keep_share(x, z):
    """A number in [0, 1) fixed by the position (centimetres), the same on every run."""
    return zlib.crc32(struct.pack("<ii", round(x * 100), round(z * 100))) / 2**32


def thin(trees, px=4.0, fov_deg=68.0, screen_px=1080):
    """The trees (x, y, z, r, h) after thinning; near trees and wide crowns are returned unchanged."""
    ang = px * math.radians(fov_deg / screen_px)
    out = []
    for x, y, z, r, h in trees:
        s = min(math.hypot(x, z) * ang / 2, MAX_R_OF_H * h)
        if r >= s * (1 - 1e-5):  # wide enough already (float32 rounding of an earlier run's radius)
            out.append((x, y, z, r, h))
        elif keep_share(x, z) < (r / s) ** 2:
            out.append((x, y, z, s, h))
    return out


def main(path, px=4.0):
    data = open(path, "rb").read()
    n = len(data) // 20
    trees = [struct.unpack_from("<5f", data, i * 20) for i in range(n)]
    kept = thin(trees, px)
    with open(path, "wb") as f:
        for t in kept:
            f.write(struct.pack("<5f", *t))
    print(f"far_thin {path}: {n} -> {len(kept)} trees")


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 4.0)

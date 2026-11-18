"""Compose the lot-marking paint layers for the viewer.

The Blender asphalt materials paint stall lines, accessible bays and crosswalk bars from
world-XY image tiles (data/<prefix>_mask_tiles.json: [file, x0, x1, y0, y1]; red = white paint,
green = accessible blue). The browser cannot run those node trees, so each prefix used by the
exported materials becomes one RGBA image (RGB = paint colour, A = coverage) at 2.5 cm/px,
written as <out>/paint_<prefix>.webp and listed in paint.json with its world bounds.
These images are our own authored line work, not imagery.
env: WORK (raw *.paint.json), OUT (models/<scene>), DATA (mask tile folder)
"""

import glob
import json
import os

import numpy as np
from PIL import Image

WORK = os.environ.get("WORK", "/workspace/nj-scenes/web/build/main")
OUT = os.environ.get("OUT", "/workspace/nj-scenes/web/campus/models/main")
DATA = os.environ.get("DATA", "/workspace/nj-scenes/montclair-state/data")
RES = 0.025
WHITE = (0.75, 0.75, 0.72)
BLUE = (0.02, 0.12, 0.45)

prefixes = set()
for f in glob.glob(WORK + "/raw/*.paint.json"):
    prefixes.update(json.load(open(f)))
layers = []
for old in glob.glob(OUT + "/paint_*.webp"):
    os.remove(old)
for pre in sorted(prefixes):
    tj = f"{DATA}/{pre}_mask_tiles.json"
    if not os.path.exists(tj):
        print("paint: no tile list for", pre)
        continue
    tiles = json.load(open(tj))
    x0 = min(t[1] for t in tiles)
    x1 = max(t[2] for t in tiles)
    y0 = min(t[3] for t in tiles)
    y1 = max(t[4] for t in tiles)
    w = int(np.ceil((x1 - x0) / RES))
    h = int(np.ceil((y1 - y0) / RES))
    r = np.zeros((h, w), np.float32)
    g = np.zeros((h, w), np.float32)
    for name, tx0, tx1, ty0, ty1 in tiles:
        im = Image.open(f"{DATA}/{name}").convert("RGB")
        pw = max(1, round((tx1 - tx0) / RES))
        ph = max(1, round((ty1 - ty0) / RES))
        a = np.asarray(im.resize((pw, ph), Image.BILINEAR), np.float32) / 255.0
        a = a[::-1]  # image row 0 is the tile's max-Y edge in Blender's UV convention
        c0 = int(round((tx0 - x0) / RES))
        r0 = int(round((ty0 - y0) / RES))
        sl = (slice(r0, r0 + ph), slice(c0, c0 + pw))
        hh, ww = r[sl].shape
        r[sl] = np.maximum(r[sl], a[:hh, :ww, 0])
        g[sl] = np.maximum(g[sl], a[:hh, :ww, 1])
    fw = np.clip((r - 0.3) / 0.4, 0, 1) * 0.92
    fb = np.clip((g - 0.3) / 0.4, 0, 1) * 0.9
    alpha = np.maximum(fw, fb)
    rgb = np.zeros((h, w, 3), np.float32)
    for i in range(3):
        rgb[..., i] = np.where(fw >= fb, WHITE[i], BLUE[i])
    srgb = np.where(rgb <= 0.0031308, rgb * 12.92, 1.055 * rgb ** (1 / 2.4) - 0.055)
    img = np.dstack([srgb, alpha]) * 255
    img = img[::-1]  # row 0 = max-Y (north) so the viewer maps v = (y - y0) / (y1 - y0) with flipY
    fn = f"paint_{pre}.webp"
    Image.fromarray(img.astype(np.uint8), "RGBA").save(f"{OUT}/{fn}", lossless=True)
    layers.append(dict(file=fn, x0=x0, x1=x1, y0=y0, y1=y1))
    print("paint", fn, w, h, os.path.getsize(f"{OUT}/{fn}"))
json.dump(layers, open(OUT + "/paint.json", "w"), indent=1)

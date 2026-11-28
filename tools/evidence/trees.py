"""Find single trees in the LiDAR canopy and write them as a plan zone file of tree points.

usage: python3 tools/evidence/trees.py NAME AREA_DIR ZONE [--min-height 5] [--existing DUMP_DIR]
NAME is the evidence folder under DATA (default /workspace/data) with lidar.npz and ortho2020.png
(tools/evidence/fetch.py). AREA_DIR is the area's plan folder (blender/scripted/<area>): trees are
kept inside its footprint, outside its buildings, stands and paving, outside the buildings
OpenStreetMap maps there (NAME/osm.json), and away from its towers.
Writes AREA_DIR/ZONE.json. With --existing (a dump of the published tiles made by dump_tiles.mjs
with instances) a tree is left out where another source model already has one.

What is measured: the position of each canopy peak (0.5 m cells) and its height above the ground.
What is not: the species. A peak that is green in the leaf-off 2020 ortho and returns as a
solid crown is called a conifer; the others get a deciduous species by turn, so a wood is not
one repeated tree. Every tree is UNVERIFIED for species and crown shape.
"""

import json
import os
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "blender" / "scripted"))

import geom  # noqa: E402
import layout  # noqa: E402

DECIDUOUS = ["red_maple", "pin_oak", "sugar_maple", "tulip_poplar", "american_beech", "sweetgum"]
PAVED = {"asphalt", "concrete", "brick", "turf", "water"}  # no tree stands on these


def fill(grid):
    """Fill the NaN cells of a grid from their neighbours, ring by ring."""
    g = grid.copy()
    for _ in range(400):
        nan = np.isnan(g)
        if not nan.any():
            break
        p = np.pad(g, 1, constant_values=np.nan)
        stack = np.stack(
            [p[1 + dj : p.shape[0] - 1 + dj, 1 + di : p.shape[1] - 1 + di]
             for dj in (-1, 0, 1) for di in (-1, 0, 1)]
        )  # fmt: skip
        ok = ~np.isnan(stack)
        mean = np.where(ok, stack, 0).sum(0) / np.maximum(ok.sum(0), 1)
        g[nan & ok.any(0)] = mean[nan & ok.any(0)]
    return g


def window_max(a, r):
    """Maximum over a (2r+1) square window."""
    p = np.pad(a, r, constant_values=-np.inf)
    out = np.full(a.shape, -np.inf)
    for dj in range(2 * r + 1):
        for di in range(2 * r + 1):
            out = np.maximum(out, p[dj : dj + a.shape[0], di : di + a.shape[1]])
    return out


def window_mean(a, r):
    p = np.pad(a, r, mode="edge")
    out = np.zeros(a.shape)
    for dj in range(2 * r + 1):
        for di in range(2 * r + 1):
            out += p[dj : dj + a.shape[0], di : di + a.shape[1]]
    return out / (2 * r + 1) ** 2


def peaks(height, cell, min_height=5.0, coarse=2.0):
    """Canopy peaks of a height-above-ground grid: [(row, col, height)], tallest first.

    The survey was flown leaf-off, so a crown is a scatter of returns, not a surface: the grid is
    first reduced to `coarse` metre cells holding their highest return. A peak is the highest
    coarse cell among its neighbours, with a crown round it: at least three of its eight
    neighbours stand above 0.4 of its height (a lamp or a pole has none). Peaks closer
    than 0.22 of the taller one's height (3.5 m at least) are one tree. Row and column are of
    the highest fine cell in the peak.
    """
    f = max(1, round(coarse / cell))
    h = np.where(np.isfinite(height) & (height < 45), height, 0.0)
    rows, cols = h.shape[0] // f, h.shape[1] // f
    blocks = h[: rows * f, : cols * f].reshape(rows, f, cols, f)
    canopy = blocks.max((1, 3))
    top = (canopy >= window_max(canopy, 1) - 1e-9) & (canopy >= min_height)
    near = np.pad(canopy, 1)
    crown = sum(
        (near[1 + dj : rows + 1 + dj, 1 + di : cols + 1 + di] > 0.4 * canopy).astype(int)
        for dj in (-1, 0, 1)
        for di in (-1, 0, 1)
        if (dj, di) != (0, 0)
    )
    cand = sorted(
        ((float(canopy[j, i]), j, i) for j, i in zip(*np.nonzero(top & (crown >= 3)), strict=True)),
        reverse=True,
    )
    kept = []
    for z, j, i in cand:
        gap = max(3.5, 0.22 * z) / coarse
        if all((j - kj) ** 2 + (i - ki) ** 2 >= gap**2 for kj, ki, _kz in kept):
            kept.append((j, i, z))
    out = []
    for j, i, z in kept:
        dj, di = np.unravel_index(np.argmax(blocks[j, :, i, :]), (f, f))
        out.append((j * f + int(dj), i * f + int(di), z))
    return out


GRID = 3.0  # cell of the map of trees the published model already has, metres


def is_vegetation(name):
    """Is a mesh of the published tiles a tree or a shrub, by its name? "tree" must start a word:
    the tiles have asphalt meshes named `..._streets_...`.
    """
    return bool(re.search(r"(?i)(?<![a-z])tree|crown|shrub", name))


def existing(dump):
    """Cells (GRID metres) that hold a tree of the published tiles, from a dump made by
    tools/evidence/dump_tiles.mjs WITH instances (tiles.json, tiles.bin).
    """
    meta = json.loads((dump / "tiles.json").read_text())
    tri = np.fromfile(dump / "tiles.bin", dtype=np.float32).reshape(-1, 9)
    cells = set()
    for e in meta["entries"]:
        if not is_vegetation(e["mesh"] + " " + e.get("node", "")):
            continue
        t = tri[e["offset"] : e["offset"] + e["tris"]]
        cx = (t[:, [0, 3, 6]].mean(1) // GRID).astype(int)
        cy = (t[:, [1, 4, 7]].mean(1) // GRID).astype(int)
        cells.update(zip(cx.tolist(), cy.tolist(), strict=True))
    return cells


def on_surface(surfaces, x, y):
    """Whether (x, y) lies on one of `surfaces` (plan surfaces as layout.load gives them): inside
    its ring and in none of its holes. A hole in a pond's water is a hummock a tree stands on."""
    return any(
        geom.inside(s["ring"], x, y) and not any(geom.inside(h, x, y) for h in s.get("holes", []))
        for s in surfaces
    )


def mapped_buildings(osm):
    """Outlines [(x, y), ...] of the buildings in an OpenStreetMap extract made by fetch.py. A
    building of another source model inside the area returns like a crown and is not in the plan:
    no tree stands on a mapped roof.
    """
    at = {e["id"]: (e["x"], e["y"]) for e in osm["elements"] if e["type"] == "node" and "x" in e}
    rings = []
    for e in osm["elements"]:
        if e["type"] == "way" and "building" in e.get("tags", {}):
            ring = [at[n] for n in e["nodes"] if n in at]
            if len(ring) >= 4 and ring[0] == ring[-1]:
                rings.append(ring[:-1])
    return rings


def main():
    args = sys.argv[1:]
    name, area, zone = args[0], Path(args[1]), args[2]
    min_height = float(args[args.index("--min-height") + 1]) if "--min-height" in args else 5.0
    data = Path(os.environ.get("DATA", "/workspace/data")) / name
    d = np.load(data / "lidar.npz")
    x0, _y0, _x1, y1, cell = (float(v) for v in d["box"])
    height = d["dsm"] - fill(d["ground"])
    lay = layout.load(area)
    keep_out = [geom.offset(_ccw(geom.expand(b["ring"], True)), -2.5, True)
                for b in lay["buildings"] + lay["stands"]]  # fmt: skip
    on = [s for s in lay["surfaces"] if s["kind"] in PAVED]
    if (data / "osm.json").exists():
        osm = json.loads((data / "osm.json").read_text())
        # the same 2.5 m margin as the plan's own buildings: a roof edge leans in the survey
        keep_out += [geom.offset(_ccw(r), -2.5, True) for r in mapped_buildings(osm)]
    # a lattice tower returns like a tall crown: no trees within 9 m of one
    towers = [q["at"] for q in lay["points"] if q["kind"] in ("pylon", "mast")]
    taken = existing(Path(args[args.index("--existing") + 1])) if "--existing" in args else set()
    meta = json.loads((data / "ortho2020.json").read_text())
    ortho = np.asarray(Image.open(data / "ortho2020.png").convert("RGB")).astype(float)
    points = []
    for j, i, z in peaks(height, cell, min_height):
        # test the position that is written: a tree 2 cm outside paving rounded to 4 cm inside it
        x, y = round(x0 + (i + 0.5) * cell, 1), round(y1 - (j + 0.5) * cell, 1)
        if not geom.inside(lay["footprint"], x, y) or any(geom.inside(r, x, y) for r in keep_out):
            continue
        if on_surface(on, x, y):
            continue
        if any((x - t[0]) ** 2 + (y - t[1]) ** 2 < 81 for t in towers):
            continue
        cx, cy = int(x // GRID), int(y // GRID)
        if any((cx + dx, cy + dy) in taken for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            continue  # another source model already has a tree here
        # leaf-off image: a green crown is a conifer
        pi, pj = int((x - meta["x0"]) / meta["mpp"]), int((meta["y1"] - y) / meta["mpp"])
        k = max(1, round(1.2 / meta["mpp"]))
        r, g, b = ortho[max(0, pj - k) : pj + k + 1, max(0, pi - k) : pi + k + 1].mean((0, 1))
        # ... and a solid one: a bare crown over a green lawn is green in the image too, but its
        # returns are a scatter, while an evergreen crown returns from most cells
        w = max(1, round(2.0 / cell))
        win = height[max(0, j - w) : j + w + 1, max(0, i - w) : i + w + 1]
        solid = float((np.nan_to_num(win) > 0.4 * z).mean())
        conifer = g > 1.06 * r and g > 1.12 * b and solid >= 0.45
        # a tree in a pond (on a hummock, a hole in the water) is seen against the water, which
        # tints the leaf-off crown green: no conifer call there (the ponds' swamp trees read as
        # pale, early-leafing crowns, not as evergreen ones)
        conifer = conifer and not any(
            s["kind"] == "water" and geom.inside(s["ring"], x, y) for s in on
        )
        n = len(points)
        points.append(
            dict(
                name=f"Tree_{n + 1:03d}",
                kind="tree",
                at=[round(x, 1), round(y, 1)],
                height=round(z, 1),
                species="white_pine" if conifer else DECIDUOUS[n % len(DECIDUOUS)],
                evidence="lidar canopy peak",
                unverified="species; crown shape",
            )
        )
    out = dict(
        zone=zone,
        notes="Written by tools/evidence/trees.py from the LiDAR canopy: positions and heights are "
        "measured, species are not (see that file). Do not edit by hand; run the tool again.",
        points=points,
    )
    (area / f"{zone}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(len(points), "trees in", area / f"{zone}.json")


def _ccw(ring):
    return ring if geom.area(ring) > 0 else ring[::-1]


if __name__ == "__main__":
    main()

"""Letter outlines for the teaser's 3D type, from a font file on the machine.

    PYTHONPATH=<folder with fontTools> python3 tools/teaser/font.py FONT.otf OUT.json

Writes, per character, the advance and its shapes (outer outline counter-clockwise, holes clockwise,
y up, in em units: 1.0 = font size), curves flattened to straight runs. Kerning pairs from the font's
`kern` feature are not read; the type is set with plain advances.
"""

import json
import sys

CHARS = (
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    " .,:;-–·/()&'’%+×km"
)
STEPS = 6  # straight runs per curve segment


def area(pts):
    """Signed area of a closed polygon (positive when counter-clockwise)."""
    return 0.5 * sum(
        pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
        for i in range(len(pts))
    )


def inside(p, poly):
    """Even-odd test of point p against a closed polygon."""
    x, y = p
    hit = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[i - 1]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit


def group(contours):
    """Sort contours into shapes: even nesting depth is an outline, odd is a hole of its parent."""
    contours = [c for c in contours if len(c) >= 3 and abs(area(c)) > 1e-6]
    depth = [sum(inside(c[0], o) for j, o in enumerate(contours) if j != i)
             for i, c in enumerate(contours)]
    shapes = []
    for i, c in enumerate(contours):
        if depth[i] % 2:
            continue
        outer = c if area(c) > 0 else c[::-1]
        holes = []
        for j, h in enumerate(contours):
            if depth[j] == depth[i] + 1 and inside(h[0], c):
                holes.append(h if area(h) < 0 else h[::-1])
        shapes.append({"outer": outer, "holes": holes})
    return shapes


def flatten(ops, scale):
    """Recorded pen operations to closed point lists."""
    out, cur, pos = [], [], (0.0, 0.0)

    def add(p):
        cur.append([round(p[0] * scale, 5), round(p[1] * scale, 5)])

    for op, args in ops:
        if op == "moveTo":
            if cur:
                out.append(cur)
            cur = []
            pos = args[0]
            add(pos)
        elif op == "lineTo":
            pos = args[0]
            add(pos)
        elif op == "curveTo":  # cubic, possibly with several off-curve points: split as pairs
            pts = list(args)
            while len(pts) >= 3:
                (c1, c2, end), pts = pts[:3], pts[3:]
                for k in range(1, STEPS + 1):
                    t = k / STEPS
                    u = 1 - t
                    add([u**3 * pos[i] + 3 * u * u * t * c1[i] + 3 * u * t * t * c2[i]
                         + t**3 * end[i] for i in (0, 1)])
                pos = end
        elif op == "qCurveTo":
            pts = list(args)
            end = pts[-1]
            offs = pts[:-1]
            for n, c in enumerate(offs):
                e = end if n == len(offs) - 1 else [(c[i] + offs[n + 1][i]) / 2 for i in (0, 1)]
                for k in range(1, STEPS + 1):
                    t = k / STEPS
                    u = 1 - t
                    add([u * u * pos[i] + 2 * u * t * c[i] + t * t * e[i] for i in (0, 1)])
                pos = e
        elif op in ("closePath", "endPath"):
            if cur:
                if len(cur) > 1 and cur[0] == cur[-1]:
                    cur.pop()
                out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def main(src, dst):
    from fontTools.pens.recordingPen import RecordingPen
    from fontTools.ttLib import TTFont

    font = TTFont(src)
    scale = 1 / font["head"].unitsPerEm
    cmap, glyphs, hmtx = font.getBestCmap(), font.getGlyphSet(), font["hmtx"]
    out = {"source": src, "ascender": font["hhea"].ascent * scale, "glyphs": {}}
    for ch in CHARS:
        name = cmap.get(ord(ch))
        if not name:
            continue
        pen = RecordingPen()
        glyphs[name].draw(pen)
        out["glyphs"][ch] = {
            "adv": round(hmtx[name][0] * scale, 5),
            "shapes": group(flatten(pen.value, scale)),
        }
    with open(dst, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"{len(out['glyphs'])} glyphs -> {dst}")


if __name__ == "__main__":
    main(*sys.argv[1:3])

"""Interiors from a plan's `interiors` list (see rooms.py and <area>/interior.json): partitions,
glazed partitions, slabs, stair and lift blocks and piers, one object per floor and kind.

Colours are neutral (white walls, grey floors): the source is a floor plan, which gives no
finishes. Every object is UNVERIFIED (positions from a sign plan, heights not on it).
"""

import kit
import rooms

WALL = ("plaster", "interior_wall", "#ebe9e4", 0.9)
GLASS = ("glass", "interior_partition", "#9fb3bd", 0.05)
SLAB = ("concrete", "interior_floor", "#a4a4a0", 0.8)
BLOCK = {"stair": ("concrete", "interior_stair", "#b8b6b0", 0.85), "lift": WALL}


def _mat(spec):
    kind, name, colour, rough = spec
    return kit.mat(kind, name, kit.srgb(colour), rough=rough)


def _add(builder, verts, faces, material):
    builder.faces(verts, [tuple(f) for f in faces], material)


def floor(f):
    """Objects of one floor: {"walls", "slabs", "blocks", "solids", ...} as rooms.py reads them."""
    keep = [k["ring"] for k in f["keep_out"]]
    out = []
    groups = {
        "walls": [w for w in f["walls"] if not w.get("glazed")],
        "glazing": [w for w in f["walls"] if w.get("glazed")],
    }
    for kind, runs in groups.items():
        if not runs:
            continue
        b = kit.Builder(f"SW_{f['name']}_{kind}_UNVERIFIED")
        m = _mat(GLASS if kind == "glazing" else WALL)
        for run in runs:
            for piece in rooms.run_pieces(run, f["floor"], f["ceiling"], keep, f["inside"]):
                _add(b, *rooms.box_mesh(rooms.box(piece)), m)
        if b.mats:
            out.append(b.finish(recalc=False))
    for s in f["slabs"]:
        b = kit.Builder(s["name"])
        _add(b, *rooms.prism(s["ring"], s["z0"], s["z1"]), _mat(SLAB))
        out.append(b.finish(recalc=False))
    for s in f["blocks"]:
        b = kit.Builder(s["name"])
        _add(b, *rooms.prism(s["ring"], s["z0"], s["z1"]), _mat(BLOCK[s["kind"]]))
        out.append(b.finish(recalc=False))
    if f["solids"]:
        b = kit.Builder(f"SW_{f['name']}_piers_UNVERIFIED")
        for s in f["solids"]:
            _add(b, *rooms.prism(s["ring"], f["floor"], f["ceiling"]), _mat(WALL))
        out.append(b.finish(recalc=False))
    return out


def build(lay):
    """Every interior of the area's plan."""
    return [ob for f in lay.get("interiors", []) for ob in floor(f)]

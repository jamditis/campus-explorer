"""Load the plan files and work out what the builders share: dense outlines, layers, paint sheets.

Pure Python (no bpy, no numpy), so `paint.py` (system Python) and `ground.py` (Blender) see the same
layout.
"""

import json
from pathlib import Path

import geom

LAYER = {"lawn": 0, "mulch": 1, "gravel": 2, "asphalt": 3, "turf": 4, "concrete": 5, "brick": 6}
YD = 0.9144
PAINTABLE = {"asphalt", "concrete", "brick", "turf"}


def load(plan_dir):
    """Merge every plan/*.json (sorted by name) into one layout dict."""
    out = dict(
        footprint=None,
        surfaces=[],
        curbs=[],
        markings=[],
        points=[],
        stands=[],
        fences=[],
        buildings=[],
        lifts=[],
        field_frame=None,
    )
    for f in sorted(Path(plan_dir).glob("*.json")):
        if f.name == "edge_heights.json":
            continue  # derived data, read by build.py
        plan = json.loads(Path(f).read_text())
        zone = plan.get("zone", f.stem)
        if plan.get("footprint"):
            out["footprint"] = geom.expand(plan["footprint"], True)
        if plan.get("field_frame"):
            out["field_frame"] = plan["field_frame"]
        for s in plan.get("surfaces", []):
            if s.get("reference"):
                continue  # drawn for checking only: the thing itself is in another source model
            out["surfaces"].append(
                dict(
                    s,
                    zone=zone,
                    ring=geom.expand(s["ring"], True),
                    holes=[geom.expand(h, True) for h in s.get("holes", [])],
                )
            )
        for s in plan.get("strips", []):
            out["surfaces"].append(
                dict(s, zone=zone, ring=geom.ribbon(s["centre"], s["width"]), holes=[])
            )
        for c in plan.get("curbs", []):
            out["curbs"].append(
                dict(c, zone=zone, line=geom.expand(c["path"], c.get("closed", False)))
            )
        for m in plan.get("markings", []):
            out["markings"].extend(primitives(m))
        for lift in plan.get("lifts", []):
            out["lifts"].append(dict(lift, zone=zone, ring=geom.expand(lift["ring"], True)))
        for key in ("points", "stands", "fences", "buildings"):
            out[key].extend(dict(p, zone=zone) for p in plan.get(key, []))
    for i, s in enumerate(out["surfaces"]):
        s["layer"] = (s.get("layer", LAYER[s["kind"]]), i)
        if geom.area(s["ring"]) < 0:
            s["ring"] = s["ring"][::-1]
    out["surfaces"].sort(key=lambda s: s["layer"])
    if out["field_frame"]:
        out["markings"].extend(football(out["field_frame"]))
    for i, s in enumerate(out["surfaces"]):
        # sheet names carry the surface's number, not its name: the web exporter refuses images
        # whose
        # names contain words such as "mask" or "photo", and a surface name must not be able to trip
        # that
        s["sheets"] = (
            geom.sheets(f"p{i:03d}", s["ring"]) if is_painted(s, out["markings"]) else None
        )
    return out


def primitives(m):
    """
    A marking as paint primitives: {"line": dense polyline, "width", "colour"} or {"ring": outline,
    "colour"}.
    """
    colour = m.get("colour", "white")
    if m["type"] == "area":
        return [dict(ring=geom.expand(m["ring"], True), colour=colour)]
    if m["type"] == "stalls":
        return [dict(line=seg, width=m.get("width", 0.1), colour=colour) for seg in geom.stalls(m)]
    line = geom.expand(m["path"], m.get("closed", False))
    if m.get("closed"):
        line = line + line[:1]
    parts = geom.dashes(line, *m["dash"]) if m.get("dash") else [line]
    return [dict(line=p, width=m.get("width", 0.1), colour=colour) for p in parts]


def is_painted(surface, markings):
    """A paved surface gets a paint texture when a marking has a point inside it."""
    if surface["kind"] not in PAINTABLE:
        return False
    b = geom.bounds(surface["ring"])
    for m in markings:
        for p in m.get("line") or m["ring"]:
            if (
                b[0] <= p[0] <= b[2]
                and b[1] <= p[1] <= b[3]
                and geom.inside(surface["ring"], p[0], p[1])
            ):
                return True
    return False


def football(ff):
    """Paint for an American football field, generated from the field frame, never traced.

    Rule-book geometry (NCAA): 120 yd x 53 1/3 yd to the outside of the 4 in boundary lines, a line
    every
    5 yd, hash marks 60 ft in from each sideline and short ticks at the sidelines every yard.
    Numerals and
    lettering are drawn by paint.py, which also draws what the 2025 photographs show (team area
    bands,
    end lettering); those are flagged UNVERIFIED there.
    """
    to_model = geom.frame(ff["centre"], ff["angle"])[1]
    w, half_l, half_w, out = 4 * 0.0254, 60 * YD, 80 * 0.3048, []

    def line(u0, v0, u1, v1, width=w, colour="white"):
        out.append(
            dict(line=[to_model(u0, v0), to_model(u1, v1)], width=width, colour=colour, field=True)
        )

    for side in (-1, 1):  # sidelines and end lines, centred half a line width inside the outer edge
        line(-half_l, side * (half_w - w / 2), half_l, side * (half_w - w / 2))
        line(side * (half_l - w / 2), -half_w, side * (half_l - w / 2), half_w)
    for i in range(-10, 11):  # goal lines and every 5 yd between them
        line(i * 5 * YD, -half_w, i * 5 * YD, half_w)
    hash_v = half_w - 60 * 0.3048
    for yard in range(-49, 50):
        if yard % 5 == 0:
            continue
        u = yard * YD
        for side in (-1, 1):
            line(u, side * hash_v, u, side * (hash_v + 2 * 0.3048))  # inbound hash marks, 2 ft long
            line(u, side * (half_w - w - 2 * 0.3048), u, side * (half_w - w))  # sideline ticks
    for side in (-1, 1):  # extra point marks at the 3 yd lines
        line(side * 47 * YD, -1 * 0.3048, side * 47 * YD, 1 * 0.3048)
    return out

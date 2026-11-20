"""Load the plan files and work out what the builders share: dense outlines, layers, paint sheets.

Pure Python (no bpy, no numpy), so `paint.py` (system Python) and `ground.py` (Blender) see the same
layout.
"""

import json
import math
from pathlib import Path

import geom
import marks

# water lies over soft ground (a pond in a gravel yard) and under paving (a walk across it wins)
LAYER = {
    "lawn": 0,
    "mulch": 1,
    "gravel": 2,
    "water": 2.5,
    "asphalt": 3,
    "turf": 4,
    "concrete": 5,
    "brick": 6,
}
YD = 0.9144
PAINTABLE = {"asphalt", "turf", "gravel"}  # gravel: chalk lines on a clay infield
# texture sheet resolution, pixels per metre: 4 in lines are 2 to 3 pixels wide
PPM = {"asphalt": 20.0, "turf": 24.0, "gravel": 24.0, "lawn": 20.0}


def areas(args=()):
    """The plan folders to work on: every folder beside this file that holds a footprint.json, or
    only those named after `--areas` (comma separated) in `args`."""
    here = Path(__file__).resolve().parent
    found = sorted(d for d in here.iterdir() if (d / "footprint.json").exists())
    if "--areas" in args:
        want = args[args.index("--areas") + 1].split(",")
        missing = set(want) - {d.name for d in found}
        if missing:
            raise SystemExit(f"no such area: {sorted(missing)}")
        found = [d for d in found if d.name in want]
    return found


def load(plan_dir):
    """Merge every *.json of one area folder (sorted by name) into one layout dict."""
    out = dict(
        footprint=None,
        free_edges=[],
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
    out["area"] = Path(plan_dir).name
    for f in sorted(Path(plan_dir).glob("*.json")):
        if f.name == "edge_heights.json":
            continue  # derived data, read by build.py
        plan = json.loads(Path(f).read_text())
        zone = plan.get("zone", f.stem)
        if plan.get("footprint"):
            out["footprint"] = geom.expand(plan["footprint"], True)
        for e in plan.get("free_edges", []):
            out["free_edges"].append(geom.expand(e["ring"], True))
        if plan.get("field_frame"):
            out["field_frame"] = plan["field_frame"]
        for s in plan.get("surfaces", []):
            if s.get("reference"):
                continue  # drawn for checking only: the thing itself is in another source model
            check_surface(s)
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
        for q in plan.get("points", []):
            check_point(q)
        for key in ("points", "stands", "fences", "buildings"):
            out[key].extend(dict(p, zone=zone) for p in plan.get(key, []))
    for i, s in enumerate(out["surfaces"]):
        s["layer"] = (s.get("layer", LAYER[s["kind"]]), i)
        if geom.area(s["ring"]) < 0:
            s["ring"] = s["ring"][::-1]
    out["surfaces"].sort(key=lambda s: s["layer"])
    if out["field_frame"]:
        out["markings"].extend(football(out["field_frame"]))
    painted = painted_surfaces(out["surfaces"], out["markings"])
    for i, s in enumerate(out["surfaces"]):
        # sheet names carry the surface's number, not its name: the web exporter refuses images
        # whose
        # names contain words such as "mask" or "photo", and a surface name must not be able to trip
        # that
        s["sheets"] = (
            geom.sheets(f"{out['area']}_p{i:03d}", s["ring"], ppm=PPM[s["kind"]])
            if i in painted
            else None
        )
    for j, b in enumerate(out["buildings"]):
        if "markings" in b:
            roof_paint(b, f"{out['area']}_d{j:03d}")
    return out


def roof_paint(part, name):
    """Paint on a flat roof (the top level of a parking deck) or on a deck's ramp (a `shed` roof:
    one sloped plane): the part's `markings` as primitives in `paint`, and one sheet over the whole
    roof in `sheets`. The sheet is mapped straight down from the plan, like the ground's sheets.
    """
    roof = part.get("roof", "flat")
    ramp = roof == "shed" and part.get("style") == "deck"
    if (roof != "flat" and not ramp) or part.get("open"):
        raise ValueError(f"{part.get('name')}: markings need a flat roof or a deck's ramp")
    part["paint"] = [p for m in part["markings"] for p in primitives(m)]
    ring = geom.expand(part["ring"], True)
    part["sheets"] = geom.sheets(name, ring, max_len=1e9, ppm=PPM["asphalt"])


def sheet_uv(sheet, x, y):
    """Texture coordinates of model point (x, y) on a paint sheet (0..1 over the sheet)."""
    u, v = geom.frame((0.0, 0.0), sheet["angle"])[0](x, y)
    return (
        (u - sheet["u0"]) / (sheet["u1"] - sheet["u0"]),
        (v - sheet["v0"]) / (sheet["v1"] - sheet["v0"]),
    )


def primitives(m):
    """
    A marking as paint primitives: {"line": dense polyline, "width", "colour"}, {"ring": outline,
    "colour"} or {"text", "at", "right_angle", "height", "width", "colour", "box": outline}.
    """
    colour = m.get("colour", "white")
    if m["type"] == "area":
        return [dict(ring=geom.expand(m["ring"], True), colour=colour)]
    if m["type"] == "arrow":
        return [
            dict(ring=r, colour=colour)
            for r in marks.arrow(m["at"], m["angle"], m["shape"], m.get("length"))
        ]
    if m["type"] == "crosswalk":
        rings = marks.crosswalk(
            m["line"],
            m.get("width", 3.0),
            m.get("style", "continental"),
            m.get("bar", 0.6),
            m.get("spacing", 1.2),
        )
        return [dict(ring=r, colour=colour) for r in rings]
    if m["type"] == "text":
        h = m.get("height", 2.4)
        w = m.get("width") or marks.word_width(m["text"], h)
        box = marks.word_box(m["at"], m["angle"], h, w)
        right = m["angle"] - 90  # read by someone facing `angle`: left to right is 90 deg less
        return [
            dict(
                text=m["text"],
                at=tuple(m["at"]),
                right_angle=right,
                height=h,
                width=w,
                colour=colour,
                box=box,
            )
        ]
    if m["type"] == "stalls":
        return [dict(line=seg, width=m.get("width", 0.1), colour=colour) for seg in geom.stalls(m)]
    line = geom.expand(m["path"], m.get("closed", False))
    if m.get("closed"):
        line = line + line[:1]
    parts = geom.dashes(line, *m["dash"]) if m.get("dash") else [line]
    return [dict(line=p, width=m.get("width", 0.1), colour=colour) for p in parts]


POINT_KINDS = {
    "lamp", "light_pole", "sign", "gate", "flasher", "goalpost", "scoreboard", "bench",
    "bike_rack", "ticket_machine", "mini_high", "utility_pole", "pylon", "foul_pole",
    "soccer_goal", "tree",
}  # fmt: skip


def check_point(p):
    """A point of a kind no builder makes was skipped without a word (a station canopy was lost
    that way): refuse it when the plan is read."""
    if p.get("kind") not in POINT_KINDS:
        raise ValueError(f"point {p.get('name')!r}: unknown kind {p.get('kind')!r}")


def check_surface(s):
    """Refuse what the builders cannot honour for water: a water surface is one level sheet with
    no paint; `level` (metres, NAVD88) is for water only and must be a number."""
    name = s.get("name")
    if "level" in s:
        lv = s["level"]
        if s["kind"] != "water":
            raise ValueError(f"{name}: only water takes a level")
        if isinstance(lv, bool) or not isinstance(lv, int | float) or not math.isfinite(lv):
            raise ValueError(f"{name}: level must be a height in metres, not {lv!r}")
    if s["kind"] == "water" and s.get("paint"):
        raise ValueError(f"{name}: water takes no paint")


def paintable(surface):
    """Can this surface carry paint? Asphalt, turf and gravel always; natural grass only when the
    plan says so (`"paint": true`: a mown ball field with chalk lines), because painted grass is
    shown as an even, untinted turf and an ordinary lawn must not turn into that by accident.
    """
    return surface["kind"] in PAINTABLE or (
        surface["kind"] == "lawn" and bool(surface.get("paint"))
    )


def painted_surfaces(surfaces, markings):
    """Indices of the surfaces that carry paint: the top surface under a point of some marking.

    Surfaces are sorted by layer, so the last one that contains a point is the one you see there. A
    ring
    walk around a field contains the whole field, but the turf lies over it: the walk gets no sheet.
    Football lines belong to turf only. Only asphalt and turf take paint.
    """
    boxes = [geom.bounds(s["ring"]) for s in surfaces]
    out = set()
    for m in markings:
        pts = m.get("line") or m.get("ring") or m["box"]
        if len(pts) == 2:  # a long straight line: test along it, not only its ends
            pts = [(p[0], p[1]) for p in geom.resample(pts, 3.0)]
        for x, y in pts:
            for i in range(len(surfaces) - 1, -1, -1):
                b, s = boxes[i], surfaces[i]
                if b[0] <= x <= b[2] and b[1] <= y <= b[3] and geom.inside(s["ring"], x, y):
                    if not any(geom.inside(h, x, y) for h in s["holes"]):
                        if paintable(s) and (s["kind"] == "turf" or not m.get("field")):
                            out.add(i)
                        break
    return out


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


def meets_neighbour(lay, x, y):
    """Does an edge sample at (x, y) count? Not inside a `free_edges` ring: there the footprint
    runs under another model's building, the ground "beside" it is hidden inside that building,
    and the edge follows this area's own grade (footprint.json gives the ring and the reason).
    """
    return not any(geom.inside(r, x, y) for r in lay["free_edges"])

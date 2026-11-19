"""Place what the plan lists besides the ground: stands, fences, hedges and fixtures.

The plan gives positions; the builders (`stand.py`, `fixtures.py`) give shapes. This module only
joins the
two: it seats each thing on the ground and turns it the way the plan says.
"""

import math
import re

import fixtures
import geom
import kit
import stand


def _slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")


def _name(zone, item, kind=""):
    return f"SW_{_slug(zone).capitalize()}_{_slug(item.get('name') or kind)}"


def _front_frame(ring, front):
    """
    Front-left corner, angle, length and depth of a stand: rows rise to the left of the front edge.
    """
    (ax, ay), (bx, by) = front
    cx = sum(p[0] for p in ring) / len(ring)
    cy = sum(p[1] for p in ring) / len(ring)
    if (bx - ax) * (cy - ay) - (by - ay) * (
        cx - ax
    ) < 0:  # the body is to the right: walk the edge the other way
        ax, ay, bx, by = bx, by, ax, ay
    length = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / length, (by - ay) / length
    depth = max((p[0] - ax) * -uy + (p[1] - ay) * ux for p in ring)
    return (ax, ay), math.degrees(math.atan2(uy, ux)), length, depth


def stands(lay, terrain):
    out, back = [], {}
    boxes = [s for s in lay["stands"] if "press" in s["name"].lower()]
    for s in lay["stands"]:
        if s in boxes:
            continue
        ring = geom.expand(s["ring"], True)
        at, angle, length, depth = _front_frame(ring, s["front"])
        z = terrain.at(at[0], at[1])
        name = _name(s["zone"], s)
        rows = int(s.get("rows") or max(3, round(depth / 0.7)))
        if s.get("elevated", depth > 12):
            first, rise = s.get("first_row_height", 1.2), s.get("rise", 0.2)
            out += stand.grandstand(
                name,
                (at[0], at[1], z),
                angle,
                length,
                depth,
                rows,
                first_row_height=first,
                rise=rise,
                sections=s.get("sections"),
            )
            back[s["name"]] = dict(
                at=at, angle=angle, length=length, depth=depth, top=z + first + rows * rise, z=z
            )
        else:
            n = int(s.get("sections") or 1)
            gap = s.get("gap", 0.6)
            part = (length - (n - 1) * gap) / n
            place = kit.placer((at[0], at[1], 0.0), angle)
            for i in range(n):  # separate bleacher units side by side, as the photographs show
                px, py, _ = place(i * (part + gap), 0)
                made = stand.bleacher(
                    f"{name}_{i + 1}", (px, py, terrain.at(px, py)), angle, part, depth, rows
                )
                out += made if isinstance(made, list) else [made]
    for s in boxes:  # the press box stands behind the top rows of the stand it belongs to
        ring = geom.expand(s["ring"], True)
        host = back.get(s.get("on")) or next(iter(back.values()), None)
        if host is None:
            continue
        to_local = geom.frame(host["at"], host["angle"])[0]
        loc = [to_local(p[0], p[1]) for p in ring]
        u0, u1 = min(p[0] for p in loc), max(p[0] for p in loc)
        v0, v1 = min(p[1] for p in loc), max(p[1] for p in loc)
        place = kit.placer((host["at"][0], host["at"][1], 0.0), host["angle"])
        px, py, _ = place(u0, v0)
        cabin = s.get("cabin", 3.0)
        # `height` is the roof above the ground where the evidence gives it; else just above the top
        # row
        floor = (
            s["height"] - cabin if s.get("height", 0) > cabin + 2 else host["top"] - host["z"] + 0.3
        )
        out += stand.press_box(
            _name(s["zone"], s),
            (px, py, host["z"]),
            host["angle"],
            u1 - u0,
            v1 - v0,
            cabin,
            floor_z=floor,
            stair_side=s.get("stair_side", "left"),
        )
    return out


def fences(lay, terrain):
    out = []
    for f in lay["fences"]:
        line = geom.expand(f["path"], f.get("closed", False))
        if f.get("closed"):
            line = line + line[:1]
        name, kind = _name(f["zone"], f, "fence"), f.get("kind", "chain_link_black")
        if kind == "hedge":
            out.append(hedge(name, line, terrain, f.get("height", 4.5), f.get("width", 1.6)))
        elif "net" in kind:
            out.append(fixtures.net_poles(name, line, f.get("height", 9.0), ground=terrain.at))
        else:
            colour = "black" if "black" in kind else "galvanised"
            out.append(
                fixtures.fence(name, line, f.get("height", 1.8), ground=terrain.at, colour=colour)
            )
    return out


def hedge(name, line, terrain, height, width):
    """A clipped evergreen row as one solid: a rounded section swept along the line. Species
    UNVERIFIED.
    """
    b = kit.Builder(name + "_UNVERIFIED")
    leaf = kit.mat("foliage", "hedge_evergreen", (0.035, 0.075, 0.03), rough=1.0)
    pts = geom.resample(line, 2.0)
    left = geom.offset([(p[0], p[1]) for p in pts], width / 2)
    right = geom.offset([(p[0], p[1]) for p in pts], -width / 2)
    # section across the row: foot, shoulder, rounded top, shoulder, foot (as fractions of width and
    # height)
    sec = [
        (1.0, 0.0),
        (1.0, 0.72),
        (0.6, 0.95),
        (0.0, 1.0),
        (-0.6, 0.95),
        (-1.0, 0.72),
        (-1.0, 0.0),
    ]
    verts, faces = [], []
    for i, p in enumerate(pts):
        z = terrain.at(p[0], p[1])
        wobble = (
            1 + 0.06 * math.sin(i * 1.7) + 0.04 * math.sin(i * 0.61)
        )  # shrubs in a row are not all one height
        for k, h in sec:
            x = p[0] + (left[i][0] - p[0]) * k if k >= 0 else p[0] + (right[i][0] - p[0]) * -k
            y = p[1] + (left[i][1] - p[1]) * k if k >= 0 else p[1] + (right[i][1] - p[1]) * -k
            verts.append((x, y, z - 0.1 + h * height * wobble))
        if i:
            a, c = (i - 1) * len(sec), i * len(sec)
            faces += [(a + j, c + j, c + j + 1, a + j + 1) for j in range(len(sec) - 1)]
    n = len(sec)
    faces += [tuple(range(n)), tuple(range((len(pts) - 1) * n + n - 1, (len(pts) - 1) * n - 1, -1))]
    b.faces(verts, faces, leaf, smooth=True)
    return b.finish()


def points(lay, terrain):
    out = []
    ff = lay["field_frame"]
    for p in lay["points"]:
        kind, (x, y) = p["kind"], p["at"]
        # `base`: the height of what the thing stands on when that is not this build's ground
        at = (x, y, p.get("base", terrain.at(x, y)))
        name, angle = _name(p["zone"], p, kind), p.get("angle", 0.0)
        opt = {}
        if "height" in p:
            opt["height"] = p["height"]
        if kind == "light_pole":
            if ff and "angle" not in p:  # flood lights face the middle of the field
                angle = math.degrees(math.atan2(ff["centre"][1] - y, ff["centre"][0] - x))
            out.append(fixtures.light_pole(name, at, angle, **opt))
        elif kind == "goalpost":
            # the goal stands on the field's long axis, 6 ft behind the end line, facing the field
            if ff:
                to_local, to_model = geom.frame(ff["centre"], ff["angle"])
                side = 1 if to_local(x, y)[0] > 0 else -1
                gx, gy = to_model(side * (60 * 0.9144 + 1.83), 0.0)
                at, angle = (gx, gy, terrain.at(gx, gy)), ff["angle"] + (180 if side > 0 else 0)
            out.append(fixtures.goalpost(name, at, angle))
        elif kind == "scoreboard":
            out.append(
                fixtures.scoreboard(
                    name, at, angle, p.get("width", 6.0), p.get("board_height", 3.0)
                )
            )
        elif kind == "bench":
            if p["zone"] == "field" and ff:
                # a team area: benches end to end along the sideline, players facing the field
                to_local = geom.frame(ff["centre"], ff["angle"])[0]
                facing = ff["angle"] + (-90 if to_local(x, y)[1] > 0 else 90)
                n = max(1, round(p.get("length", 6.0) / 7.5))
                run = kit.placer((x, y, 0.0), ff["angle"])
                for i in range(n):
                    bx, by, _ = run((i - (n - 1) / 2) * 7.5, 0)
                    seat = (bx, by, terrain.at(bx, by))
                    out.append(fixtures.team_bench(f"{name}_{i + 1}", seat, facing, 6.0))
            else:
                out.append(fixtures.platform_bench(name, at, angle, p.get("length", 1.8)))
        elif kind in ("gate", "flasher"):
            out.append(
                fixtures.crossing_gate(
                    name, at, angle, p.get("arm", 7.0 if kind == "gate" else 0.0)
                )
            )
        elif kind == "lamp":
            out.append(fixtures.lot_lamp(name, at, angle, heads=p.get("heads", 1), **opt))
        elif kind == "sign":
            out.append(fixtures.station_sign(name, at, angle))
        elif kind == "bike_rack":
            out.append(fixtures.bike_rack(name, at, angle, p.get("hoops", 4)))
        elif kind == "ticket_machine":
            out.append(fixtures.ticket_machine(name, at, angle))
        elif kind == "utility_pole":
            out.append(fixtures.utility_pole(name, at, angle, **opt))
        elif kind == "mini_high" and p.get("ring"):
            ring = [(q[0], q[1]) for q in p["ring"]]
            out.append(
                fixtures.mini_high_platform(
                    name, ring, at[2] + p.get("deck", 1.0), at[2], ramp=p.get("ramp")
                )
            )
    return out


def buildings(lay, terrain):
    """Plain massing for small buildings the evidence gives only an outline and a height for."""
    out = []
    wall = kit.mat("plaster", "massing_wall", kit.srgb("#b9b6ad"), rough=0.9)
    roof = kit.mat("metal", "massing_roof", kit.srgb("#7d8084"), rough=0.6, metal=0.3)
    for b in lay["buildings"]:
        ring = geom.expand(b["ring"], True)
        if geom.area(ring) < 0:
            ring = ring[::-1]
        zs = [terrain.at(x, y) for x, y in ring]
        base, top = min(zs) - 0.3, max(zs) + b["height"]
        m = kit.Builder(_name(b["zone"], b) + "_UNVERIFIED")
        m.prism(ring, base, top - 0.25, wall, top=False)
        eave = geom.offset(ring, -0.3, True)  # the roof oversails the walls by 0.3 m
        m.prism(eave, top - 0.25, top, roof, top=True, bottom=True)
        out.append(m.finish())
    return out


TREE_MESH, TREE_HEIGHT = (
    "Tree_RedMaple_LOD1_v2Oct",
    16.56,
)  # a tree mesh of the main model, its height


def trees(lay, terrain, assets):
    """Single trees from the LiDAR canopy, as copies of one tree mesh of the main model.

    `assets` is a main-model .blend (a release file will do). Position and height are from the plan;
    the species is not known, so every tree is the red maple asset, UNVERIFIED. Trees that another
    source model already has (plan field `skip`) and trees outside the footprint are left out.
    """
    import bpy

    todo = [p for p in lay["points"] if p["kind"] == "tree" and not p.get("skip")]
    todo = [p for p in todo if geom.inside(lay["footprint"], *p["at"])]
    if not todo:
        return []
    if not assets:
        print("SW no --assets file: skipping", len(todo), "trees")
        return []
    with bpy.data.libraries.load(str(assets)) as (src, dst):
        dst.meshes = [TREE_MESH] if TREE_MESH in src.meshes else []
    if not dst.meshes:
        print("SW", TREE_MESH, "not found in", assets, ": skipping trees")
        return []
    out = []
    for i, p in enumerate(todo):
        x, y = p["at"]
        ob = bpy.data.objects.new(_name(p["zone"], p, "tree") + "_UNVERIFIEDspecies", dst.meshes[0])
        k = p.get("height", 12.0) / TREE_HEIGHT
        ob.location = (x, y, terrain.at(x, y) - 0.1)
        ob.scale = (k, k, k)
        ob.rotation_euler = (0, 0, math.radians((i * 137.5) % 360))
        kit.collection().objects.link(ob)
        out.append(ob)
    return out


def build(lay, terrain, assets=None):
    return (
        trees(lay, terrain, assets)
        + stands(lay, terrain)
        + fences(lay, terrain)
        + points(lay, terrain)
        + buildings(lay, terrain)
    )

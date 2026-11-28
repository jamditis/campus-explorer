"""Rough interiors: floors in the `interiors` format (rooms.py, interior.py) made from a building's
footprint, its floor levels and what little public evidence there is, instead of from a floor plan.

A plan's `rough` list holds one entry per building (README "rough interiors"). `floors(entry)`
turns it into one `interiors` floor per level: a slab at the level, an inner lining along the
shell with an opening at each entrance, an entrance lobby from each entrance to the nearest
corridor, corridors along `spines`, stair and lift cores, rooms as walls square to the corridor
every `bay` metres with a door each, toilets only where the entry places them, and room numbers
only where the entry gives them. Every object is UNVERIFIED: only the footprint and the levels
come from a source, and the entry says which.

Coordinates are model metres (x east, y north, z NAVD88), as everywhere in blender/scripted.
No bpy.
"""

import math

import geom
import rooms

WALL = 0.4  # outline to the shell's inner face when the entry gives none (UNVERIFIED)
LINING = 0.15  # the inner lining's thickness
SLAB = 0.3  # floor slab thickness: a floor's ceiling is the next level less this
CORRIDOR = 2.4  # corridor width between wall centres
BAY = 7.2  # room width along a corridor: two 3.6 m window bays
DEPTH = 9.0  # deepest room behind a corridor wall; deeper floor stays open
LOBBY = 6.0  # lobby width: from the entrance to the middle of the nearest corridor
ENTRANCE = 2.0  # opening in the lining at an entrance
ENTRANCE_HEAD = 2.4  # its head above the floor
DOOR = 0.9  # a room's door in the corridor wall
STAIR = (6.0, 3.0)  # length along the corridor, width across it
LIFT = (2.4, 2.4)
REACH = 3.0  # an entrance may lie this far outside the outline (a porch, a step)
PASS = 0.3  # a walk crosses the lining at least this far inside its door's opening's edges
CLEAR = 1.0  # a hall round a corner keeps this far from the shell's inner face
FAR = 1000.0  # a line long enough to cross any building, cut back to the shell
# OSM building tags of housing: residence halls and apartments get exteriors only (AGENTS.md)
HOUSING = {"dormitory", "apartments", "residential", "house", "detached", "semidetached_house"}


def _unit(p, q):
    d = math.dist(p, q)
    return (q[0] - p[0]) / d, (q[1] - p[1]) / d


def _rect(p, q, half):
    """Anticlockwise ring of the band `half` metres either side of segment p->q."""
    ux, uy = _unit(p, q)
    nx, ny = -uy * half, ux * half
    return [
        (p[0] - nx, p[1] - ny),
        (q[0] - nx, q[1] - ny),
        (q[0] + nx, q[1] + ny),
        (p[0] + nx, p[1] + ny),
    ]


def _box(at, u, along, across):
    """Ring of a box centred on `at`, `along` metres in direction `u` and `across` square to it."""
    ux, uy = u
    a, c = along / 2, across / 2
    return [
        (at[0] + sx * ux * a - sy * uy * c, at[1] + sx * uy * a + sy * ux * c)
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))
    ]


def _r(ring):
    return [[round(x, 2), round(y, 2)] for x, y in ring]


def inset(ring, d):
    """`ring` moved `d` metres inward (mitred), anticlockwise."""
    ring = [tuple(p[:2]) for p in ring]
    if geom.area(ring) < 0:
        ring = ring[::-1]
    return geom.offset(ring, d, closed=True)


def _centroid(ring):
    a = geom.area(ring)
    cx = cy = 0.0
    for p, q in zip(ring, ring[1:] + ring[:1], strict=True):
        k = p[0] * q[1] - q[0] * p[1]
        cx += (p[0] + q[0]) * k
        cy += (p[1] + q[1]) * k
    return cx / (6 * a), cy / (6 * a)


def default_spine(inside):
    """The longest piece, inside the shell, of the line through the floor's centroid along the
    long side of the smallest rectangle round it."""
    ang = math.radians(geom.long_axis(inside))
    c = _centroid(inside)
    u = (math.cos(ang), math.sin(ang))
    seg = ((c[0] - u[0] * FAR, c[1] - u[1] * FAR), (c[0] + u[0] * FAR, c[1] + u[1] * FAR))
    pieces = rooms.clip(seg, inside=inside)
    if not pieces:
        raise ValueError("the long axis through the centroid misses the floor")
    return max(pieces, key=lambda s: math.dist(*s))


def _nearest(spines, pt):
    """(spine index, point on it, distance along it) nearest to `pt`."""
    best = None
    for i, (p, q) in enumerate(spines):
        ux, uy = _unit(p, q)
        d = math.dist(p, q)
        t = max(0.0, min(d, (pt[0] - p[0]) * ux + (pt[1] - p[1]) * uy))
        on = (p[0] + ux * t, p[1] + uy * t)
        e = math.dist(on, pt)
        if best is None or e < best[0]:
            best = (e, i, on, t)
    return best[1:]


def closed_path(ring, avoid=()):
    """`ring` as a closed wall path that starts and ends in the middle of the side farthest from
    the points `avoid` (the doors), so no door crosses the path's ends and the seam is no corner.
    """
    ring = [tuple(p[:2]) for p in ring]
    sides = list(zip(ring, ring[1:] + ring[:1], strict=True))

    def room(i):
        a, b = sides[i]
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        return min((math.dist(m, x) for x in avoid), default=0.0), math.dist(a, b)

    i = max(range(len(sides)), key=room)
    a, b = sides[i]
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    return [mid] + ring[i + 1 :] + ring[: i + 1] + [mid]


def _door(path, pt, width, head=None):
    """An opening `width` wide in `path` centred on the point of the path nearest to `pt`."""
    s = rooms._along(path, pt)
    out = dict(
        at=_r([rooms._point(path, s - width / 2)])[0], to=_r([rooms._point(path, s + width / 2)])[0]
    )
    if head is not None:
        out["head"] = head
    return out


def _runs(name, p, q, keep, inside, thickness, doors=()):
    """A straight wall p->q as wall runs, cut to `inside` and out of every `keep` ring. Each door
    (s0, s1 metres from p) goes to the piece that holds it whole; a door no piece holds is dropped
    with the wall it was in."""
    ux, uy = _unit(p, q)
    out = []
    for a, b in rooms.clip((p, q), keep_out=keep, inside=inside):
        s_a, s_b = math.dist(p, a), math.dist(p, b)
        if s_b - s_a < 0.3:
            continue  # a sliver between two clear zones
        run = dict(name=f"{name}_{len(out)}_UNVERIFIED", path=_r([a, b]), thickness=thickness)
        held = [(s0, s1) for s0, s1 in doors if s_a + 0.1 <= s0 and s1 <= s_b - 0.1]
        if held:
            run["openings"] = [
                dict(
                    at=_r([(p[0] + ux * s0, p[1] + uy * s0)])[0],
                    to=_r([(p[0] + ux * s1, p[1] + uy * s1)])[0],
                )
                for s0, s1 in held
            ]
        out.append(run)
    return out


def _crosses(leg, ring):
    """Does the segment `leg` pass through or into `ring`?"""
    if math.dist(*leg) < 0.01:
        return False
    free = rooms.clip(leg, keep_out=[ring])
    return (
        len(free) != 1
        or math.dist(free[0][0], leg[0]) > 0.01
        or math.dist(free[0][1], leg[1]) > 0.01
    )


def _overlap(a, b):
    """Do the convex rings `a` and `b` share any area (touching edges do not count)?"""
    for ring in (a, b):
        for p, q in zip(ring, ring[1:] + ring[:1], strict=True):
            n = (-(q[1] - p[1]), q[0] - p[0])  # an axis square to this side
            pa = [n[0] * x + n[1] * y for x, y in a]
            pb = [n[0] * x + n[1] * y for x, y in b]
            if max(pa) <= min(pb) + 1e-9 or max(pb) <= min(pa) + 1e-9:
                return False
    return True


def _cores(r, ends, spines, lobbies, rings):
    """Stair and lift cores: the entry's own, or a stair at each end of each spine (`ends`: the
    spines before they were cut back for the stairs; beside the end when a way in passes there)
    and a lift across the corridor from the first lobby."""
    if "cores" in r:
        out = []
        for c in r["cores"]:
            size = c.get("size", STAIR if c["kind"] == "stair" else LIFT)
            u = (
                math.cos(math.radians(c.get("angle", 0))),
                math.sin(math.radians(c.get("angle", 0))),
            )
            if "angle" not in c:
                i, _on, _t = _nearest(spines, c["at"])
                u = _unit(*spines[i])
            out.append(dict(kind=c["kind"], ring=_box(c["at"], u, *size)))
        return out
    corridor = r.get("corridor", CORRIDOR)
    lifts = []
    if lobbies:
        lob = lobbies[0]
        p, q = spines[lob["spine"]]
        u = _unit(p, q)
        side = lob["side"]  # +1: the entrance is left of the spine
        off = -side * (corridor / 2 + LIFT[1] / 2)
        s = lob["along"]
        at = (p[0] + u[0] * s - u[1] * off, p[1] + u[1] * s + u[0] * off)
        lifts.append(dict(kind="lift", ring=_box(at, u, *LIFT)))
    # a stair stands inside the lining of every level, since it runs from the lowest to the roof
    wall = r.get("wall", WALL)
    rooms_in = [inset(outline, wall + LINING - 0.01) for outline, _in, _li in rings.values()]
    walks = [leg for lob in lobbies for leg in zip(lob["route"], lob["route"][1:], strict=False)]
    out = []
    for p, q in ends:
        u = _unit(p, q)
        for end, sign in ((p, 1), (q, -1)):
            at = (end[0] + sign * u[0] * STAIR[0] / 2, end[1] + sign * u[1] * STAIR[0] / 2)
            # a door at the corridor's end: the stair steps aside, beside the corridor's end, to
            # a side where it fits every level and meets no lift
            across = corridor / 2 + STAIR[1] / 2
            for off in (0.0, across, -across):
                ring = _box((at[0] - u[1] * off, at[1] + u[0] * off), u, *STAIR)
                if (
                    not any(_crosses(leg, ring) for leg in walks)
                    and all(geom.inside(g, *v) for g in rooms_in for v in ring)
                    and not any(_overlap(ring, c["ring"]) for c in lifts)
                ):
                    break
            else:
                ring = _box(at, u, *STAIR)  # nowhere clear: _blocked refuses the way in
            out.append(dict(kind="stair", ring=ring))
    return out + lifts


def _foot(ring, pt):
    """The point of `ring` nearest to `pt` and the inward normal of the side it is on (`ring`
    anticlockwise: its inside is on the left)."""
    best = None
    for a, b in zip(ring, ring[1:] + ring[:1], strict=True):
        ux, uy = _unit(a, b)
        d = math.dist(a, b)
        s = max(0.0, min(d, (pt[0] - a[0]) * ux + (pt[1] - a[1]) * uy))
        on = (a[0] + ux * s, a[1] + uy * s)
        e = math.dist(on, pt)
        if best is None or e < best[0]:
            best = (e, on, (-uy, ux))
    return best[1], best[2]


def _free(p, q, ring):
    """Does the segment p->q lie wholly inside `ring`?"""
    if math.dist(p, q) < 1e-6:
        return geom.inside(ring, *p)
    pieces = rooms.clip((p, q), inside=ring)
    return (
        len(pieces) == 1 and math.dist(pieces[0][0], p) < 1e-6 and math.dist(pieces[0][1], q) < 1e-6
    )


def _path(a, b, ring):
    """The shortest walk from `a` to `b` inside `ring`: straight when it can be, otherwise by the
    ring's corners moved CLEAR into the floor (round a set-back, between the wings of a U). None
    when there is none."""
    if _free(a, b, ring):
        return [a, b]
    nodes = [a, b] + [v for v in inset(ring, CLEAR) if geom.inside(ring, *v)]
    best, back, todo = {0: 0.0}, {}, {0}
    while todo:
        i = min(todo, key=best.get)
        todo.discard(i)
        if i == 1:
            out = [1]
            while out[-1] != 0:
                out.append(back[out[-1]])
            return [nodes[k] for k in reversed(out)]
        for j, v in enumerate(nodes):
            d = best[i] + math.dist(nodes[i], v)
            if j != i and d < best.get(j, math.inf) and _free(nodes[i], v, ring):
                best[j], back[j] = d, i
                todo.add(j)
    return None


def _through(leg, lining, door):
    """Does the walk's last leg cross the lining (`lining`, the path the door's opening is cut in,
    centred on the lining's point nearest the door) PASS or more inside the opening's edges?"""
    centre, _n = _foot(lining, door)
    out = rooms.clip(leg, inside=lining)
    return len(out) == 1 and math.dist(out[0][1], centre) <= ENTRANCE / 2 - PASS


def _sides(a, b, k, part):
    """The side walls of a clear zone LOBBY wide along a->b (ring `k` of the way in)."""
    h = _unit(a, b)
    w = (h[1], -h[0])
    return [
        (
            part,
            (b[0] + w[0] * s * LOBBY / 2, b[1] + w[1] * s * LOBBY / 2),
            (a[0] + w[0] * s * LOBBY / 2, a[1] + w[1] * s * LOBBY / 2),
            s,
            k,
        )
        for s in (1, -1)
    ]


def _lobby(entrance, spines, inside, lining):
    """The way in from an entrance to the middle of the nearest corridor, as clear zones LOBBY
    wide. When the straight line from the corridor to the door stays in the floor (`inside`) and
    crosses the lining (`lining`) well inside the door's opening: one lobby along it, REACH past
    the door. Otherwise (a door beside a corridor's end, a set-back side, another wing): a porch
    square to the shell's side through the middle of the door's opening, LOBBY / 2 deep, and a
    hall from the porch to the corridor along the shortest walk inside the floor (`_path`),
    round its corners. The corridor wall on the entrance's side stops at it, the far one runs
    on. `route` is the walk: corridor, (corners, porch,) door."""
    door = tuple(entrance["at"][:2])
    i, on, along = _nearest(spines, door)
    p, q = spines[i]
    u = _unit(p, q)
    side = 1 if (u[0] * (door[1] - p[1]) - u[1] * (door[0] - p[0])) > 0 else -1
    gap = math.dist(on, door)
    out = dict(spine=i, side=side, along=along)
    pieces = rooms.clip((on, door), inside=inside) if gap > 0.01 else []
    straight = (
        len(pieces) == 1
        and math.dist(pieces[0][0], on) < 0.01
        and _through((on, door), lining, door)
    )
    if gap <= 0.01 or straight:
        n = _unit(on, door) if gap > 0.01 else (-u[1] * side, u[0] * side)  # towards the door
        near = (on[0] + n[0] * (gap + REACH), on[1] + n[1] * (gap + REACH))
        w = (n[1] * side, -n[0] * side)  # the corridor's direction for a lobby square to it
        sides = [
            (
                "",
                (near[0] + w[0] * s * LOBBY / 2, near[1] + w[1] * s * LOBBY / 2),
                (on[0] + w[0] * s * LOBBY / 2, on[1] + w[1] * s * LOBBY / 2),
                s,
                0,
            )
            for s in (1, -1)
        ]
        return dict(out, rings=[_rect(on, near, LOBBY / 2)], sides=sides, route=[on, door])
    foot, inward = _foot(lining, door)  # the middle of the door's opening
    stand = (foot[0] + inward[0] * LOBBY / 2, foot[1] + inward[1] * LOBBY / 2)
    outside = (foot[0] - inward[0] * REACH, foot[1] - inward[1] * REACH)
    rings = [_rect(outside, stand, LOBBY / 2)]
    e = (inward[1], -inward[0])  # along the shell's side
    sides = [
        (
            "p",
            (foot[0] + e[0] * s * LOBBY / 2, foot[1] + e[1] * s * LOBBY / 2),
            (stand[0] + e[0] * s * LOBBY / 2, stand[1] + e[1] * s * LOBBY / 2),
            s,
            0,
        )
        for s in (1, -1)
    ]
    walk = _path(on, stand, inside) or [on, stand]  # no walk inside: _blocked says so
    legs = [(a, b) for a, b in zip(walk, walk[1:], strict=False) if math.dist(a, b) > 0.01]
    for k, (a, b) in enumerate(legs):
        rings.append(_rect(a, b, LOBBY / 2))
        sides += _sides(a, b, len(rings) - 1, str(k) if k else "")
    return dict(
        out, rings=rings, sides=sides, route=[*walk, door]
    )  # stand, the opening's middle and the door lie in line


def _blocked(lob, inside, lining, cores):
    """Why the walk in from an entrance (`lob["route"]`) is not clear, or None: it must stay in
    the floor (`inside`) up to the lining, cross the lining within the door's opening with PASS
    to spare and pass no stair or lift."""
    route = lob["route"]
    legs = [leg for leg in zip(route, route[1:], strict=False) if math.dist(*leg) > 0.01]
    if not legs:
        return None  # the door is on the corridor: no walk to clear
    for k, leg in enumerate(legs):
        part = rooms.clip(leg, inside=inside)
        if not part or math.dist(part[0][0], leg[0]) > 0.01:
            return "starts outside the floor"
        if len(part) > 1:
            return "leaves the floor: give a corridor nearer to it"
        if k < len(legs) - 1 and math.dist(part[0][1], leg[1]) > 0.01:
            return "leaves the floor: give a corridor nearer to it"
        for c in cores:
            if _crosses(leg, c["ring"]):
                return f"passes a {c['kind']}: move it or the corridor"
    if not _through(legs[-1], lining, route[-1]):
        return "crosses the lining outside its door's opening: give a corridor nearer to it"
    return None


def _spines(r, building):
    """The corridor centrelines: `ends` as given (or the default), `spines` cut back for the
    stairs at their ends when the entry gives no cores."""
    wall = r.get("wall", WALL)
    ends = (
        [tuple(tuple(v[:2]) for v in s) for s in r["spines"]]
        if "spines" in r
        else [default_spine(inset(building, wall + LINING))]  # stairs stand inside the lining
    )
    if "cores" in r:
        return ends, ends
    spines = []  # the corridor stops at the stairs placed at its ends
    for p, q in ends:
        if math.dist(p, q) < 2 * STAIR[0] + BAY:
            raise ValueError(
                f"{r['name']}: a spine under {2 * STAIR[0] + BAY} m has no room for "
                "stairs at its ends: give the cores"
            )
        u = _unit(p, q)
        spines.append(
            (
                (p[0] + u[0] * STAIR[0], p[1] + u[1] * STAIR[0]),
                (q[0] - u[0] * STAIR[0], q[1] - u[1] * STAIR[0]),
            )
        )
    return ends, spines


def _outlines(r, building):
    """Each level's outline (anticlockwise), its floor ring (the shell's inner face) and its
    lining's path."""
    wall = r.get("wall", WALL)
    out = {}
    for lv in r["levels"]:
        ring = [tuple(p[:2]) for p in lv.get("outline", building)]
        if geom.area(ring) < 0:
            ring = ring[::-1]
        out[lv["level"]] = (ring, inset(ring, wall), inset(ring, wall + LINING / 2))
    return out


def routes(r):
    """Each entrance's walk in: (level, polyline from the corridor to the door)."""
    building = [tuple(p[:2]) for p in r["outline"]]
    if geom.area(building) < 0:
        building = building[::-1]
    if r.get("use") == "dining":
        return []  # an open dining floor: no corridor to walk from
    _ends, spines = _spines(r, building)
    rings = _outlines(r, building)
    return [
        (e["level"], _lobby(e, spines, *rings[e["level"]][1:])["route"])
        for e in r.get("entrances", [])
    ]


def check(r):
    """Problems with a rough entry, as text (empty when it is usable)."""
    out = []
    for key in (
        "name",
        "building",
        "osm_building",
        "outline",
        "levels",
        "roof",
        "evidence",
        "unverified",
    ):
        if key not in r:
            out.append(f"{r.get('name', '?')}: no {key}")
    if out:
        return out
    ring = [tuple(p[:2]) for p in r["outline"]]
    for one in [ring] + [lv["outline"] for lv in r["levels"] if "outline" in lv]:
        if abs(geom.area([tuple(p[:2]) for p in one])) < 20:
            out.append(f"{r['name']}: an outline is not a building")
    levels = [lv["floor"] for lv in r["levels"]]
    if levels != sorted(levels) or len(set(levels)) != len(levels):
        out.append(f"{r['name']}: levels must rise")
    if r["roof"] - levels[-1] < 2.4:
        out.append(f"{r['name']}: the top floor is under 2.4 m high")
    use = r.get("use")
    if use not in (None, "dining"):
        out.append(f"{r['name']}: use is 'dining' or not given")
    if r["osm_building"] in HOUSING and use != "dining":
        out.append(f"{r['name']}: housing gets no interior (AGENTS.md)")
    if use == "dining":  # AGENTS.md rule 16: the public dining floor and its entrance, nothing more
        if len(r["levels"]) != 1:
            out.append(f"{r['name']}: a dining hall gets its dining floor only")
        if not (r.get("open") or r["levels"][0].get("open")):
            out.append(f"{r['name']}: a dining floor is open: no corridors or rooms")
        for key in ("cores", "spines", "rooms"):
            if r.get(key):
                out.append(f"{r['name']}: a dining hall gets no {key}")
    if r.get("method", "overlay") not in ("overlay", "supersede"):
        out.append(f"{r['name']}: method is overlay or supersede")
    names = {lv["level"] for lv in r["levels"]}
    grown = inset(ring, -REACH)
    for e in r.get("entrances", []):
        if e["level"] not in names:
            out.append(f"{r['name']}: an entrance on level {e['level']}, which it does not have")
        if not geom.inside(grown, *e["at"]):
            out.append(
                f"{r['name']}: entrance {e['at']} is more than {REACH} m outside the outline"
            )
    for t in r.get("toilets", []) + r.get("rooms", []):
        if t["level"] not in names:
            out.append(
                f"{r['name']}: a room or toilet on level {t['level']}, which it does not have"
            )
        if "evidence" not in t:
            out.append(f"{r['name']}: a toilet or room label needs its evidence")
    for x in r.get("rooms", []):  # the viewer shows a label's last word and finds rooms by digits
        if " " in x["number"] or not any(ch.isdigit() for ch in x["number"]):
            out.append(f"{r['name']}: room label {x['number']!r} is not a room number")
    return out


def floors(r):
    """The `interiors` floors of one rough entry, lowest first."""
    problems = check(r)
    if problems:
        raise ValueError("; ".join(problems))
    name = r["name"]
    corridor = r.get("corridor", CORRIDOR)
    bay = r.get("bay", BAY)
    depth = r.get("depth", DEPTH)
    building = [tuple(p[:2]) for p in r["outline"]]
    if geom.area(building) < 0:
        building = building[::-1]
    dining = r.get("use") == "dining"  # no corridors, stairs or lifts: nothing leads to rooms
    ends, spines = ([], []) if dining else _spines(r, building)
    rings = _outlines(r, building)
    corridors = [_rect(*s, corridor / 2) for s in spines]
    entrances = r.get("entrances", [])
    lobbies = [
        dict(_lobby(e, spines, *rings[e["level"]][1:]), level=e["level"])
        for e in entrances
        if not dining
    ]
    cores = [] if dining else _cores(r, ends, spines, lobbies, rings)
    for e, lob in zip(entrances if lobbies else [], lobbies, strict=True):
        why = _blocked(lob, *rings[e["level"]][1:], cores)
        if why:
            raise ValueError(f"{name}: the way in from the entrance at {e['at']} {why}")
    levels = r["levels"]
    top = r["roof"]
    out = []
    for k, lv in enumerate(levels):
        z = lv["floor"]
        outline, inside, lining = rings[lv["level"]]  # a level's own: an upper block, no annex
        # a core runs from the lowest floor to the roof, so it must stand inside every level
        for c in cores:
            if not all(geom.inside(inside, x, y) for x, y in c["ring"]):
                raise ValueError(f"{name}: a {c['kind']} core is outside level {lv['level']}")
        ceiling = levels[k + 1]["floor"] - r.get("slab", SLAB) if k + 1 < len(levels) else top
        here = [lob for lob in lobbies if lob["level"] == lv["level"]]
        toilets = [t for t in r.get("toilets", []) if t["level"] == lv["level"]]
        clear = (
            [c["ring"] for c in cores]
            + [ring for lob in here for ring in lob["rings"]]
            + [[tuple(p[:2]) for p in t["ring"]] for t in toilets]
        )
        tag = f"{name}_F{lv['level']}"
        walls = []
        # the lining: the shell's inner face, open at this level's entrances
        if r.get("lining", True):
            at = [e["at"] for e in entrances if e["level"] == lv["level"]]
            path = closed_path(lining, at)
            doors = [_door(path, x, ENTRANCE, ENTRANCE_HEAD) for x in at]
            run = dict(name=f"SW_{tag}_lining_UNVERIFIED", path=_r(path), thickness=LINING)
            if doors:
                run["openings"] = doors
            walls.append(run)
        open_floor = lv.get("open", r.get("open", False))
        for j, (p, q) in enumerate(spines):
            if open_floor:
                break
            u = _unit(p, q)
            length = math.dist(p, q)
            others = [c for i, c in enumerate(corridors) if i != j]
            keep = clear + others
            # rooms of an earlier spine win: this spine's room walls stay out of them
            taken = [_rect(*spines[i], corridor / 2 + depth) for i in range(j)]
            for side in (1, -1):
                off = side * corridor / 2
                n = (-u[1], u[0])
                a = (p[0] + n[0] * off, p[1] + n[1] * off)
                b = (q[0] + n[0] * off, q[1] + n[1] * off)
                # rooms every `bay` from the spine's start, the last one takes what is left; a
                # door in the middle of each
                marks = [m * bay for m in range(max(1, round(length / bay)))] + [length]
                doors = [
                    ((m0 + m1 - DOOR) / 2, (m0 + m1 + DOOR) / 2)
                    for m0, m1 in zip(marks, marks[1:], strict=False)
                ]
                walls += _runs(
                    f"SW_{tag}_corridor{j}_{'L' if side > 0 else 'R'}",
                    a,
                    b,
                    keep,
                    inside,
                    r.get("partition", rooms.WALL),
                    doors,
                )
                for k_m, m in enumerate(marks):
                    base = (p[0] + u[0] * m + n[0] * off, p[1] + u[1] * m + n[1] * off)
                    tip = (base[0] + n[0] * side * depth, base[1] + n[1] * side * depth)
                    walls += _runs(
                        f"SW_{tag}_room{j}_{k_m}_{'L' if side > 0 else 'R'}",
                        base,
                        tip,
                        keep + taken + [corridors[j]],
                        inside,
                        r.get("partition", rooms.WALL),
                    )
        # lobby side walls, from the entrance to the corridor; a porch's walls stay out of its
        # hall and the hall's out of its porch
        for lob in here:
            if open_floor:
                break
            for part, a, b, s, k_r in lob["sides"]:
                own = lob["rings"][k_r]
                walls += _runs(
                    f"SW_{tag}_lobby_{part}{'a' if s > 0 else 'b'}",
                    a,
                    b,
                    [c["ring"] for c in cores]
                    + corridors
                    + [g for g in lob["rings"] if g is not own],
                    inside,
                    r.get("partition", rooms.WALL),
                )
        # toilets: a closed room with one door, where the entry's evidence puts them; no label (the
        # viewer finds rooms by number only, and a toilet has none)
        for t, toilet in enumerate(toilets):
            ring = [tuple(p[:2]) for p in toilet["ring"]]
            path = closed_path(ring, [toilet["door"]] if "door" in toilet else [])
            run = dict(name=f"SW_{tag}_toilet{t}_UNVERIFIED", path=_r(path), thickness=rooms.WALL)
            if "door" in toilet:
                run["openings"] = [_door(path, toilet["door"], DOOR)]
            walls.append(run)
        labels = [
            dict(number=x["number"], at=x["at"])
            for x in r.get("rooms", [])
            if x["level"] == lv["level"]
        ]
        floor = dict(
            name=tag,
            level=lv["level"],
            floor=z,
            ceiling=round(ceiling, 2),
            evidence=r["evidence"],
            unverified=r["unverified"],
            outline=_r(outline),
            inside=_r(inside),
            keep_out=r.get("keep_out", []),
            walls=walls,
            slabs=[
                dict(
                    name=f"SW_{tag}_slab_UNVERIFIED",
                    ring=_r(inside),
                    z0=round(z - r.get("slab", SLAB), 2),
                    z1=z,
                )
            ],
            blocks=[],
            solids=[],
            rooms=labels,
        )
        if k == 0:  # a core is one closed block from the lowest floor to the roof
            floor["blocks"] = [
                dict(
                    name=f"SW_{name}_{c['kind']}{i}_UNVERIFIED",
                    kind=c["kind"],
                    ring=_r(c["ring"]),
                    z0=z,
                    z1=top,
                )
                for i, c in enumerate(cores)
            ]
        out.append(floor)
    return out


def expand(plan):
    """A plan file's `interiors` and its `rough` entries made into floors, in that order."""
    return list(plan.get("interiors", [])) + [f for r in plan.get("rough", []) for f in floors(r)]

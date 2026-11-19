"""One seamless ground for the southwest build: terrain, paving and turf cut from a single
triangulation.

Every surface outline in the plan is a constraint of one Delaunay triangulation of the footprint, so
neighbouring surfaces share their edge vertices: no overlaps, no gaps and nothing to flicker.
Heights come
from the 3DEP LiDAR ground (class 2) returns, smoothed; near the footprint edge they blend into the
ground
the published tiles already have there, so the seam to the other source models is flush.
"""

import math

import bmesh
import bpy
import geom
import kit
import numpy as np
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from terrain import Terrain, _edge_distance, _inside  # noqa: F401

GRID = 2.0  # spacing of the points that make the ground follow the terrain, metres
# the web export files an object under the tile that holds its centre: one object per tile
TILE = 160.0
LIP = 0.6  # depth of the skirt that closes any crack along the footprint edge
CURB_H, CURB_W = 0.15, 0.15
# base colours, linear RGB. Asphalt without a paint texture is retoned by the viewer (look.js); a
# painted
# sheet carries its own tone (paint.py), chosen to come out the same.
COLOUR = {
    # matched to the neighbouring models' materials as the viewer shows them (look.js):
    # lawn = their grey lawns after the viewer's lawn tint; asphalt above 0.45 comes out at the
    # viewer's top asphalt tone (0.19), the tone of the main model's College Avenue
    "lawn": (0.312, 0.356, 0.184),
    "mulch": (0.09, 0.06, 0.04),
    "gravel": (0.23, 0.21, 0.19),
    "asphalt": (0.5, 0.5, 0.49),
    "turf": (0.03, 0.12, 0.04),
    "concrete": (0.44, 0.43, 0.40),
    "brick": (0.32, 0.11, 0.07),
}
ROUGH = {
    "lawn": 1.0,
    "mulch": 1.0,
    "gravel": 0.95,
    "asphalt": 0.92,
    "turf": 0.9,
    "concrete": 0.85,
    "brick": 0.88,
}
PAVED = {"asphalt", "turf", "concrete", "brick"}


def _densify(ring, step):
    return [(p[0], p[1]) for p in geom.resample(ring, step, True)]


def triangulate(lay):
    """Constrained triangulation of the footprint. Returns (xy array, triangles, surface index per
    triangle).
    """
    foot = _densify(lay["footprint"], GRID)
    pts, edges = [], []

    def add_ring(ring):
        base = len(pts)
        pts.extend(ring)
        edges.extend((base + i, base + (i + 1) % len(ring)) for i in range(len(ring)))

    add_ring(foot)
    for s in lay["surfaces"]:
        add_ring(_densify(s["ring"], GRID))
        for h in s["holes"]:
            add_ring(_densify(h, GRID))
    # terrain-following points on a staggered grid, kept clear of the outlines so no slivers form
    b = geom.bounds(foot)
    cons = np.array(pts)
    cells = {}
    for x, y in cons:
        cells.setdefault((int(x // 1), int(y // 1)), []).append((x, y))
    row = 0
    y = b[1] + GRID / 2
    while y < b[3]:
        x = b[0] + (GRID / 2 if row % 2 else GRID)
        while x < b[2]:
            near = False
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for q in cells.get((int(x // 1) + dx, int(y // 1) + dy), ()):
                        if (q[0] - x) ** 2 + (q[1] - y) ** 2 < 0.49:
                            near = True
            if not near and geom.inside(foot, x, y):
                pts.append((x, y))
            x += GRID
        y += GRID * 0.866
        row += 1
    res = delaunay_2d_cdt([Vector(p) for p in pts], edges, [], 0, 1e-5)
    xy = np.array([(v.x, v.y) for v in res[0]])
    tris = np.array([f for f in res[2] if len(f) == 3], int)
    cx, cy = xy[tris].mean(1).T
    keep = _inside(foot, cx, cy)
    tris, cx, cy = tris[keep], cx[keep], cy[keep]
    owner = np.full(len(tris), -1)  # -1 = base ground (lawn)
    for i, s in enumerate(lay["surfaces"]):  # already sorted by layer: later entries win
        bb = geom.bounds(s["ring"])
        m = (cx >= bb[0]) & (cx <= bb[2]) & (cy >= bb[1]) & (cy <= bb[3])
        if not m.any():
            continue
        idx = np.nonzero(m)[0]
        hit = _inside(s["ring"], cx[idx], cy[idx])
        for h in s["holes"]:
            hit &= ~_inside(h, cx[idx], cy[idx])
        owner[idx[hit]] = i
    return xy, tris, owner


def heights(lay, terrain, xy, tris, owner):
    """
    Vertex heights: smoothed ground on paving, lighter smoothing elsewhere, blended at the footprint
    edge.
    """
    kinds = np.array([lay["surfaces"][o]["kind"] if o >= 0 else "lawn" for o in owner])
    paved = np.zeros(len(xy), bool)
    graded = np.array(
        [o >= 0 and lay["surfaces"][o].get("grade", True) for o in owner]
    )  # a pad on a bank follows the bank
    paved[np.unique(tris[np.isin(kinds, list(PAVED)) & graded])] = True
    return terrain.surface(xy[:, 0], xy[:, 1], paved)


def build(lay, terrain, image_dir=None):
    """Make the ground objects (one per kind, verified and UNVERIFIED apart). Returns them."""
    xy, tris, owner = triangulate(lay)
    z = heights(lay, terrain, xy, tris, owner)
    groups = {}
    for t, o in zip(tris, owner, strict=True):
        s = lay["surfaces"][o] if o >= 0 else dict(kind="lawn", name="Ground", sheets=None)
        cx, cy = xy[t].mean(0)
        key = (s["kind"], bool(s.get("unverified")), math.floor(cx / TILE), math.floor(cy / TILE))
        groups.setdefault(key, []).append((t, s))
    # triangles on the footprint edge get a skirt: an edge used by one triangle only
    count = {}
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            count[(min(a, b), max(a, b))] = count.get((min(a, b), max(a, b)), 0) + 1
    objects = []
    for (kind, unverified, tx, ty), items in sorted(groups.items()):
        name = f"SW_ground_{kind}_{tx}_{ty}" + ("_UNVERIFIED" if unverified else "")
        bm = bmesh.new()
        uv = bm.loops.layers.uv.new("UVMap")
        mats, vmap = [], {}

        def vert(i, bm=bm, vmap=vmap):
            if i not in vmap:
                vmap[i] = bm.verts.new((xy[i, 0], xy[i, 1], z[i]))
            return vmap[i]

        def slot(material, mats=mats):
            if material not in mats:
                mats.append(material)
            return mats.index(material)

        plain = kit.mat(kind, "base", COLOUR[kind], ROUGH[kind])
        for t, s in items:
            # anticlockwise seen from above, so the face looks up and its skirt looks outward
            (ax, ay), (bx, by), (cx, cy) = xy[t]
            if (bx - ax) * (cy - ay) - (by - ay) * (cx - ax) < 0:
                t = t[::-1]
            face = bm.faces.new([vert(i) for i in t])
            face.smooth = True
            sheet = None
            if s.get("sheets"):
                to_local = geom.frame((0.0, 0.0), s["sheets"][0]["angle"])[0]
                cu = to_local(*xy[t].mean(0))[0]
                sheet = next(
                    (sh for sh in s["sheets"] if sh["cut0"] <= cu <= sh["cut1"]), s["sheets"][-1]
                )
                for loop, i in zip(face.loops, t, strict=True):
                    u, v = to_local(xy[i, 0], xy[i, 1])
                    loop[uv].uv = (
                        (u - sheet["u0"]) / (sheet["u1"] - sheet["u0"]),
                        (v - sheet["v0"]) / (sheet["v1"] - sheet["v0"]),
                    )
            face.material_index = slot(sheet_material(kind, sheet, image_dir) if sheet else plain)
            for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                if count[(min(a, b), max(a, b))] == 1:  # outer edge: skirt down, facing outward
                    lo = [bm.verts.new((xy[i, 0], xy[i, 1], z[i] - LIP)) for i in (a, b)]
                    lip = bm.faces.new([vert(b), vert(a), lo[0], lo[1]])
                    lip.material_index = slot(plain)
                    # where the neighbour's ground stands higher (a bank beside a road), a face up
                    # to
                    # it, seen from this side: without it you would look under the neighbour's edge
                    up = terrain.neighbour_z(xy[[a, b], 0], xy[[a, b], 1])
                    if np.isfinite(up).all() and (up - z[[a, b]]).max() > 0.05:
                        hi = [
                            bm.verts.new((xy[i, 0], xy[i, 1], max(z[i], h) + 0.02))
                            for i, h in zip((a, b), up, strict=True)
                        ]
                        bank = bm.faces.new([vert(a), vert(b), hi[1], hi[0]])
                        bank.material_index = slot(
                            kit.mat("lawn", "bank_edge", COLOUR["lawn"], 1.0)
                        )
        # no recalc_face_normals here: on an open sheet it flips whole patches face down
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        for m in mats:
            me.materials.append(m)
        ob = bpy.data.objects.new(name, me)
        kit.collection().objects.link(ob)
        objects.append(ob)
    objects.extend(curbs(lay, terrain))
    return objects


def sheet_material(kind, sheet, image_dir):
    """Material that shows one authored paint sheet through the UV map."""
    m = kit.mat(kind, sheet["name"].replace("authored_", "painted_"), COLOUR[kind], ROUGH[kind])
    nt = m.node_tree
    if image_dir and not any(n.type == "TEX_IMAGE" for n in nt.nodes):
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(f"{image_dir}/{sheet['name']}.png", check_existing=True)
        nt.links.new(tex.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    return m


def curbs(lay, terrain):
    """Sweep a 0.15 m curb along every curb line, on the side away from the carriageway."""
    asphalt = [s for s in lay["surfaces"] if s["kind"] == "asphalt"]

    def on_road(x, y):
        return any(geom.inside(s["ring"], x, y) for s in asphalt)

    out = {}
    for c in lay["curbs"]:
        line = c["line"]
        closed = c.get("closed", False)
        pts = geom.resample(line, 1.5, closed)
        if closed:
            pts.append(pts[0])
        mid = pts[len(pts) // 2]
        nxt = pts[min(len(pts) - 1, len(pts) // 2 + 1)]
        prv = pts[len(pts) // 2 - 1]
        tx, ty = nxt[0] - prv[0], nxt[1] - prv[1]
        ln = math.hypot(tx, ty) or 1.0
        left = (-ty / ln, tx / ln)
        # the curb body goes to the side that is not carriageway
        side = (
            -1.0
            if on_road(mid[0] + left[0] * 0.4, mid[1] + left[1] * 0.4)
            and not on_road(mid[0] - left[0] * 0.4, mid[1] - left[1] * 0.4)
            else 1.0
        )
        dense = [(p[0], p[1]) for p in pts]
        if closed:  # offset the ring as a ring, so its two ends get the same normal and meet
            back = geom.offset(dense[:-1], side * CURB_W, True)
            back.append(back[0])
        else:
            back = geom.offset(dense, side * CURB_W, False)
        kind = c.get("kind", "concrete")
        key = (kind, bool(c.get("unverified")))
        b = out.get(key)
        if b is None:
            b = out[key] = kit.Builder(f"SW_curbs_{kind}" + ("_UNVERIFIED" if key[1] else ""))
        m = kit.mat(
            "concrete" if kind == "concrete" else "stone",
            f"curb_{kind}",
            (0.40, 0.39, 0.37) if kind == "concrete" else (0.45, 0.44, 0.43),
            0.8,
        )
        zf = terrain.surface(np.array([p[0] for p in dense]), np.array([p[1] for p in dense]), True)
        verts, faces = [], []
        for i, (f, bk) in enumerate(zip(dense, back, strict=True)):
            verts += [
                (f[0], f[1], zf[i] - 0.05),
                (f[0], f[1], zf[i] + CURB_H),
                (bk[0], bk[1], zf[i] + CURB_H),
                (bk[0], bk[1], zf[i] - 0.05),
            ]
            if i:
                a, d = (i - 1) * 4, i * 4
                quads = [
                    (a, d, d + 1, a + 1),
                    (a + 1, d + 1, d + 2, a + 2),
                    (a + 2, d + 2, d + 3, a + 3),
                ]
                faces += quads if side > 0 else [q[::-1] for q in quads]
        n = len(dense)
        if not closed:  # end caps
            faces += [
                (0, 1, 2, 3) if side > 0 else (3, 2, 1, 0),
                ((n - 1) * 4 + 3, (n - 1) * 4 + 2, (n - 1) * 4 + 1, (n - 1) * 4)
                if side > 0
                else ((n - 1) * 4, (n - 1) * 4 + 1, (n - 1) * 4 + 2, (n - 1) * 4 + 3),
            ]
        b.faces(verts, faces, m)
    return [b.finish(weld=0.0) for b in out.values()]

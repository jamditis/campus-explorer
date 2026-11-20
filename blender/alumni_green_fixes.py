"""Corrections to the main model's Alumni Green plaza in front of Susan A. Cole Hall, from Joe's
three photographs of 2026-11-20 (1000102881 to 1000102883). Run on a copy of the main .blend,
headless, and save under a new name (AGENTS.md):

    blender -b MAIN.blend --python blender/alumni_green_fixes.py -- OUT.blend [--dry-run]

What it changes, all inside the plaza that session ws5 built (WS5_Cole_plaza_circle_quatrefoil_
20261109, centre C, radius R, gable axis ANG from ws5/shape.py), which keeps its outline:

- The paver field is red-brown herringbone brick pavers (photos 1 and 2), not grey pavers.
- The light concrete band is a ring with four pointed tips on the diagonals of the gable axis
  (photo 2), not four round lobes. Sizes from photo 2 and the 2025 Esri image: UNVERIFIED, 0.5 m.
- New: the "ALUMNI GREEN" stone inlay in the brick edge course on the north side, the steel
  access hatch beside it, and a black fluted lamp post with an acorn globe on the lawn just
  outside the edge (photos 1 and 2). Positions are relations read from the photos (inlay on the
  gable axis, hatch and lamp west of it), not measurements: UNVERIFIED, about 1.5 m.

Larger corrections that need the plaza and its walks laid out again are listed in LATER.
"""

import math
import sys

# The ws5 plaza (blender/montclair-state/scripts/ws5/shape.py).
C = (-107.0, -50.5)
R = 9.5  # plaza radius
RING = 0.6  # brick edge course
ANG = -13.5  # gable axis (degrees anticlockwise from east): u along the face, v out of it

# Band (photo 2, ground mapped from a camera fitted to the Cole Hall gable; Esri 2025 band
# about 9.2 m tip to tip). UNVERIFIED, 0.5 m.
BAND_IN, BAND_OUT, BAND_TIP = 3.45, 4.0, 4.9
TIP_HALF = 8.0  # degrees: where a tip's straight flanks meet the outer circle
ARC_STEP = 360 / 256  # the arc resolution ws5 used (shapely resolution 64)

# Inlay: four light stone tiles with black letters, about 3.6 x 0.45 m (photo 1: each tile is
# about four and a half paver lengths). On the gable axis (photo 2: about 12 degrees east of
# north from the band centre; the axis points 13.5).
INLAY_LEN, INLAY_DEPTH = 3.6, 0.45
INLAY_R = R - RING / 2 - 0.05
INLAY_TEXT, INLAY_TEXT_H = "ALUMNI GREEN", 0.24

HATCH = (1.25, 0.95)  # metres, long side along the edge
HATCH_R, HATCH_DA = 8.0, 14.0  # 14 degrees west of the inlay (photo 2: az 358 vs 12)
LAMP_R, LAMP_DA = R + 0.8, 20.0  # on the lawn, 20 degrees west of the inlay (photo 2: az 352)

LATER = [
    "Plaza position: photo 2 (camera fitted to the Cole Hall gable, the ws5 north addition) puts "
    "the band centre about 6 m in front of the doors, its far tips 2 to 3 m from the face; the "
    "2025 Esri image puts it at about (-105, -55.5). The model has it 11 m out, at (-107, -50.5). "
    "Move the plaza about 5 m toward the doors, to about (-104.4, -56.0) +-1.5 m, radius about "
    "7.8 m +-0.7 (photo 2: inlay at the edge 7.3 to 7.8 m from the band centre), and run the "
    "north-west and north-east walks (WS3_Cole_plaza_paving_20261109) on to the new edge; lawn "
    "where the old north cap was. Photo 1 agrees within its error (the library's arched bay "
    "seen about 20 degrees east of north from about 40 m). The move rests on one photo and an "
    "image with 8 m stated accuracy: pace doors to band and doors to inlay on site first.",
    "Sprague Library south face (photo 1): the model's walls are dark red brick; the photo shows "
    "buff brick on the arched bay and the east block, red brick only on the west end. A row of "
    "about nine young conifers and six benches stands along its foot (model: none).",
    "Cole Hall north addition (TZ_Cole_north_addition_UNVERIFIED, WS6, WS7): photo 2 shows the "
    "arched window over the doors about 6 m wide (model 3.5 m), the eave about 2 m higher than "
    "142.9, a tall window either side, two black lanterns beside the doors and the name "
    "'SUSAN A. COLE HALL' in black on a light band over them.",
    "Boulder with a bronze plaque (about 1.5 to 2.5 m wide, 1 to 1.6 m high) and a row of "
    "slender white string-light poles among small trees west of the plaza, toward the Kasser "
    "steps (photo 3). No source gives their position closer than about 5 m.",
]


def L(pu, pv):
    """Plaza frame (u along the gable face, v out of it) to model x, y."""
    a = math.radians(ANG)
    return (
        C[0] + pu * math.cos(a) - pv * math.sin(a),
        C[1] + pu * math.sin(a) + pv * math.cos(a),
    )


def polar(r, deg):
    """Point at radius r from C, at model angle deg (anticlockwise from east)."""
    a = math.radians(deg)
    return (C[0] + r * math.cos(a), C[1] + r * math.sin(a))


def _arc(r, a0, a1):
    """Points on the circle r from angle a0 to a1 (degrees, a1 > a0), ends included."""
    n = max(1, math.ceil((a1 - a0) / ARC_STEP))
    return [polar(r, a0 + (a1 - a0) * i / n) for i in range(n + 1)]


def band_rings():
    """(outer, inner) rings of the band: outer circle BAND_OUT with four pointed tips at
    BAND_TIP on the diagonals of the gable axis, inner circle BAND_IN. Anticlockwise lists."""
    tips = [ANG + a for a in (45, 135, 225, 315)]
    outer = []
    for i, t in enumerate(tips):
        nxt = tips[(i + 1) % 4] + (360 if i == 3 else 0)
        outer.append(polar(BAND_TIP, t))
        outer += _arc(BAND_OUT, t + TIP_HALF, nxt - TIP_HALF)
    inner = _arc(BAND_IN, 0, 360)[:-1]
    return outer, inner


def hole_square():
    """Integer square (x0, y0, x1, y1) round the band: the ws5 field pieces are cut on the
    whole-metre grid, so deleting the pieces inside it leaves exactly this hole."""
    m = BAND_TIP + 0.6
    return (
        math.floor(C[0] - m),
        math.floor(C[1] - m),
        math.ceil(C[0] + m),
        math.ceil(C[1] + m),
    )


def bend(x, y, r0, th0):
    """Text plane (x along the reading direction, y toward the top of the letters) onto the
    circle r0 round C: x = 0 sits at angle th0 (radians); the reader stands inside facing out,
    so reading runs clockwise and the letters' tops point away from C."""
    th = th0 - x / r0
    r = r0 + y
    return (C[0] + r * math.cos(th), C[1] + r * math.sin(th))


def arc_strip(r0, depth, th0, length, step):
    """Inner then outer row of points of a strip `depth` wide, centred on circle r0 at angle
    th0 (radians), `length` long along the arc, cut every `step` metres or less."""
    n = max(1, math.ceil(length / step))
    rows = []
    for r in (r0 - depth / 2, r0 + depth / 2):
        for i in range(n + 1):
            th = th0 + length / (2 * r0) - (length / r0) * i / n
            rows.append((C[0] + r * math.cos(th), C[1] + r * math.sin(th)))
    return rows


def bilinear(corner, x, y):
    """Height at (x, y) from the heights corner(ix, iy) at the whole-metre grid corners round it:
    every new vertex in a 1 m cell then lies on one smooth patch, so thin triangles shade evenly."""
    ix, iy = math.floor(x), math.floor(y)
    fx, fy = x - ix, y - iy
    return (
        corner(ix, iy) * (1 - fx) * (1 - fy)
        + corner(ix + 1, iy) * fx * (1 - fy)
        + corner(ix, iy + 1) * (1 - fx) * fy
        + corner(ix + 1, iy + 1) * fx * fy
    )


def places():
    """name -> (x, y, heading in degrees): inlay centre, hatch centre, lamp foot."""
    ax = ANG + 90  # the gable axis, out of the face
    ix, iy = polar(INLAY_R, ax)
    hx, hy = polar(HATCH_R, ax + HATCH_DA)
    lx, ly = polar(LAMP_R, ax + LAMP_DA)
    return {
        "inlay": (ix, iy, ax - 90),
        "hatch": (hx, hy, ax + HATCH_DA - 90),
        "lamp": (lx, ly, 0.0),
    }


# ---------------------------------------------------------------- Blender part

PLAZA = "WS5_Cole_plaza_circle_quatrefoil_20261109"
LAMP_SRC = "Lamp_acorn_017"
COLL = "GRN_alumni_green_20261120"
PAVERS = "GRN_Plaza_pavers_herringbone_redbrown_JOEphoto_20261120"
# Inlay and hatch stand this much proud of the graded plaza top, so the brick course under them
# (cut in 1 m pieces at their own heights) does not show through.
LIFT = 0.02
EVIDENCE = "Joe's photos 1000102881..83 (2026-11-20); Esri World Imagery 2025-05-11"


def _material(bpy, name, rgb, rough=0.85, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*rgb, 1.0)
    return m


def _surface(plaza):
    """z of the plaza top under (x, y): a vertical ray on the unchanged ws5 mesh."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    mw = plaza.matrix_world
    vs = [mw @ v.co for v in plaza.data.vertices]
    tree = BVHTree.FromPolygons(vs, [list(p.vertices) for p in plaza.data.polygons])

    def z(x, y):
        hit = tree.ray_cast(Vector((x, y, 400.0)), Vector((0, 0, -1)))
        if hit[0] is not None:
            return hit[0].z
        near = tree.find_nearest(Vector((x, y, 134.0)))
        return near[0].z

    return z


def _fill(bm, rings, mat, verts_z):
    """Triangles filling the rings (first outer, then holes) with material index mat."""
    from mathutils.geometry import tessellate_polygon

    flat = [[(x, y, 0.0) for x, y in r] for r in rings]
    pts = [p for r in flat for p in r]
    vs = [bm.verts.new((x, y, verts_z(x, y))) for x, y, _ in pts]
    faces = []
    for tri in tessellate_polygon(flat):
        try:
            f = bm.faces.new([vs[i] for i in tri])
        except ValueError:
            continue
        f.material_index = mat
        faces.append(f)
    return faces


def rebuild_plaza(bpy, plaza):
    """Herringbone field material; band rebuilt inside the hole square, cut on the 1 m grid."""
    import bmesh
    from mathutils import Vector

    z = _surface(plaza)
    me = plaza.data
    slots = [s.material.name if s.material else None for s in plaza.material_slots]
    print("plaza slots", slots)
    plaza.material_slots[0].material = _material(bpy, PAVERS, (0.29, 0.17, 0.12))
    bm = bmesh.new()
    bm.from_mesh(me)
    inv = plaza.matrix_world.inverted()
    x0, y0, x1, y1 = hole_square()
    gone = []
    for f in bm.faces:
        c = plaza.matrix_world @ f.calc_center_median()
        if f.material_index in (0, 2) and x0 < c.x < x1 and y0 < c.y < y1:
            gone.append(f)
    bmesh.ops.delete(bm, geom=gone, context="FACES")
    outer, inner = band_rings()
    square = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    new = _fill(bm, [square, outer], 0, z)
    new += _fill(bm, [outer, inner], 2, z)
    new += _fill(bm, [inner], 0, z)
    geom = list({v for f in new for v in f.verts}) + list({e for f in new for e in f.edges})
    geom += new
    for gx in range(x0 + 1, x1):
        r = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(gx, 0, 0), plane_no=(1, 0, 0))
        geom = list({*geom, *r["geom"]})
    for gy in range(y0 + 1, y1):
        r = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, gy, 0), plane_no=(0, 1, 0))
        geom = list({*geom, *r["geom"]})
    corners = {}

    def corner(ix, iy):
        if (ix, iy) not in corners:
            corners[ix, iy] = z(ix, iy)
        return corners[ix, iy]

    for v in {g for g in geom if isinstance(g, bmesh.types.BMVert) and g.is_valid}:
        w = v.co.copy()
        v.co = inv @ Vector((w.x, w.y, bilinear(corner, w.x, w.y)))
    bm.to_mesh(me)
    bm.free()
    me.update()
    print(f"plaza: {len(gone)} pieces removed in {(x0, y0, x1, y1)}, band rebuilt")
    return z


def _mesh_object(bpy, coll, name, verts, faces, mats):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    ob["evidence"] = EVIDENCE
    coll.objects.link(ob)
    return ob


def add_inlay(bpy, coll, z):
    th0 = math.radians(ANG + 90)
    pts = arc_strip(INLAY_R, INLAY_DEPTH, th0, INLAY_LEN, 0.1)
    n = len(pts) // 2
    verts = [(x, y, z(x, y) + LIFT) for x, y in pts]
    faces = [(i, i + 1, n + i + 1, n + i) for i in range(n - 1)]
    stone = _material(bpy, "GRN_inlay_limestone_light", (0.78, 0.76, 0.70), 0.7)
    _mesh_object(bpy, coll, "GRN_AlumniGreen_inlay_tiles_UNVERIFIED", verts, faces, [stone])
    # letters: Blender's own sans font, converted to a mesh and bent onto the arc
    cu = bpy.data.curves.new("GRN_inlay_text", "FONT")
    cu.body = INLAY_TEXT
    cu.size = INLAY_TEXT_H / 0.72  # cap height of Bfont is about 0.72 of its size
    cu.space_character = 1.6
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    tob = bpy.data.objects.new("GRN_inlay_text_tmp", cu)
    coll.objects.link(tob)
    dg = bpy.context.evaluated_depsgraph_get()
    tm = bpy.data.meshes.new_from_object(tob.evaluated_get(dg))
    bpy.data.objects.remove(tob)
    bpy.data.curves.remove(cu)
    xs = [v.co.x for v in tm.vertices]
    scale = min(1.0, (INLAY_LEN - 0.3) / (max(xs) - min(xs)))
    for v in tm.vertices:
        x, y = bend(v.co.x * scale, v.co.y, INLAY_R, th0)
        v.co = (x, y, z(x, y) + LIFT + 0.004)
    tm.name = "GRN_AlumniGreen_inlay_letters_UNVERIFIED"
    tm.materials.append(_material(bpy, "GRN_inlay_letters_black", (0.03, 0.03, 0.03), 0.6))
    ob = bpy.data.objects.new(tm.name, tm)
    ob["evidence"] = EVIDENCE
    coll.objects.link(ob)


def add_hatch(bpy, coll, z):
    x, y, hd = places()["hatch"]
    a = math.radians(hd)
    ca, sa = math.cos(a), math.sin(a)
    verts, faces = [], []
    sizes = ((HATCH[0], HATCH[1], LIFT), (HATCH[0] - 0.08, HATCH[1] - 0.08, LIFT + 0.004))
    for k, (w, d, dz) in enumerate(sizes):
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            px, py = sx * w / 2, sy * d / 2
            wx, wy = x + px * ca - py * sa, y + px * sa + py * ca
            verts.append((wx, wy, z(wx, wy) + dz))
        faces.append((4 * k, 4 * k + 1, 4 * k + 2, 4 * k + 3))
    frame = _material(bpy, "GRN_hatch_frame_steel", (0.42, 0.42, 0.40), 0.5, 0.8)
    plate = _material(bpy, "GRN_hatch_plate_steel_dark", (0.10, 0.10, 0.10), 0.55, 0.8)
    ob = _mesh_object(bpy, coll, "GRN_access_hatch_UNVERIFIED", verts, faces, [frame, plate])
    ob.data.polygons[1].material_index = 1


def add_lamp(bpy, coll, z):
    src = bpy.data.objects.get(LAMP_SRC)
    if src is None:
        print("missing", LAMP_SRC, ": no lamp added")
        return
    x, y, _ = places()["lamp"]
    ob = src.copy()  # shares the mesh, like the other acorn lamps
    ob.name = "GRN_Lamp_acorn_fluted_N_UNVERIFIED"
    ob.location = (x, y, z(x, y) - 0.02)
    ob["evidence"] = EVIDENCE
    coll.objects.link(ob)


def main():
    import bpy

    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    dry = "--dry-run" in args
    plaza = bpy.data.objects.get(PLAZA)
    if plaza is None:
        sys.exit(f"{PLAZA} not in this file")
    for k, v in places().items():
        print(f"{k}: x {v[0]:.2f} y {v[1]:.2f} heading {v[2]:.1f}")
    for note in LATER:
        print("later:", note)
    if dry:
        print("dry run: nothing changed")
        return
    coll = bpy.data.collections.get(COLL) or bpy.data.collections.new(COLL)
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    z = rebuild_plaza(bpy, plaza)
    add_inlay(bpy, coll, z)
    add_hatch(bpy, coll, z)
    add_lamp(bpy, coll, z)
    out = [a for a in args if not a.startswith("--")]
    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out[0], compress=True)
        print("saved", out[0])


if __name__ == "__main__":
    main()

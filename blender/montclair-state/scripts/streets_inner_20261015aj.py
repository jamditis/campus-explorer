"""tag 20261015aj (RERUNNABLE, --save). OSM street ribbons for the inner 0.45-1.6 km band of the CCOM lab
view wedge (data/ccom_mid_distance/aj/streets_inner_20261015aj.json). Same widths/drape/asphalt as ae/ag.
Clipped: outside the campus boundary (+15 m) and the LiDAR/Roads_OSM tile (|x|,|y|<260), and portions of
ways already drawn by ae/ag (same osm_id inside their bbox+100) are skipped to avoid doubled ribbons.
Collection MID_streets_inner_20261015aj. Centreline ACCURATE-to-OSM; widths UNVERIFIED. No markings/lamps."""
import bpy, bmesh, json, math, os, sys
from mathutils import Vector
TAG = "20261015aj"; SAVE = "--save" in sys.argv
ROOT = bpy.path.abspath("//"); DD = os.path.join(ROOT, "data/ccom_mid_distance")
D = json.load(open(os.path.join(DD, "aj/streets_inner_20261015aj.json")))
CX, CY = D["cam"]
W = {"primary": (13.0, 0.16), "secondary": (11.0, 0.15), "tertiary": (9.0, 0.14),
     "residential": (7.5, 0.12), "unclassified": (7.0, 0.12), "living_street": (6.0, 0.12)}
prior = []
for f in ("ae/streets_20261015ae.json", "ag/streets_far_20261015ag.json"):
    P = json.load(open(os.path.join(DD, f))); bx = P["bbox_local_m"]
    prior.append(({w["osm_id"] for w in P["ways"]}, bx))
poly = json.load(open(os.path.join(ROOT, "north/data/boundary.json")))["polygon_blender_m"]
def in_poly(x, y):
    c = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c
def near_poly(x, y, m=15.0):
    if in_poly(x, y): return True
    for dx, dy in ((m, 0), (-m, 0), (0, m), (0, -m)):
        if in_poly(x + dx, y + dy): return True
    return False
def keep(p, oid):
    x, y = p
    if abs(x) < 260 and abs(y) < 260: return False
    r = math.hypot(x - CX, y - CY); b = math.degrees(math.atan2(y - CY, x - CX))
    if not (380 <= r <= 1700 and -78 <= b <= 8): return False
    if near_poly(x, y): return False
    for ids, (a0, b0, a1, b1) in prior:
        if oid in ids and a0 - 100 <= x <= a1 + 100 and b0 - 100 <= y <= b1 + 100: return False
    return True
gobs = [bpy.data.objects[n] for n in ("Context_skirt_3DEP_ortho_4km", "BD_farfield_3DEP_ortho") if n in bpy.data.objects]
gi = [(o, o.matrix_world.inverted()) for o in gobs]
def gz(x, y):
    best = None
    for o, mi in gi:
        ok, loc, *_ = o.ray_cast(mi @ Vector((x, y, 3000)), (mi.to_3x3() @ Vector((0, 0, -1))).normalized())
        if ok:
            z = (o.matrix_world @ loc).z; best = z if best is None else max(best, z)
    return best
bm = bmesh.new(); nruns = 0; length = 0.0; cls = {}
for w in D["ways"]:
    wd, dz = W.get(w["highway"], (7.0, 0.12))
    runs, cur = [], []
    for p in w["line_local_m"]:
        if keep(p, w["osm_id"]): cur.append(Vector(p))
        elif cur: runs.append(cur); cur = []
    if cur: runs.append(cur)
    for run in runs:
        if len(run) < 2: continue
        pts = [run[0]]
        for a, b in zip(run, run[1:]):
            n = max(1, int((b - a).length // 6.0))
            for i in range(1, n + 1): pts.append(a.lerp(b, i / n))
            length += (b - a).length
        L = []; R = []
        for i, p in enumerate(pts):
            t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)])
            if t.length < 1e-6: t = Vector((1, 0))
            t.normalize(); nrm = Vector((-t.y, t.x)) * (wd / 2)
            ql, qr = p + nrm, p - nrm
            zl = gz(ql.x, ql.y); zr = gz(qr.x, qr.y); zc = gz(p.x, p.y)
            zz = [z for z in (zl, zr, zc) if z is not None] or [0.0]
            zm = max(zz)
            L.append(bm.verts.new((ql.x, ql.y, (zl if zl is not None else zm) + dz)))
            R.append(bm.verts.new((qr.x, qr.y, (zr if zr is not None else zm) + dz)))
        for i in range(len(pts) - 1):
            bm.faces.new((L[i], R[i], R[i + 1], L[i + 1]))
        nruns += 1; cls[w["highway"]] = cls.get(w["highway"], 0) + 1
name = f"MID_streets_inner_{TAG}"
col = bpy.data.collections.get(name) or bpy.data.collections.new(name)
if col.name not in bpy.context.scene.collection.children:
    bpy.context.scene.collection.children.link(col)
old = bpy.data.objects.get(name)
me = bpy.data.meshes.new(name + "_me"); bm.normal_update(); bm.to_mesh(me); bm.free()
for p in me.polygons:
    if p.normal.z < 0: p.flip()
if old:
    om = old.data; old.data = me; bpy.data.meshes.remove(om); ob = old
else:
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
mat = bpy.data.materials.get("MID_street_asphalt_20261015ag")
me.materials.clear(); me.materials.append(mat)
ob["status"] = "OSM centreline ACCURATE-to-OSM; width UNVERIFIED"; col["TAG"] = TAG
ob.visible_shadow = False
print("INNER_STREETS runs", nruns, cls, "len_km", round(length / 1000, 2), "faces", len(me.polygons))
if SAVE: bpy.ops.wm.save_mainfile(); print("SAVED")

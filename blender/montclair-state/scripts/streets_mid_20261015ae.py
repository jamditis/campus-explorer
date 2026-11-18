"""tag 20261015ae (RERUNNABLE, --save). OSM street ribbons for the 1.5-3.5 km ESE neighbourhood
(data/ccom_mid_distance/ae/streets_20261015ae.json, Overpass, (c) OSM contributors, EPSG:6527 same origin).
Centreline ACCURATE-to-OSM; widths by class UNVERIFIED (primary 13 / secondary 11 / tertiary 9 / residential 7.5 / unclassified 7 m).
One merged mesh, resampled every 8 m, draped on topmost skirt/farfield hit + class offset (0.12-0.16 m).
No lamps, no markings, no street furniture."""
import bpy, bmesh, json, math, os, sys
from mathutils import Vector
TAG = "20261015ae"; SAVE = "--save" in sys.argv
ROOT = bpy.path.abspath("//")
D = json.load(open(os.path.join(ROOT, "data/ccom_mid_distance/ae/streets_20261015ae.json")))
W = {"primary": (13.0, 0.16), "secondary": (11.0, 0.15), "tertiary": (9.0, 0.14), "residential": (7.5, 0.12), "unclassified": (7.0, 0.12), "living_street": (6.0, 0.12)}
x0, y0, x1, y1 = D["bbox_local_m"]
gobs = [bpy.data.objects[n] for n in ("Context_skirt_3DEP_ortho_4km", "BD_farfield_3DEP_ortho") if n in bpy.data.objects]
def gz(x, y):
    best = None
    for o in gobs:
        mi = o.matrix_world.inverted()
        ok, loc, *_ = o.ray_cast(mi @ Vector((x, y, 3000)), (mi.to_3x3() @ Vector((0, 0, -1))).normalized())
        if ok:
            z = (o.matrix_world @ loc).z; best = z if best is None else max(best, z)
    return best
def inside(p): return x0 - 100 <= p[0] <= x1 + 100 and y0 - 100 <= p[1] <= y1 + 100
bm = bmesh.new(); nways = 0; nverts = 0; length = 0.0
for w in D["ways"]:
    wd, dz = W.get(w["highway"], (7.0, 0.12))
    # split into runs inside the bbox
    runs, cur = [], []
    for p in w["line_local_m"]:
        if inside(p): cur.append(Vector(p))
        elif cur: runs.append(cur); cur = []
    if cur: runs.append(cur)
    for run in runs:
        if len(run) < 2: continue
        pts = [run[0]]
        for a, b in zip(run, run[1:]):
            n = max(1, int((b - a).length // 8.0))
            for i in range(1, n + 1): pts.append(a.lerp(b, i / n))
            length += (b - a).length
        L = []; R = []
        for i, p in enumerate(pts):
            t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)])
            if t.length < 1e-6: t = Vector((1, 0))
            t.normalize(); nrm = Vector((-t.y, t.x)) * (wd / 2)
            ql, qr = p + nrm, p - nrm
            zl = gz(ql.x, ql.y); zr = gz(qr.x, qr.y); zc = gz(p.x, p.y)
            zz = [z for z in (zl, zr, zc) if z is not None]
            if not zz: zz = [0.0]
            zm = max(zz) + dz
            L.append(bm.verts.new((ql.x, ql.y, (zl if zl is not None else zm - dz) + dz)))
            R.append(bm.verts.new((qr.x, qr.y, (zr if zr is not None else zm - dz) + dz)))
        for i in range(len(pts) - 1):
            bm.faces.new((L[i], R[i], R[i + 1], L[i + 1]))
        nways += 1; nverts += 2 * len(pts)
name = f"MID_streets_{TAG}"
col = bpy.data.collections.get(name) or bpy.data.collections.new(name)
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
old = bpy.data.objects.get(name)
me = bpy.data.meshes.new(name + "_me"); bm.normal_update(); bm.to_mesh(me); bm.free()
for p in me.polygons:
    if p.normal.z < 0: p.flip()
if old:
    om = old.data; old.data = me; bpy.data.meshes.remove(om); ob = old
else:
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
mat = bpy.data.materials.get(f"MID_street_asphalt_{TAG}") or bpy.data.materials.new(f"MID_street_asphalt_{TAG}")
mat.use_nodes = True; b = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
b.inputs["Base Color"].default_value = (0.055, 0.055, 0.058, 1.0); b.inputs["Roughness"].default_value = 0.95
me.materials.clear(); me.materials.append(mat)
ob["status"] = "OSM centreline ACCURATE-to-OSM; width UNVERIFIED"; col["TAG"] = TAG
ob.visible_shadow = False
print("STREETS runs", nways, "verts", nverts, "len_km", round(length / 1000, 1), "faces", len(me.polygons))
if SAVE: bpy.ops.wm.save_mainfile(); print("SAVED")

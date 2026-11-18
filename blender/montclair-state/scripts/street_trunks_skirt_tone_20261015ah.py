"""tag 20261015ah (RERUNNABLE, --save).
(1) Street trees (MID_street_trees_20261015ag): lift crowns onto trunks (crown bottom ~2.2-2.8 m
    above drape), shared low-poly trunk mesh (tapered 6-sided cylinder, bark mat), crown proto
    upgraded ico sub1 -> sub2 with deterministic vertex jitter (shared mesh, 233 users).
    Trunk height/girth UNVERIFIED (typical NJ street tree); xy unchanged (13 OSM ACCURATE, 220 UNVERIFIED).
(2) Skirt ortho lawn tone: distance-ramped HSV on Context_skirt_ortho so the 1-2 km band matches the
    darker/greener BD_farfield ortho (seam seen in ag oblique) while the campus-boundary end stays as-is.
    Ramp r_xy 800 m -> 1600 m: Value 0.85 -> 0.58, Saturation 1.00 -> 1.12 (then /tmp/ah_tone2.py -> V 0.42, S 1.22 after first WIP: seam still visible). Non-destructive (node values only).
No lamps / no furniture / no world change.
"""
import bpy, bmesh, math, random, sys
from mathutils import Vector, noise
TAG = "20261015ah"
SAVE = "--save" in sys.argv
rng = random.Random(2026101503)
col = bpy.data.collections["MID_street_trees_20261015ag"]
crowns = [o for o in col.objects if o.name.startswith("MID_stree_")]
print("crowns", len(crowns), flush=True)
proto = bpy.data.objects["MID_street_tree_proto_20261015ag"]

# --- crown mesh upgrade (sub2 + jitter), keep material ---
me = proto.data
if not me.get("ah_upgraded"):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    for v in bm.verts:
        n = noise.noise(v.co * 1.7 + Vector((3.1, 7.7, 1.3)))
        v.co *= 1.0 + 0.14 * n
        if v.co.z < -0.55:
            v.co.z = -0.55 - (v.co.z + 0.55) * 0.35  # flatten underside a little (canopy base)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = False
    me["ah_upgraded"] = 1
zmin_local = min(v.co.z for v in me.vertices)
print("crown zmin_local", round(zmin_local, 3), flush=True)

# --- ground drape (exclude trees) ---
gobs = [bpy.data.objects[n] for n in ("Context_skirt_3DEP_ortho_4km", "BD_farfield_3DEP_ortho",
        "Context_ground_beyond_data") if n in bpy.data.objects]
def gz(x, y):
    best = None
    for o in gobs:
        mi = o.matrix_world.inverted()
        ok, loc, *_ = o.ray_cast(mi @ Vector((x, y, 3000)), (mi.to_3x3() @ Vector((0, 0, -1))).normalized())
        if ok:
            z = (o.matrix_world @ loc).z
            best = z if best is None else max(best, z)
    return best

# --- trunk proto / material ---
TM = f"MID_street_trunk_bark_{TAG}"
tmat = bpy.data.materials.get(TM) or bpy.data.materials.new(TM)
tmat.use_nodes = True
b = next(n for n in tmat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
b.inputs["Base Color"].default_value = (0.055, 0.045, 0.036, 1.0)
b.inputs["Roughness"].default_value = 0.92
TMESH = f"MID_street_trunk_mesh_{TAG}"
tme = bpy.data.meshes.get(TMESH)
if tme is None:
    tme = bpy.data.meshes.new(TMESH)
    bm = bmesh.new()
    # unit-height tapered 6-gon: r 1.0 at base -> 0.7 at top (scaled per instance)
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=1.0, radius2=0.7, depth=1.0)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, 0.5))
    bm.to_mesh(tme); bm.free()
    tme.materials.append(tmat)
TCOL = f"MID_street_trunks_{TAG}"
if TCOL in bpy.data.collections:
    tcol = bpy.data.collections[TCOL]
    for o in list(tcol.objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    tcol = bpy.data.collections.new(TCOL)
    col.children.link(tcol)

n = 0; heights = []
for c in crowns:
    x, y = c.location.x, c.location.y
    g = gz(x, y)
    if g is None:
        continue
    sz = c.scale.z
    clear = 2.2 + rng.random() * 0.6   # UNVERIFIED crown base height
    c.location.z = g + clear - zmin_local * sz
    top = c.location.z  # trunk into crown centre
    t = bpy.data.objects.new(f"MID_strunk_{TAG}_{n:04d}", tme)
    rad = 0.13 + 0.025 * (c.scale.x - 2.8)   # girth loosely with crown size
    rad = max(0.11, min(0.24, rad))
    t.location = (x + rng.uniform(-0.15, 0.15), y + rng.uniform(-0.15, 0.15), g - 0.25)
    t.scale = (rad, rad, top - g + 0.25)
    t.rotation_euler = (rng.uniform(-0.03, 0.03), rng.uniform(-0.03, 0.03), rng.random() * math.tau)
    t["status"] = "trunk UNVERIFIED height/girth; xy follows crown"
    t["TAG"] = TAG
    tcol.objects.link(t)
    t.cycles.use_distance_cull = True; t.cycles.use_camera_cull = True
    c["ah_crown_base_m"] = round(clear, 2)
    heights.append(c.location.z + c.scale.z * max(v.co.z for v in me.vertices) - g)
    n += 1
print("trunks", n, "tree total height min/med/max",
      round(min(heights), 1), round(sorted(heights)[len(heights)//2], 1), round(max(heights), 1), flush=True)

# --- skirt distance-ramped tone ---
m = bpy.data.materials["Context_skirt_ortho"]
nt = m.node_tree
hsv = nt.nodes["Hue/Saturation/Value"]
for nm in ("ah_geo", "ah_sep", "ah_len", "ah_mrV", "ah_mrS", "ah_x2", "ah_y2", "ah_add"):
    if nm in nt.nodes:
        nt.nodes.remove(nt.nodes[nm])
geo = nt.nodes.new("ShaderNodeNewGeometry"); geo.name = "ah_geo"
sep = nt.nodes.new("ShaderNodeSeparateXYZ"); sep.name = "ah_sep"
x2 = nt.nodes.new("ShaderNodeMath"); x2.name = "ah_x2"; x2.operation = "MULTIPLY"
y2 = nt.nodes.new("ShaderNodeMath"); y2.name = "ah_y2"; y2.operation = "MULTIPLY"
add = nt.nodes.new("ShaderNodeMath"); add.name = "ah_add"; add.operation = "ADD"
ln = nt.nodes.new("ShaderNodeMath"); ln.name = "ah_len"; ln.operation = "SQRT"
mv = nt.nodes.new("ShaderNodeMapRange"); mv.name = "ah_mrV"; mv.clamp = True
ms = nt.nodes.new("ShaderNodeMapRange"); ms.name = "ah_mrS"; ms.clamp = True
L = nt.links
L.new(geo.outputs["Position"], sep.inputs[0])
L.new(sep.outputs["X"], x2.inputs[0]); L.new(sep.outputs["X"], x2.inputs[1])
L.new(sep.outputs["Y"], y2.inputs[0]); L.new(sep.outputs["Y"], y2.inputs[1])
L.new(x2.outputs[0], add.inputs[0]); L.new(y2.outputs[0], add.inputs[1])
L.new(add.outputs[0], ln.inputs[0])
for mr, lo, hi in ((mv, 0.85, 0.58), (ms, 1.00, 1.12)):
    L.new(ln.outputs[0], mr.inputs["Value"])
    mr.inputs["From Min"].default_value = 800.0
    mr.inputs["From Max"].default_value = 1600.0
    mr.inputs["To Min"].default_value = lo
    mr.inputs["To Max"].default_value = hi
L.new(mv.outputs["Result"], hsv.inputs["Value"])
L.new(ms.outputs["Result"], hsv.inputs["Saturation"])
m["ah_tone"] = "r 800->1600 m: V 0.85->0.58, S 1.0->1.12"
print("skirt tone ramp linked", flush=True)

if SAVE:
    bpy.ops.wm.save_mainfile()
    print("SAVED", bpy.data.filepath, flush=True)

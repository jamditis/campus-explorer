"""tag 20261015ag (RERUNNABLE, --save). Instance OSM street trees + densify UNVERIFIED
low-poly ico crowns along MID_streets_20261015ae / ae street centrelines.
Collection MID_street_trees_20261015ag. No lamps/furniture.
- 13 OSM natural=tree from street_trees_mid_20261015af.json (xy ACCURATE-to-OSM)
- Densify: offset 3-6 m alternate sides, spacing 28-40 m, skip within 8 m of house
  footprints (ad/ae/af) or 6 m of another tree; cap ~150-250 densify.
Species/height UNVERIFIED for all.
"""
import bpy, json, math, os, random, sys
from mathutils import Vector, kdtree

TAG = "20261015ag"
SAVE = "--save" in sys.argv
ROOT = bpy.path.abspath("//")
rng = random.Random(20261015)
COL_NAME = f"MID_street_trees_{TAG}"
PROTO = f"MID_street_tree_proto_{TAG}"
MAT = f"MID_street_tree_olive_{TAG}"

# --- ground drape ---
gobs = [bpy.data.objects[n] for n in (
    "Context_skirt_3DEP_ortho_4km", "BD_farfield_3DEP_ortho", "Context_ground_beyond_data"
) if n in bpy.data.objects]

def gz(x, y):
    best = None
    for o in gobs:
        mi = o.matrix_world.inverted()
        ok, loc, *_ = o.ray_cast(mi @ Vector((x, y, 3000)), (mi.to_3x3() @ Vector((0, 0, -1))).normalized())
        if ok:
            z = (o.matrix_world @ loc).z
            best = z if best is None else max(best, z)
    return best

# --- house footprint centroids (skip within 8 m) ---
house_pts = []
for rel in (
    "data/ccom_mid_distance/ad/house_footprints_20261014ad.json",
    "data/ccom_mid_distance/ae/house_footprints_mid_20261015ae.json",
    "data/ccom_mid_distance/af/house_footprints_far_20261015af.json",
):
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        continue
    for b in json.load(open(p)).get("buildings", []):
        c = b.get("centroid_local_m")
        if c:
            house_pts.append(Vector((c[0], c[1], 0)))
        # also sample footprint verts if present (tighter skip)
        for v in (b.get("footprint_local_m") or [])[::max(1, len(b.get("footprint_local_m") or []) // 4)]:
            house_pts.append(Vector((v[0], v[1], 0)))
hkd = kdtree.KDTree(len(house_pts)) if house_pts else None
for i, p in enumerate(house_pts):
    hkd.insert(p, i)
if hkd:
    hkd.balance()
print("house anchor pts", len(house_pts), flush=True)

def near_house(x, y, r=8.0):
    if not hkd:
        return False
    _co, _i, d = hkd.find(Vector((x, y, 0)))
    return d < r

# --- collection / proto ---
if COL_NAME in bpy.data.collections:
    col = bpy.data.collections[COL_NAME]
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)
else:
    col = bpy.data.collections.new(COL_NAME)
    bpy.context.scene.collection.children.link(col)

if PROTO not in bpy.data.objects:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0, location=(0, 0, -8000))
    proto = bpy.context.active_object
    proto.name = PROTO
    proto.hide_set(True)
    proto.hide_render = True
    # unlink from scene collection if linked there
    for c in list(proto.users_collection):
        if c != col and PROTO in [o.name for o in c.objects]:
            pass
else:
    proto = bpy.data.objects[PROTO]

mat = bpy.data.materials.get(MAT) or bpy.data.materials.new(MAT)
mat.use_nodes = True
bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
# olive like ac after neon fix
bsdf.inputs["Base Color"].default_value = (0.05, 0.09, 0.04, 1.0)
bsdf.inputs["Roughness"].default_value = 0.9
if proto.data.materials:
    proto.data.materials[0] = mat
else:
    proto.data.materials.append(mat)

placed = []  # (x,y) for spacing KD

def place_crown(x, y, h, status, kind, osm_id=None):
    g = gz(x, y)
    if g is None:
        g = 30.0
    r = max(1.8, 0.32 * h)
    ob = proto.copy()
    ob.data = proto.data
    ob.name = f"MID_stree_{TAG}_{len(placed):04d}"
    ob.hide_set(False)
    ob.hide_render = False
    ob.location = Vector((x, y, g + r * 0.75))
    s = r * (0.92 + rng.random() * 0.16)
    ob.scale = Vector((s, s, s * (1.05 + rng.random() * 0.25)))
    ob.rotation_euler = (0, 0, rng.random() * math.tau)
    ob["status"] = status
    ob["kind"] = kind
    ob["TAG"] = TAG
    if osm_id is not None:
        ob["osm_id"] = str(osm_id)
    col.objects.link(ob)
    placed.append(Vector((x, y, 0)))
    return ob

# --- 13 OSM trees ---
td = json.load(open(os.path.join(ROOT, "data/ccom_mid_distance/af/street_trees_mid_20261015af.json")))
n_osm = 0
for t in td["trees"]:
    x, y = t["local_xy_m"]
    if near_house(x, y, 6.0):
        # still place OSM (ACCURATE) but note if close — prefer place; only skip densify near houses
        pass
    h = 9.0 + rng.random() * 5.0  # UNVERIFIED
    place_crown(x, y, h,
                "OSM natural=tree ACCURATE-to-OSM xy; species/height/crown UNVERIFIED",
                "osm_street_tree", t.get("osm_id"))
    n_osm += 1
print("OSM trees placed", n_osm, flush=True)

# tree KD for densify skip
def rebuild_tkd():
    tk = kdtree.KDTree(len(placed))
    for i, p in enumerate(placed):
        tk.insert(p, i)
    tk.balance()
    return tk

tkd = rebuild_tkd()

def near_tree(x, y, r=6.0):
    if len(placed) == 0:
        return False
    _co, _i, d = tkd.find(Vector((x, y, 0)))
    return d < r

# --- densify along ae streets ---
streets = json.load(open(os.path.join(ROOT, "data/ccom_mid_distance/ae/streets_20261015ae.json")))
x0, y0, x1, y1 = streets["bbox_local_m"]
DENSIFY_MAX = 220
SPACING = 34.0  # mid of 28-40
OFFSET_LO, OFFSET_HI = 3.5, 5.5
n_dens = 0
n_skip_house = n_skip_tree = n_skip_bbox = 0
side = 0
accum = 0.0
candidates = []

for w in streets["ways"]:
    line = [Vector((p[0], p[1])) for p in w["line_local_m"]]
    if len(line) < 2:
        continue
    # walk centreline
    dist_along = 0.0
    next_at = rng.uniform(0, SPACING * 0.5)
    for a, b in zip(line, line[1:]):
        seg = b - a
        seglen = seg.length
        if seglen < 1e-3:
            continue
        tdir = seg.normalized()
        nrm = Vector((-tdir.y, tdir.x))
        s0 = 0.0
        while True:
            need = next_at - dist_along
            if need > seglen - s0 + 1e-6:
                break
            s0 += need
            dist_along += need
            p = a + tdir * s0
            off = OFFSET_LO + rng.random() * (OFFSET_HI - OFFSET_LO)
            sign = 1 if (side % 2 == 0) else -1
            side += 1
            q = p + nrm * (off * sign)
            next_at = dist_along + SPACING + rng.uniform(-4.0, 4.0)
            candidates.append((q.x, q.y))
        dist_along += seglen - s0

print("densify candidates", len(candidates), flush=True)
# shuffle slightly by spatial hash order already street order; subsample if huge
if len(candidates) > DENSIFY_MAX * 4:
    step = max(1, len(candidates) // (DENSIFY_MAX * 3))
    candidates = candidates[::step]
    print("thinned candidates", len(candidates), flush=True)

for x, y in candidates:
    if n_dens >= DENSIFY_MAX:
        break
    if not (x0 - 50 <= x <= x1 + 50 and y0 - 50 <= y <= y1 + 50):
        n_skip_bbox += 1
        continue
    if near_house(x, y, 8.0):
        n_skip_house += 1
        continue
    if near_tree(x, y, 6.0):
        n_skip_tree += 1
        continue
    h = 7.5 + rng.random() * 6.0
    place_crown(x, y, h,
                "UNVERIFIED densify along ae street centreline; species/height/xy procedural",
                "densify_street_tree")
    n_dens += 1
    # incremental KD refresh every 20
    if n_dens % 20 == 0:
        tkd = rebuild_tkd()
    else:
        # cheap: rebuild always for correctness at modest N
        tkd = rebuild_tkd()

col["TAG"] = TAG
col["status"] = f"osm={n_osm} densify={n_dens} UNVERIFIED species/height; osm xy ACCURATE"
print("DONE osm", n_osm, "densify", n_dens, "skip_house", n_skip_house,
      "skip_tree", n_skip_tree, "skip_bbox", n_skip_bbox, "total", len(placed), flush=True)
if SAVE:
    bpy.ops.wm.save_mainfile()
    print("SAVED", flush=True)

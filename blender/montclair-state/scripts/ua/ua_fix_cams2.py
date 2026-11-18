"""Lift UA eye/closeup cams above skirt/ribbon volume; restore working College Ave eye."""
import bpy, os
from mathutils import Vector, bvhtree

SAVE = os.environ.get('SAVE') == '1'

def world_bvh(name):
    o = bpy.data.objects.get(name)
    if not o or o.type != 'MESH':
        return None, None
    deps = bpy.context.evaluated_depsgraph_get()
    eo = o.evaluated_get(deps)
    mesh = eo.to_mesh()
    try:
        mesh.transform(o.matrix_world)
        bvh = bvhtree.BVHTree.FromPolygons(
            [v.co.copy() for v in mesh.vertices],
            [p.vertices for p in mesh.polygons])
    finally:
        eo.to_mesh_clear()
    return o, bvh

# Prefer skirt surface, fall back to Terrain / ribbon
candidates = [
    'Context_skirt_3DEP_ortho_4km',
    'Terrain',
    'UA_NormalAve_CR618_583841725_727_729_UNVERIFIED',
]
bvhs = []
for n in candidates:
    o, b = world_bvh(n)
    if b:
        bvhs.append((n, b))
        print('BVH', n)

def ground_z(x, y):
    # cast from high down
    origin = Vector((x, y, 300))
    direction = Vector((0, 0, -1))
    best = None
    for n, b in bvhs:
        hit = b.ray_cast(origin, direction)
        # Blender 4 BVHTree.ray_cast returns (location, normal, index, distance)
        if hit and hit[0] is not None:
            z = hit[0].z
            if best is None or abs(z - 120) < abs(best - 120):
                # prefer hits near expected campus elevation
                if 80 < z < 200:
                    best = z
                    # keep first valid near-range
                    return z, n
    return best, None

road = bpy.data.objects.get('UA_NormalAve_CR618_583841725_727_729_UNVERIFIED')
walk = bpy.data.objects.get('UA_NormalAve_N_sidewalk_583841727_UNVERIFIED')
spur = bpy.data.objects.get('UA_CollegeAve_spur_1557427669_UNVERIFIED')

def mid_of(o):
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector((
        (min(v.x for v in bb)+max(v.x for v in bb))/2,
        (min(v.y for v in bb)+max(v.y for v in bb))/2,
        (min(v.z for v in bb)+max(v.z for v in bb))/2,
    ))

rmid = mid_of(road)
print('road mid', tuple(rmid))

# Sample ground along Normal Ave corridor
for xy in [(-167, -296), (-177, -282), (-230, -200), (-256, -271), (-140, -290), (-100, -280)]:
    z, src = ground_z(*xy)
    print('gz', xy, z, src)

def aim(ob, loc, target, lens=None, clip_start=0.05):
    ob.location = Vector(loc)
    direction = Vector(target) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    if lens is not None:
        ob.data.lens = lens
    ob.data.clip_start = clip_start
    ob.data.clip_end = 5000
    print('CAM', ob.name, 'loc', tuple(round(x,2) for x in ob.location), '->', tuple(round(x,2) for x in target))

# --- Oblique: keep high SW view looking NE across Normal Ave toward campus ---
z0, _ = ground_z(rmid.x, rmid.y)
z0 = z0 or rmid.z
cam = bpy.data.objects.get('UA_CAM_oblique_NormalAve_from_SW')
if cam:
    aim(cam, (rmid.x - 90, rmid.y - 110, z0 + 70),
        (rmid.x + 40, rmid.y + 80, z0 + 8), lens=28)

# --- Eye from N: stand on campus side ~25 m north of ribbon, 3.5 m AGL (raised eye clears skirt) ---
# Prefer a point on the north sidewalk corridor looking SE along the road
wx, wy = -160.0, -270.0
zg, src = ground_z(wx, wy)
print('eyeN stand', zg, src)
zg = zg or (z0 + 2)
cam = bpy.data.objects.get('UA_CAM_eye_NormalAve_from_N')
if cam:
    # elevated pedestrian / low-drone so we clear any skirt thickness
    aim(cam, (wx, wy, zg + 4.5),
        (rmid.x + 30, rmid.y - 5, z0 + 0.5), lens=32)

# --- College Ave spur eye: restore working 1128 framing (stood at -230,-200) ---
cam = bpy.data.objects.get('UA_CAM_eye_CollegeAve_spur_to_Normal')
if cam:
    zx, _ = ground_z(-230, -200)
    zx = zx or 120
    zt, _ = ground_z(-256.1, -271.6)
    zt = zt or 118
    aim(cam, (-230, -200, zx + 2.5),
        (-256.1, -271.6, zt + 0.8), lens=35)

# --- Closeup: elevated look-down onto walk/road join, not buried ---
cam = bpy.data.objects.get('UA_CAM_closeup_NormalAve_N_sidewalk')
if cam and walk:
    wmid = mid_of(walk)
    zw, _ = ground_z(wmid.x, wmid.y)
    zw = zw or wmid.z
    aim(cam, (wmid.x - 6, wmid.y + 10, zw + 6.0),
        (wmid.x + 4, wmid.y - 2, zw + 0.2), lens=40)

if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', len(bpy.data.objects))

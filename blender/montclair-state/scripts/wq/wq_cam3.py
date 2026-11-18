"""Raise the NW eye camera onto Terrain_LiDAR (DTM was NaN; fallback 130 left it underground)."""
import bpy, json, math
from mathutils import Vector, Euler
from mathutils.bvhtree import BVHTree

ROOT = '/workspace/nj-scenes/montclair-state'
dg = bpy.context.evaluated_depsgraph_get()

def look_rot(loc, tgt):
    d = Vector(tgt) - Vector(loc)
    return Euler((math.pi / 2 + math.atan2(d.z, math.hypot(d.x, d.y)), 0,
                  math.atan2(d.y, d.x) - math.pi / 2))

def ground_z(x, y):
    names = [
        'Terrain_LiDAR_DTM_1m',
        'QG_north_strip_LiDAR_terrain_patch',
        'QH_east_fan_LiDAR_terrain_patch',
        'QI_east_edge_LiDAR_terrain_patch',
    ]
    best = None
    hitn = None
    for n in names:
        o = bpy.data.objects.get(n)
        if o is None:
            continue
        e = o.evaluated_get(dg)
        m = e.to_mesh()
        vs = [o.matrix_world @ v.co for v in m.vertices]
        b = BVHTree.FromPolygons(vs, [tuple(p.vertices) for p in m.polygons])
        e.to_mesh_clear()
        h = b.ray_cast(Vector((x, y, 400)), Vector((0, 0, -1)))
        if h[0] is not None and (best is None or h[0].z > best):
            best = h[0].z
            hitn = n
    return best, hitn

cam = bpy.data.objects['WQ_CAM_eye_south_wood_from_NW']
old = list(cam.location)
zg, gn = ground_z(cam.location.x, cam.location.y)
print('OLD', old, 'ground', zg, gn, flush=True)
# keep look target from current rotation roughly: use stored tgt from cam2
tgt = (172.0, 180.0, 121.98)
if zg is None:
    raise SystemExit('no ground')
new = (cam.location.x, cam.location.y, zg + 1.65)
cam.location = Vector(new)
cam.rotation_euler = look_rot(new, tgt)
print('NEW', new, '->', tgt, flush=True)

# also verify the other two cams are above ground
rep = {'nw_old': old, 'nw_ground': zg, 'nw_ground_obj': gn, 'nw_new': list(new), 'others': []}
for name in ('WQ_CAM_closeup_south_wood_trees', 'WQ_CAM_eye_south_wood_from_SE'):
    o = bpy.data.objects[name]
    z, n = ground_z(o.location.x, o.location.y)
    rec = {'name': name, 'loc': [round(c, 2) for c in o.location], 'ground': None if z is None else round(z, 2),
           'obj': n, 'height_above': None if z is None else round(o.location.z - z, 2)}
    print('CHK', rec, flush=True)
    rep['others'].append(rec)

bpy.ops.wm.save_mainfile()
print('SAVED', flush=True)
json.dump(rep, open(f'{ROOT}/data/wq/cam3.json', 'w'), indent=1)

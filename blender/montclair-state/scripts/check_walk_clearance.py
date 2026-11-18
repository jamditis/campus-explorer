"""Walk-camera clearance check (3i). Run: blender -b montclair_state.blend --python scripts/check_walk_clearance.py -- [cam] [min_m] [step]
For every `step`-th frame of the walk camera, casts 162 rays (geodesic sphere) of length min_m (default 1.5 m) from the camera
position against the evaluated scene. Any hit on TREE or BUILDING geometry -> FAIL (exit 1). Other hits (lamp posts, benches) are
reported as warnings. Also checks the final hold frame: rays from the camera to a 7x5 grid on the Morehead entrance pavilion;
FAIL if more than 25% are blocked by tree geometry before reaching the facade.
"""
import bpy, sys, math, json
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
CAM = a[0] if len(a) > 0 else 'CAM_walk_west'; MIN = float(a[1]) if len(a) > 1 else 1.5; STEP = int(a[2]) if len(a) > 2 else 1
sc = bpy.context.scene; cam = bpy.data.objects[CAM]
# ray directions: icosphere subdivided twice (162 verts)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0); _ico = bpy.context.active_object
DIRS = [v.co.normalized() for v in _ico.data.vertices]; bpy.data.objects.remove(_ico, do_unlink=True)
tree_objs = set()
for cn in ('Trees_assets_LiDAR', 'Trees'):
    c = bpy.data.collections.get(cn)
    if c: tree_objs |= {o.name for o in c.all_objects}
tree_objs |= {o.name for o in bpy.data.objects if o.name.startswith('T_')}
BLD_KEYS = ('walls', 'roof', 'eave', 'entrance', 'Facade', 'facade', 'pavilion', 'parapet', 'gutter', 'downspout', 'reveals', 'tower', 'Building', 'cornice', 'pier', 'spandrel')
GROUND_KEYS = ('Terrain', 'paving', 'Paving', 'joint', 'grass', 'Lawn', 'lawn', 'worn', 'mulch', 'Mulch', 'curb', 'Curb', 'leaves', 'Leaves', 'cshadow', 'forecourt')
def kind(o):
    n = o.name
    if n in tree_objs: return 'tree'
    if any(k in n for k in GROUND_KEYS): return 'ground'
    if any(k in n for k in BLD_KEYS): return 'building'
    return 'other'
dg = bpy.context.evaluated_depsgraph_get()
fails, warns, worst = [], [], (1e9, None, None)
f0, f1 = sc.frame_start, sc.frame_end
for fr in range(f0, f1 + 1, STEP):
    sc.frame_set(fr); dg = bpy.context.evaluated_depsgraph_get(); p = cam.matrix_world.translation.copy()
    for d in DIRS:
        hit, loc, nrm, idx, ob, mx = sc.ray_cast(dg, p, d, distance=MIN)
        if not hit: continue
        o = ob.original if hasattr(ob, 'original') else ob; k = kind(o); dist = (loc - p).length
        if k == 'ground': continue
        if dist < worst[0]: worst = (dist, fr, o.name)
        (fails if k in ('tree', 'building') else warns).append((fr, k, o.name, round(dist, 2)))
# end-frame visibility of the pavilion (trees in the way)
vis = None
pav = bpy.data.objects.get('Morehead entrance pavilion body')
if pav is not None:
    sc.frame_set(f1); dg = bpy.context.evaluated_depsgraph_get(); p = cam.matrix_world.translation.copy()
    mw = pav.matrix_world; bb = [mw @ Vector(c) for c in pav.bound_box]
    lo = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb))); hi = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    nb = nt = 0
    for i in range(7):
        for j in range(5):
            q = Vector((lo.x + (hi.x - lo.x) * (i + .5) / 7, lo.y + (hi.y - lo.y) * (i + .5) / 7, lo.z + (hi.z - lo.z) * (j + .5) / 5))
            d = q - p; L = d.length
            hit, loc, nrm, idx, ob, mx = sc.ray_cast(dg, p, d.normalized(), distance=L - 0.6)
            nt += 1
            if hit and kind(ob.original if hasattr(ob, 'original') else ob) == 'tree': nb += 1
    vis = dict(blocked=nb, total=nt, frac=round(nb / nt, 3))
ftr = sorted({f for f, *_ in fails})
res = dict(camera=CAM, frames=[f0, f1], step=STEP, min_m=MIN, fail_frames=len(ftr), first_fail=ftr[:1], last_fail=ftr[-1:],
           fail_objects=sorted({n for _, _, n, _ in fails})[:20], warn_objects=sorted({n for _, _, n, _ in warns})[:20],
           closest=dict(dist=round(worst[0], 2), frame=worst[1], obj=worst[2]) if worst[1] else None, end_view_tree_block=vis)
ok = not fails and (vis is None or vis['frac'] <= 0.25)
res['result'] = 'PASS' if ok else 'FAIL'
print('CLEARANCE', json.dumps(res))
sys.exit(0 if ok else 1)

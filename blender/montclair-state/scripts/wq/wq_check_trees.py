"""List any existing (non-WQ) objects in the south-wood box that look like trees,
and measure distance from each WQ tree to the nearest other object origin.
"""
import bpy, json, math
from mathutils import Vector
ROOT = '/workspace/nj-scenes/montclair-state'
keys = ('tree', 'maple', 'oak', 'pine', 'beech', 'spruce', 'locust', 'sweetgum',
        'poplar', 'hemlock', 'cedar', 'linden', 'ash', 'birch', 'tulip', 'plane')
found = []
for o in bpy.data.objects:
    if o.name.startswith('WQ_'):
        continue
    t = o.matrix_world.translation
    if not (120 <= t.x <= 220 and 130 <= t.y <= 230):
        continue
    n = o.name.lower()
    if any(k in n for k in keys) or n.startswith('t_'):
        found.append([o.name, round(t.x, 2), round(t.y, 2), round(t.z, 2), o.type])

wq = []
for o in bpy.data.objects:
    if o.name.startswith('WQ_south_wood_tree_'):
        t = o.matrix_world.translation
        wq.append((o.name, t.x, t.y))

dups = []
for n, x, y in wq:
    near = []
    for fn, fx, fy, fz, ft in found:
        d = math.hypot(x - fx, y - fy)
        if d < 8:
            near.append([round(d, 2), fn, fx, fy])
    near.sort()
    if near:
        dups.append({'wq': n, 'x': round(x, 2), 'y': round(y, 2), 'near': near[:4]})

# also list cams
cams = []
for o in bpy.data.objects:
    if o.name.startswith('WQ_CAM') or o.name == 'TI_CAM_oblique_east_dorms_from_SW':
        t = o.matrix_world.translation
        cams.append([o.name, round(t.x, 2), round(t.y, 2), round(t.z, 2)])

rep = {
    'found_other': found,
    'n_found': len(found),
    'dups': dups,
    'n_wq': len(wq),
    'cams': cams,
    'objs': len(bpy.data.objects),
}
json.dump(rep, open(f'{ROOT}/data/wq/tree_overlap.json', 'w'), indent=1)
print('OTHER', len(found), 'WQ', len(wq), 'dups', len(dups))
for f in found[:40]:
    print(' ', f)
print('DUPS', json.dumps(dups, indent=1)[:2000])
print('CAMS', cams)

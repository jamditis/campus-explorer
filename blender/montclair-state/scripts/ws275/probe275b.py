# ws275 probe275b (modifiers off, no save): AGENTS.md rule 16 spatial check. For each housing building (OSM centre and radius from
# viewer/places.json, scene x = x, y = -z; list in HOUS), list every object whose world bounding box lies inside the circle, with its
# z range and the highest object top in the circle, so anything enclosed by a housing shell (rooms, floors, furniture, lights) shows.
import bpy, os, json
from bpy.app.handlers import persistent
from mathutils import Vector
@persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers: m.show_viewport = False
bpy.app.handlers.load_post.append(_off)
bpy.ops.wm.open_mainfile(filepath=os.environ['INF'])
HOUS = json.load(open(os.environ['HOUS']))
res = {}
bb = {}
for o in bpy.data.objects:
    if o.type not in ('MESH', 'FONT', 'LIGHT', 'CURVE', 'EMPTY'): continue
    if o.type == 'LIGHT' or o.type == 'EMPTY':
        p = o.matrix_world.translation; bb[o.name] = (p.x, p.x, p.y, p.y, p.z, p.z, o.type)
        continue
    c = [o.matrix_world @ Vector(v) for v in o.bound_box]
    bb[o.name] = (min(v.x for v in c), max(v.x for v in c), min(v.y for v in c), max(v.y for v in c),
                  min(v.z for v in c), max(v.z for v in c), o.type)
for name, hx, hy, r in HOUS:
    rr = r + 2.0; inside = []
    for on, (x0, x1, y0, y1, z0, z1, t) in bb.items():
        if all(((x - hx) ** 2 + (y - hy) ** 2) ** 0.5 <= rr for x in (x0, x1) for y in (y0, y1)):
            inside.append([on, t, round(z0, 1), round(z1, 1), round(max(x1 - x0, y1 - y0), 1)])
    res[name] = sorted(inside, key=lambda a: a[2])
    print('P275B', name, len(inside), flush=True)
json.dump(res, open(os.environ['OUTJ'], 'w'), indent=0)

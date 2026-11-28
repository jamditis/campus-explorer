# ws277 probe277a (modifiers off, no save): objects whose world bbox meets x -385..-330, y -300..-245 (Alumni House, OSM way
# 232846660, and Void's row-78 strip S of Normal Ave W): name, type, bbox, verts, materials, collections.
import bpy, os
from bpy.app.handlers import persistent
from mathutils import Vector
@persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers: m.show_viewport = False
bpy.app.handlers.load_post.append(_off)
bpy.ops.wm.open_mainfile(filepath=os.environ['INF'])
for o in bpy.data.objects:
    if o.type not in ('MESH', 'CURVE'): continue
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = [min(v[i] for v in bb) for i in range(3)]; hi = [max(v[i] for v in bb) for i in range(3)]
    if hi[0] < -385 or lo[0] > -330 or hi[1] < -300 or lo[1] > -245 or hi[0] - lo[0] > 150 or hi[1] - lo[1] > 150: continue
    mats = sorted({s.material.name for s in o.material_slots if s.material})[:4]
    print('P277A', o.name[:60], '|', [round(v, 1) for v in lo], [round(v, 1) for v in hi], len(o.data.vertices) if o.type == 'MESH' else 0,
          mats, [c.name for c in o.users_collection][:2], 'H' if o.hide_render else '', flush=True)

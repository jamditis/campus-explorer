import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.hide_render or o.type not in ('MESH','CURVE','EMPTY'): continue
    if not (o.hide_get() or o.hide_viewport): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]
    if min(xs)<-244 and max(xs)>-248 and min(ys)<-84 and max(ys)>-93: print('P76h',o.name,o.type,round(max(xs)-min(xs),1),flush=True)

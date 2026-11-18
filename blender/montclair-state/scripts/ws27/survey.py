import bpy
from mathutils import Vector
X0,X1,Y0,Y1=-345,-185,-180,-20
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE','CAMERA') : continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    big=(max(xs)-min(xs))>600
    print('OBJ',o.name,o.type,'hide' if o.hide_render else '', 'BIG' if big else '', 'x%.0f..%.0f y%.0f..%.0f z%.1f..%.1f'%(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)), [m.name for m in o.data.materials][:3] if o.type=='MESH' else '', len(o.data.vertices) if o.type=='MESH' else '', [c.name for c in o.users_collection][:1])

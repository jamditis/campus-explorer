import bpy
from mathutils import Vector
X0,X1,Y0,Y1=-225,-190,-112,-78
for o in bpy.context.scene.objects:
    if o.type not in ('MESH','CURVE') or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    sz=(max(xs)-min(xs))*(max(ys)-min(ys))
    if sz>20000: tag='BIG'
    else: tag=''
    print('OBJ',o.name,o.type,len(o.data.vertices) if o.type=='MESH' else '-',round(min(zs),2),round(max(zs),2),tag)

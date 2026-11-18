import bpy
from mathutils import Vector
X0,X1,Y0,Y1=-182,-110,-275,-215
print("NOBJ",len(bpy.data.objects))
for o in bpy.data.objects:
    if o.type not in('MESH','CURVE','EMPTY') : continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    area=(max(xs)-min(xs))*(max(ys)-min(ys))
    if area>40000: continue
    print('OB',o.name[:60],o.type,'x %.0f %.0f y %.0f %.0f z %.1f %.1f'%(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)), o.users_collection[0].name[:30] if o.users_collection else '', 'hide' if o.hide_render else '')

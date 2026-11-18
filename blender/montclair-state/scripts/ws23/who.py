import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(zs)-min(zs)>12 and min(xs)<-20 and max(xs)>-75 and min(ys)<290 and max(ys)>200 and (max(xs)-min(xs))<120:
        print('B|',o.name,[round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)),round(max(zs),1)])

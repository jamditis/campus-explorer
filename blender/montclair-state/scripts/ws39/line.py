import bpy
from mathutils import Vector
cx0,cx1,cy0,cy1=-250,-150,-150,-60
for o in bpy.context.scene.objects:
    if o.type in ('CAMERA','LIGHT') or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<cx0 or min(xs)>cx1 or max(ys)<cy0 or min(ys)>cy1: continue
    dx=max(xs)-min(xs); dy=max(ys)-min(ys); dz=max(zs)-min(zs)
    if o.type!='MESH' or max(dx,dy)>60 and (min(xs)<cx0-20 or max(xs)>cx1+20 or min(ys)<cy0-20 or max(ys)>cy1+20):
        print('LN39',o.type,o.name,len(o.data.vertices) if o.type=='MESH' else '',[round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)),round(min(zs),1),round(max(zs),1)])

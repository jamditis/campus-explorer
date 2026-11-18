import bpy
from mathutils import Vector
X0,X1,Y0,Y1=48,122,226,302
hits=[]
for o in bpy.data.objects:
    if o.type not in('MESH','CURVE','EMPTY') : continue
    if o.type=='EMPTY': 
        p=o.matrix_world.translation
        if X0<p.x<X1 and Y0<p.y<Y1: hits.append((o.name,'EMPTY',o.hide_render))
        continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    area=(max(xs)-min(xs))*(max(ys)-min(ys))
    if area>200000: hits.append((o.name,'BIG',o.hide_render,round(min(zs),1),round(max(zs),1))); continue
    hits.append((o.name,o.type,o.hide_render,[round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)),round(min(zs),1),round(max(zs),1)],o.users_collection[0].name if o.users_collection else ''))
for h in sorted(hits,key=lambda h:h[0]): print('HIT',h)
print('NHITS',len(hits))
print('CAMS',[c.name for c in bpy.data.objects if c.type=='CAMERA'][-12:])

import bpy, numpy as np
from mathutils import Vector
C=np.array([-178.,-82.]); R=22
out=[]
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if min(xs)<C[0]+R and max(xs)>C[0]-R and min(ys)<C[1]+R and max(ys)>C[1]-R:
        dx=max(xs)-min(xs); dy=max(ys)-min(ys)
        out.append((o.name,[c.name for c in o.users_collection],round(dx,1),round(dy,1),round(min(zs),2),round(max(zs),2),len(o.data.polygons),o.hide_render))
for r in sorted(out,key=lambda r:r[2]*r[3]): print('MAINOBJ',r)

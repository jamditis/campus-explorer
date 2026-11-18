import bpy, numpy as np, os
from mathutils import Vector
C=np.array([-178.,-82.]); R=22
for o in bpy.data.objects:
    if o.library: print('LINKED', o.name, os.path.basename(o.library.filepath), [c.name for c in o.users_collection])
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVES','POINTCLOUD'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if min(xs)<C[0]+R and max(xs)>C[0]-R and min(ys)<C[1]+R and max(ys)>C[1]-R:
        print('NORTHOBJ',o.name,o.type,[c.name for c in o.users_collection],round(max(xs)-min(xs),1),round(max(ys)-min(ys),1),round(min(zs),2),round(max(zs),2),o.hide_render, [m.type+':'+m.name for m in getattr(o,'modifiers',[])][:4])
print('CAMS',[c.name for c in bpy.data.objects if c.type=='CAMERA'])

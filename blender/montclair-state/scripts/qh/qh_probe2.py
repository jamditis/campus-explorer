import bpy, numpy as np
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
D=np.load('north/data/grid_1m.npz')['dtm_filled']
for y in (200,204,212,230,245,255):
    for x in (180,200,215,219,222,230,245):
        r=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
        l=float(D[int(y+260),int(min(x,219)+600)])
        print(y,x,'lid%.1f'%l, (round(r[1].z,1),r[4].name) if r[0] else None)

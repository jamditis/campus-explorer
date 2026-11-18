import bpy, numpy as np
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
L=np.load('north/data/grid_1m.npz')['dtm_filled']
for x in (-70,-58,-45,-35):
  for y in range(258,296,2):
    p=Vector((x,y,300)); hs=[]
    for k in range(6):
        h,l,n,i,o,m=sc.ray_cast(dg,p,Vector((0,0,-1)))
        if not h: break
        if not o.name.startswith(('T_','RZ_CAM','SA_CAM')): hs.append('%s@%.2f'%(o.name[:26],l.z))
        p=l-Vector((0,0,0.01))
    print('SA',x,y,'L=%.2f'%L[y+260,x+600],' | '.join(hs[:4]))

import bpy, numpy as np
dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['Center for Computing and Information Science roof (LiDAR)']; me=o.evaluated_get(dg).data
P=np.array([tuple(p.center) for p in me.polygons]); nz=np.array([p.normal.z for p in me.polygons])
for y in range(192,246,3):
    s=(P[:,1]>=y)&(P[:,1]<y+3)
    hi=s&(P[:,2]>153)&(nz>0.8); lo=s&(P[:,2]>140.5)&(P[:,2]<141.6)&(nz>0.8)
    print('y',y,'hi xmax',P[hi,0].max().round(2) if hi.any() else None,'lo x',(P[lo,0].min().round(1),P[lo,0].max().round(1)) if lo.any() else None)

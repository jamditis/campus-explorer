import bpy, numpy as np
from mathutils import Vector
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene; em=t.evaluated_get(dg).data
H=750739
fan=set(p.index for p in em.polygons if H in p.vertices)
xs=[];ys=[]
for i in fan:
    for v in em.polygons[i].vertices: xs.append(em.vertices[v].co.x); ys.append(em.vertices[v].co.y)
print('P113 fan',len(fan),'bbox x %.1f..%.1f y %.1f..%.1f'%(min(xs),max(xs),min(ys),max(ys)))
vis=[]; 
for x in np.arange(min(xs),max(xs),2.0):
    for y in np.arange(min(ys),max(ys),2.0):
        h=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)),distance=500)
        if h[0] and h[4]==t and h[3] in fan: vis.append((round(x),round(y)))
print('P113 visible fan samples (2m grid)',len(vis), vis[:60])

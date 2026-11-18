import bpy, random
from mathutils import Vector
from collections import Counter
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
pv=bpy.data.objects['WS113_paving_tops_proxy']; me=pv.data; random.seed(2)
C=Counter(); n=0; bad=[]
fs=[f for f in me.polygons if -132<f.center.x<48 and -251<f.center.y<-228]
random.shuffle(fs)
for f in fs[:150]:
    q=f.center
    h=sc.ray_cast(dg,q+Vector((0,0,3)),Vector((0,0,-1)),distance=3.02); n+=1
    if h[0]:
        nm=h[4].name
        if nm.startswith(('WS114_terrain','Terrain_LiDAR')) and h[1].z>q.z-0.02: C[nm]+=1; bad.append(tuple(round(c,1) for c in q))
print('P114b samples',n,'terrain-over-paving',dict(C),bad[:8])

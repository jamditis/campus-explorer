import bpy, os, numpy as np
from mathutils import Vector
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws250d.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
T=b.objects[0]; bpy.context.scene.collection.objects.link(T)
dg=bpy.context.evaluated_depsgraph_get(); me=T.evaluated_get(dg).to_mesh(); M=T.matrix_world
box=(-196,-140,141,214); out=[]
for p in me.polygons:
    c=M@p.center
    if box[0]<c.x<box[1] and box[2]<c.y<box[3] and p.normal.z<0.85: out.append((round(p.normal.z,2),round(p.area,4),round(c.x,2),round(c.y,2),round(c.z,2),len(p.vertices)))
print('ST250 steep faces',len(out),flush=True)
ar=np.array([o[1] for o in out]) if out else np.zeros(1); print('ST250 area quantiles',np.percentile(ar,[10,50,90,100]),flush=True)
for o in sorted(out,key=lambda o:o[3])[:: max(1,len(out)//40)]: print('ST250',o,flush=True)
# edges: boundary (1 face) count in box
from collections import Counter
ec=Counter()
for p in me.polygons:
    c=M@p.center
    if box[0]<c.x<box[1] and box[2]<c.y<box[3]:
        for k in p.edge_keys: ec[k]+=1
print('ST250 edges with 1 face in box',sum(1 for v in ec.values() if v==1),'of',len(ec),flush=True)
os._exit(0)

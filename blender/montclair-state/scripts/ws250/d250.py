# ws250 read-only: which evaluated Terrain faces (ws250a) would a "centre in BOX and area>1.5" delete remove; their coverage on
# a 1 m grid (cell centres) over a wide window -> d250.npy (1=covered by a deleted face); extents printed.
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws250a.blend')
BOX=tuple(map(float,os.environ.get('BOX','-194,-142,141,213').split(',')))
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
T=b.objects[0]; bpy.context.scene.collection.objects.link(T)
dg=bpy.context.evaluated_depsgraph_get(); me=T.evaluated_get(dg).to_mesh(); M=T.matrix_world
vs=[M@v.co for v in me.vertices]; sel=[]
for p in me.polygons:
    c=M@p.center
    if BOX[0]<c.x<BOX[1] and BOX[2]<c.y<BOX[3] and p.area>1.5: sel.append(p.vertices[:])
xs=[vs[i].x for f in sel for i in f]; ys=[vs[i].y for f in sel for i in f]
print('D250 faces',len(sel),'extent x %.1f..%.1f y %.1f..%.1f'%(min(xs),max(xs),min(ys),max(ys)),flush=True)
t=BVHTree.FromPolygons(vs,sel); W=(-230,-110,110,240)
C=np.zeros((W[3]-W[2],W[1]-W[0]),np.int8)
for j,y in enumerate(range(W[2],W[3])):
    for i,x in enumerate(range(W[0],W[1])):
        if t.ray_cast(Vector((x+0.5,y+0.5,400)),Vector((0,0,-1)),600)[0] is not None: C[j,i]=1
np.save('/workspace/nj-scenes/montclair-state/scripts/ws250/d250.npy',C); print('D250 covered cells',int(C.sum()),flush=True)
os._exit(0)

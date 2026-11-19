# ws229: base faces under the remaining SE residual samples (area, vert count, vert dz vs dtm)
import bpy,sys,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def d(x,y): return float(A[min(499,max(0,int(y+250))),min(499,max(0,int(x+250)))])
P=[(165,-85),(195,-100),(205,-105),(225,-135),(195,-185),(195,-105),(215,-160),(220,-180),(225,-140),(235,-210),(235,-205)]
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
B=BVHTree.FromPolygons([v.co.copy() for v in me.vertices],[p.vertices[:] for p in me.polygons])
for x,y in P:
    h=B.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    p=me.polygons[h[2]]; vs=[me.vertices[i].co for i in p.vertices]
    print('P229C',(x,y),'dz',round(h[0].z-d(x,y),2),'face',p.index,'area',round(p.area,1),'nv',len(vs),'vdz',[round(v.z-d(v.x,v.y),2) for v in vs],'dtm3x3',[round(d(x+i,y+j)-d(x,y),2) for i in (-2,0,2) for j in (-2,0,2)],flush=True)
sys.stdout.flush(); import os; os._exit(0)

import bpy,sys,os,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def d(x,y): return float(A[min(499,max(0,int(y+250))),min(499,max(0,int(x+250)))])
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
B=BVHTree.FromPolygons([v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])
H=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws228/probe227a_ws228c.json'))['grid']
for x,y,v in sorted([g for g in H if g[2] is not None and g[2]>0.9],key=lambda g:-g[2]):
    h=B.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    if h[0] is None: print('P228F',x,y,v,'base nohit',flush=True); continue
    p=me.polygons[h[2]]
    print('P228F',x,y,'eval',v,'base',round(h[0].z-d(x,y),2),'face',h[2],'area',round(p.area,1),'vdz',[round(me.vertices[i].co.z-d(me.vertices[i].co.x,me.vertices[i].co.y),2) for i in p.vertices],'vxy',[(round(me.vertices[i].co.x),round(me.vertices[i].co.y)) for i in p.vertices],flush=True)
sys.stdout.flush(); os._exit(0)

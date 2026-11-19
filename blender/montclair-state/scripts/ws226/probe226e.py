import bpy, sys, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
print('P226E users',me.users,[o.name for o in bpy.data.objects if o.data==me],flush=True)
P=[bpy.data.objects[n] for n in ('QG_north_strip_LiDAR_terrain_patch','QH_east_fan_LiDAR_terrain_patch','QI_east_edge_LiDAR_terrain_patch')]
V=[];F=[]
for o in P:
    b=len(V); M=o.matrix_world; V+= [M@v.co for v in o.data.vertices]; F+=[[i+b for i in p.vertices] for p in o.data.polygons]
BP=BVHTree.FromPolygons(V,F)
co=np.array([v.co[:] for v in me.vertices])
e=co[:,0]>60
print('P226E east verts',e.sum(),'of',len(co),flush=True)
# spacing
ex=co[e]
import collections
st=collections.Counter()
for x,y,z in ex[::7]:
    h=BP.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    d=float(A[min(499,int(y+250)),min(499,int(x+250))])
    if h[0] is None: st['nohit '+('hi' if z-d>0.5 else 'ok')]+=1
    else: st['hit '+('above>0.1' if z>h[0].z+0.1 else 'ok')]+=1
print('P226E',dict(st),flush=True)
# nearest-neighbour spacing sample in box
box=ex[(ex[:,0]>150)&(ex[:,0]<240)&(ex[:,1]>0)&(ex[:,1]<200)]
print('P226E box verts',len(box),'area 18000',flush=True)
# faces in box sizes
ar=[p.area for p in me.polygons if 150<p.center.x<240 and 0<p.center.y<200]
print('P226E box faces',len(ar),'mean area',sum(ar)/max(1,len(ar)),'max',max(ar) if ar else 0,flush=True)
sys.stdout.flush(); os._exit(0)

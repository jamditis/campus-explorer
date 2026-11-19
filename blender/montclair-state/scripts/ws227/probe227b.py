# residual hi samples after fix227a: which base faces own them (south strip y<-215, north band y>-75, east edge)
import bpy, sys, os, json, collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def d(x,y): return float(A[min(499,max(0,int(y+250))),min(499,max(0,int(x+250)))])
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
B=BVHTree.FromPolygons([v.co.copy() for v in me.vertices],[p.vertices[:] for p in me.polygons])
G=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws227/probe227a_after.json'))['grid']
own=collections.defaultdict(list)
for x,y,dz in G:
    if dz is None or dz<=0.5: continue
    h=B.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    if h[0] is None: own['none'].append((x,y,dz)); continue
    own[h[2]].append((x,y,dz,round(h[0].z-d(x,y),2)))
for k,v in sorted(own.items(),key=lambda kv:-len(kv[1]))[:15]:
    if k=='none': print('P227B none',len(v),v[:5],flush=True); continue
    p=me.polygons[k]; vs=[me.vertices[i].co for i in p.vertices]
    print('P227B face',k,'n',len(v),'area',round(p.area),'nv',len(vs),'c',tuple(round(c) for c in p.center[:2]),'vdz',[round(q.z-d(q.x,q.y),2) for q in vs][:8],'evaldz max',max(r[2] for r in v),'basedz',v[0][3],flush=True)
sys.stdout.flush(); os._exit(0)

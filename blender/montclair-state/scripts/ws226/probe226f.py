import bpy, sys, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
P=[bpy.data.objects[n] for n in ('QG_north_strip_LiDAR_terrain_patch','QH_east_fan_LiDAR_terrain_patch','QI_east_edge_LiDAR_terrain_patch')]
V=[];F=[]
for o in P:
    b=len(V); M=o.matrix_world; V+= [M@v.co for v in o.data.vertices]; F+=[[i+b for i in p.vertices] for p in o.data.polygons]
BP=BVHTree.FromPolygons(V,F)
BB=BVHTree.FromPolygons([v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])
big=[p for p in me.polygons if p.area>20]
print('P226F faces>20m2',len(big),'total area',round(sum(p.area for p in big)),flush=True)
out=[]
for p in sorted(big,key=lambda p:-p.area)[:60]:
    vs=[me.vertices[i].co for i in p.vertices]
    xs=[v.x for v in vs]; ys=[v.y for v in vs]
    n=0; cov=0; hi=[]
    for x in np.arange(min(xs),max(xs),2.0):
        for y in np.arange(min(ys),max(ys),2.0):
            z=400; inside=None
            while True:
                hh=BB.ray_cast(Vector((x,y,z)),Vector((0,0,-1)))
                if hh[0] is None: break
                if hh[2]==p.index: inside=hh; break
                z=hh[0].z-0.01
            if not inside: continue
            n+=1
            q=BP.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
            if q[0] is not None: cov+=1
            else:
                d=float(A[min(499,max(0,int(y+250))),min(499,max(0,int(x+250)))]); hi.append(inside[0].z-d)
    out.append((p.index,round(p.area),len(vs),round(p.center.x),round(p.center.y),n,cov,round(float(np.mean(hi)),2) if hi else None,round(float(np.max(hi)),2) if hi else None))
    print('P226F',out[-1],flush=True)
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws226/probe226f.json','w'))
sys.stdout.flush(); os._exit(0)

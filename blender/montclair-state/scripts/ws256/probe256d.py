# ws256 read-only: targets for merging ge_police_south_walk (north file) into main (M2c review item).
# For each walk vertex: main's EVALUATED ground (WS68 north-DTM patch / M3b corridor / base terrain), mean of 5 samples
# (r 0.35 m) -> drape target +3 cm; faces whose centre lies under main's police building / terrace / Red Hawk W core -> delete.
import sys, json; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
with bpy.data.libraries.load(MS+'north/montclair_north.blend') as (a,b): b.objects=['ge_police_south_walk']
W=b.objects[0]
G=['WS68_RHD_ground_northDTM','M3b_north_LiDAR_DTM_1m_west_rail_corridor','Terrain_LiDAR_DTM_1m']
OB=['fp_police_body','fp_police_foundation','fp_police_outbuilding','ge_police_terrace_walls','ge_police_terrace_bed','Red Hawk W core','Red Hawk Deck']
with bpy.data.libraries.load(MS+'montclair_state.blend') as (a,c): c.objects=[n for n in a.objects if n.startswith(tuple(G+OB))]
for o in list(c.objects)+[W]: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
X0,X1,Y0,Y1=-360,-330,-25,-2
def bvh(o):
    em=o.evaluated_get(dg).to_mesh(); M=o.matrix_world; vs=[M@v.co for v in em.vertices]
    ps=[p.vertices[:] for p in em.polygons if any(X0<vs[i].x<X1 and Y0<vs[i].y<Y1 for i in p.vertices)]
    return BVHTree.FromPolygons(vs,ps) if ps else None
GB=[bvh(o) for o in c.objects if o.name.startswith(tuple(G))]; GB=[g for g in GB if g]
BB={o.name:bvh(o) for o in c.objects if o.name.startswith(tuple(OB))}; BB={k:v for k,v in BB.items() if v}
print('P256D ground objs',len(GB),'blockers',list(BB))
def gz(x,y):
    z=None
    for g in GB:
        h=g.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600)
        if h[0] and (z is None or h[0].z>z): z=h[0].z
    return z
M=W.matrix_world; me=W.data; tgt={}; d=[]
for v in me.vertices:
    w=M@v.co; s=[gz(w.x+dx,w.y+dy) for dx,dy in ((0,0),(0.35,0),(-0.35,0),(0,0.35),(0,-0.35))]; s=[q for q in s if q is not None]
    if not s: continue
    t=float(np.mean(s))+0.03; tgt[v.index]=t; d.append(w.z-t)
d=np.array(d); print('P256D verts',len(me.vertices),'with target',len(tgt),'walk-target p5 %.2f p50 %.2f p95 %.2f max |d| %.2f'%(*np.percentile(d,[5,50,95]),np.abs(d).max()))
dele=[]; why={}
for p in me.polygons:
    cw=M@p.center
    for n,bt in BB.items():
        h=bt.ray_cast(Vector((cw.x,cw.y,400)),Vector((0,0,-1)),600)
        if h[0] and h[0].z>cw.z+0.05 and h[0].z<cw.z+40:
            dele.append(p.index); why[n[:20]]=why.get(n[:20],0)+1; break
print('P256D faces under blockers',len(dele),why)
json.dump({'tgt':tgt,'del':dele},open(MS+'scripts/ws256/police_walk256.json','w'))
os._exit(0)

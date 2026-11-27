# ws256 read-only M2c review of ge_police_south_walk (north file) vs main ground INCLUDING the north-merged patches
# (ws254 rev254 loaded only the base terrain, which has no faces here -> inconclusive)
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
with bpy.data.libraries.load(MS+'north/montclair_north.blend') as (a,b): b.objects=[n for n in a.objects if n=='ge_police_south_walk']
nobj=list(b.objects)
X0,X1,Y0,Y1=-358,-332,-23,-4
import json
BB=json.load(open(MS+'scripts/ws205/bbox205.json'))
want=[n for n,(t,hr,x0,x1,y0,y1,z0,z1,cols) in BB.items() if t=='MESH' and not (x1<X0 or x0>X1 or y1<Y0 or y0>Y1) and not n.startswith(('BD_farfield','Context_ground_beyond','WS48_band'))]
with bpy.data.libraries.load(MS+'montclair_state.blend') as (a,b): b.objects=[n for n in a.objects if n in want or n.startswith(('Terrain_LiDAR_DTM_1m','Footpaths_OSM','Roads_OSM','M3'))]
mobj=[o for o in b.objects if o]
for o in mobj+nobj: bpy.context.scene.collection.objects.link(o)
print('REV256 main objs',[o.name[:40] for o in mobj])
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    em=o.evaluated_get(dg).to_mesh(); M=o.matrix_world; vs=[M@v.co for v in em.vertices]
    ps=[p.vertices[:] for p in em.polygons if any(X0<vs[i].x<X1 and Y0<vs[i].y<Y1 for i in p.vertices)]
    return BVHTree.FromPolygons(vs,ps) if ps else None
MB={o.name:bvh(o) for o in mobj if o.type=='MESH'}; MB={k:v for k,v in MB.items() if v}
print('REV256 main objs with faces in box',[k[:40] for k in MB])
W=nobj[0]; WB=bvh(W)
print('REV256 walk mods',[m.name for m in W.modifiers],'mats',[m.name for m in W.data.materials if m])
def hit(bt,x,y):
    h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return h[0].z if h[0] else None
stats={}; d=[]; rows=[]
for y in np.arange(Y0+0.25,Y1,0.5):
    row=''
    for x in np.arange(X0+0.25,X1,0.5):
        w=hit(WB,x,y)
        if w is None: row+=' '; continue
        hs=[(hit(t,x,y),n) for n,t in MB.items()]; hs=[(z,n) for z,n in hs if z is not None and z<w+5]
        if not hs: row+='?'; continue
        z,n=max(hs); dd=w-z; d.append(dd); stats[n[:30]]=stats.get(n[:30],0)+1
        row+= 'B' if dd<-0.02 else ('.' if dd<0.1 else ('f' if dd<0.3 else 'F'))
    rows.append('REV256 y%6.1f %s'%(y,row))
d=np.array(d)
print('REV256 samples',len(d),'walk-ground p5 %.2f p50 %.2f p95 %.2f'%tuple(np.percentile(d,[5,50,95])),'buried',(d<-0.02).sum(),'float>0.3',(d>0.3).sum())
print('REV256 top main object under walk',stats)
for r in rows: print(r)
os._exit(0)

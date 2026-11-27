# ws257 read-only UNIFY #10: WS110_ground_patch_S_of_y-238 outer boundary vs whatever ground is just outside it (evaluated).
# For each evaluated boundary edge midpoint: patch z vs topmost other ground-like surface 0.5 m outward -> step (+ = patch above).
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, json, re, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
X0,X1,Y0,Y1=-306,-144,-306,-232
P='WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED'
BB=json.load(open(MS+'scripts/ws205/bbox205.json'))
G=re.compile(r'ground|terrain|skirt|lawn|patch|dtm|yard|verge|walk|road|carriage|sidewalk|asphalt|lot|paving|apron|footpath|drive|fill|bank',re.I)
want=[n for n,v in BB.items() if v[0]=='MESH' and not (v[3]<X0 or v[2]>X1 or v[5]<Y0 or v[4]>Y1) and G.search(n) and not n.startswith(('BD_farfield','WS48_band','T_')) and 'hidden' not in n and 'target' not in n.lower()]
with bpy.data.libraries.load(MS+'montclair_state.blend') as (a,b): b.objects=[n for n in a.objects if n in want or n==P]
objs=[o for o in b.objects if o]
for o in objs: bpy.context.scene.collection.objects.link(o)
print('P257F loaded',len(objs))
dg=bpy.context.evaluated_depsgraph_get()
def ev(o):
    em=o.evaluated_get(dg).to_mesh(); M=o.matrix_world; vs=[M@v.co for v in em.vertices]
    ps=[p.vertices[:] for p in em.polygons if any(X0<vs[i].x<X1 and Y0<vs[i].y<Y1 for i in p.vertices)]
    return vs,ps
pv,pp=ev(bpy.data.objects[P])
# boundary edges of the evaluated patch
from collections import Counter
ec=Counter()
for f in pp:
    for i in range(len(f)): ec[tuple(sorted((f[i],f[(i+1)%len(f)])))]+=1
bnd=[e for e,c in ec.items() if c==1]
PB=BVHTree.FromPolygons(pv,pp)
OB={}
for o in objs:
    if o.name==P: continue
    vs,ps=ev(o)
    if ps: OB[o.name]=BVHTree.FromPolygons(vs,ps)
print('P257F patch faces',len(pp),'boundary edges',len(bnd),'other ground objs',len(OB))
cx=np.mean([v.x for v in pv]); cy=np.mean([v.y for v in pv])
rows=[]
for a,b2 in bnd:
    A,B=pv[a],pv[b2]; m=(A+B)/2; d=(B-A); d.z=0
    if d.length<1e-6: continue
    nrm=Vector((d.y,-d.x,0)).normalized()
    # outward = the side where the patch is NOT
    t=m+nrm*0.5
    if PB.ray_cast(Vector((t.x,t.y,400)),Vector((0,0,-1)),600)[0]: nrm=-nrm; t=m+nrm*0.5
    best=None; bn=None
    for n,bt in OB.items():
        h=bt.ray_cast(Vector((t.x,t.y,m.z+3)),Vector((0,0,-1)),8)
        if h[0] and (best is None or h[0].z>best): best=h[0].z; bn=n
    rows.append((m.x,m.y,m.z,(m.z-best) if best is not None else None,bn))
st=[r for r in rows if r[3] is not None]; miss=[r for r in rows if r[3] is None]
print('P257F edges with ground outside',len(st),'no ground outside (hole/void)',len(miss))
s=np.array([r[3] for r in st])
print('P257F step p5 %.2f p50 %.2f p95 %.2f  |step|>0.15: %d  >0.3: %d'%(*np.percentile(s,[5,50,95]),(abs(s)>0.15).sum(),(abs(s)>0.3).sum()))
by={}
for r in st:
    if abs(r[3])>0.15: by.setdefault(r[4][:40],[]).append(r)
for n,L in by.items():
    L.sort(key=lambda r:-abs(r[3])); print('P257F  vs',n,len(L),'worst',[(round(r[0],1),round(r[1],1),round(r[3],2)) for r in L[:6]])
for r in miss[:15]: print('P257F  miss at',round(r[0],1),round(r[1],1),round(r[2],2))
json.dump(rows,open(MS+'scripts/ws257/probe257f.json','w'))
os._exit(0)

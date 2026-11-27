# ws257 read-only M2c review: north-file "MSU Maintenance Building (OSM 232850495 ...)" massing vs main.
# (1) footprint cells (0.5 m) where the massing exists vs main structures (Red Hawk Deck, rhd retaining wall, cogen) -> overlap cells
# (2) base ring: massing's lowest verts vs main's EVALUATED ground (WS68 north DTM patch + terrain) -> floating / buried
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
X0,X1,Y0,Y1=-393,-323,-79,-36
with bpy.data.libraries.load(MS+'north/montclair_north.blend') as (a,b): b.objects=[n for n in a.objects if n.startswith('MSU Maintenance Building')]
mb=b.objects[0]
BB=json.load(open(MS+'scripts/ws205/bbox205.json'))
want=[n for n,v in BB.items() if v[0]=='MESH' and not (v[3]<X0 or v[2]>X1 or v[5]<Y0 or v[4]>Y1) and not n.startswith(('BD_farfield','WS48_band'))]
with bpy.data.libraries.load(MS+'montclair_state.blend') as (a,b): b.objects=[n for n in a.objects if n in want]
mobj=[o for o in b.objects if o]
for o in mobj+[mb]: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    em=o.evaluated_get(dg).to_mesh(); M=o.matrix_world; vs=[M@v.co for v in em.vertices]
    ps=[p.vertices[:] for p in em.polygons if any(X0<vs[i].x<X1 and Y0<vs[i].y<Y1 for i in p.vertices)]
    return (BVHTree.FromPolygons(vs,ps),len(ps)) if ps else (None,0)
GROUND=('Terrain','WS68','Context','WS60','WS1','gb_grass','M3','North_terrain','gb_','gd_')
MB={}
for o in mobj:
    t,n=bvh(o)
    if t: MB[o.name]=t
print('P257C main objs with faces in box',len(MB),[k[:34] for k in MB])
T,_=bvh(mb)
def hits(bt,x,y):
    out=[]; o=Vector((x,y,400))
    while True:
        h=bt.ray_cast(o,Vector((0,0,-1)),600)
        if not h[0]: return out
        out.append(h[0].z); o=Vector((x,y,h[0].z-0.001))
ov={}; cells=0; gz=[]
for x in np.arange(X0,X1,0.5):
    for y in np.arange(Y0,Y1,0.5):
        hm=hits(T,x,y)
        if len(hm)<2: continue
        cells+=1; top,bot=max(hm),min(hm)
        for n,t in MB.items():
            for z in hits(t,x,y):
                if bot+0.3<z<top-0.05:
                    ov[n[:40]]=ov.get(n[:40],0)+1; break
print('P257C massing cells',cells,'cells with a main surface INSIDE the massing (by object):',ov)
# base ring vs ground
em=mb.data; M=mb.matrix_world; vs=np.array([M@v.co for v in em.vertices]); zb=vs[:,2].min()
base=vs[vs[:,2]<zb+3.0]
gnames=[n for n in MB if any(n.startswith(g) for g in GROUND) or 'ground' in n.lower() or 'lawn' in n.lower() or 'paving' in n.lower() or 'asphalt' in n.lower()]
print('P257C ground-ish objs',[g[:30] for g in gnames])
d=[]
for v in base:
    zs=[]
    for g in gnames:
        h=hits(MB[g],v[0]+0.0,v[1]+0.0)
        zs+= [z for z in h if z<v[2]+6]
    if zs: d.append(v[2]-max(zs))
d=np.array(d)
print('P257C base verts',len(base),'base z %.2f..%.2f'%(base[:,2].min(),base[:,2].max()),'base-ground p5 %.2f p50 %.2f p95 %.2f'%tuple(np.percentile(d,[5,50,95])) if len(d) else 'no ground','floating>0.05',int((d>0.05).sum()) if len(d) else -1)
os._exit(0)

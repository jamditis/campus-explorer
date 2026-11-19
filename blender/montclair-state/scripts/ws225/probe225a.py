# W52: scene-wide limb clearance for tree objects (deciduous). Raw meshes, modifiers off.
import bpy, time, json, re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
t0=time.time()
CON=re.compile('Spruce|Pine|Fir|Hemlock|Arbor|Juniper|Cedar|Yew|Conifer|Shrub|Hedge|Bush',re.I)
trees=[o for o in bpy.data.objects if o.type=='MESH' and o.data.name.startswith('Tree_') and not CON.search(o.data.name)]
from collections import Counter
print('P225 trees',len(trees),Counter(o.data.name for o in trees).most_common(30),flush=True)
PAVE=re.compile('walk|Footpath|apron|plaza|landing|sidewalk|Plaza|Walk|courtyard|Courtyard|patio|Patio|steps|deck_top',re.I)
G=[];P=[]
for g in bpy.data.objects:
    if g.type!='MESH' or not g.visible_get(): continue
    isT=g.name.startswith('Terrain_LiDAR_DTM_1m'); isP=bool(PAVE.search(g.name)) and len(g.data.polygons)<200000
    if not (isT or isP): continue
    Mg=g.matrix_world
    b=BVHTree.FromPolygons([Mg@v.co for v in g.data.vertices],[p.vertices[:] for p in g.data.polygons])
    (G if isT else P).append(b)
print('P225 bvh terrain',len(G),'paving',len(P),round(time.time()-t0),flush=True)
def hit(Ts,x,y):
    zs=[h[0].z for T in Ts for h in [T.ray_cast(Vector((x,y,250)),Vector((0,0,-1)))] if h[0]]
    return max(zs) if zs else None
res=[]
for o in trees:
    M=o.matrix_world; ws=[M@v.co for v in o.data.vertices]
    vs=sorted(ws,key=lambda w:w.z)[:20]; ax=Vector((sum(w.x for w in vs)/20,sum(w.y for w in vs)/20)); zb=vs[0].z
    gt=hit(G,ax.x,ax.y)
    under=0; lowpave=0; minc=99
    for i,w in enumerate(ws[::3]):
        if (w.xy-ax).length<1.0: continue
        g=hit(G,w.x,w.y); p=hit(P,w.x,w.y)
        if g is not None and w.z<g-0.02: under+=1
        # paving clearance is independent of the raw terrain (unreliable in the east, W53)
        if p is not None and w.z-p<2.4: lowpave+=1; minc=min(minc,w.z-p)
    if under or lowpave: res.append((o.name,o.data.name,round(ax.x,1),round(ax.y,1),round(zb-(gt or 0),2),under*3,lowpave*3,round(minc,2)))
res.sort(key=lambda r:-(r[5]+r[6]))
print('P225 flagged',len(res),'time',round(time.time()-t0),flush=True)
for r in res[:60]: print('P225',r)
json.dump(res,open('/workspace/nj-scenes/montclair-state/scripts/ws225/probe225a.json','w'))

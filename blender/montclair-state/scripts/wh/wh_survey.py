"""wh: list exposure >12 cm (slab top - top ground within 45 cm of a slab) in a box, with which ground object is top and its local edge length."""
import bpy,numpy as np,json,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
BX=tuple(float(v) for v in os.environ['BOX'].split(',')); TAG=os.environ.get('TAG','s')
def dg(): return bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg()); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
def bbx(o):
    c=np.array([o.matrix_world@Vector(b) for b in o.bound_box]); return c[:,0].min(),c[:,0].max(),c[:,1].min(),c[:,1].max()
ov=lambda b,m:(b[0]<BX[1]+m and b[1]>BX[0]-m and b[2]<BX[3]+m and b[3]>BX[2]-m)
SLn=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QW_footway_','QS_service_','TR_footway','SG_')) and ov(bbx(O[n]),3)]
GRDn=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('WV_stone','WN_south','WO_gully','Terrain_LiDAR','QW_DTM','WU_rich','WT_rich','WF_east','RZ2_','WA0_','SA_ground_lower_patch')) and ov(bbx(O[n]),0)]
print('SL',SLn,'GRD',GRDn,flush=True)
SL=[bvh(O[n]) for n in SLn]; G={n:bvh(O[n]) for n in GRDn}
def top(B,x,y):
    z=[h[0].z for b in B for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]; return max(z) if z else None
def topn(x,y):
    best=None
    for n,b in G.items():
        h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
        if h[0] is not None and (best is None or h[0].z>best[1]): best=(n,h[0].z,h[2])
    return best
def near(x,y):
    for r in np.arange(0.1,0.46,0.1):
        zs=[top(SL,x+r*np.cos(a),y+r*np.sin(a)) for a in np.linspace(0,2*np.pi,16,endpoint=False)]
        zs=[z for z in zs if z is not None]
        if zs: return r,max(zs)
out=[];allE=[]
for x in np.arange(BX[0],BX[1],0.2):
    for y in np.arange(BX[2],BX[3],0.2):
        if top(SL,x,y) is not None: continue
        ns=near(x,y)
        if not ns: continue
        t=topn(x,y)
        if not t: continue
        e=ns[1]-t[1]; allE.append(e)
        if e>0.12:
            o=O[t[0]]; p=o.data.polygons[t[2]]; vs=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
            el=max((vs[i]-vs[(i+1)%len(vs)]).length for i in range(len(vs)))
            out.append((round(float(x),1),round(float(y),1),round(float(e),3),t[0],round(el,2)))
allE=np.array(allE)
print('N',len(allE),'p50',np.median(allE),'p90',np.percentile(allE,90),'max',allE.max(),'n>12',len(out),flush=True)
out.sort(key=lambda r:-r[2])
for r in out[:40]: print(r)
from collections import Counter
print(Counter(r[3] for r in out)); print('edge',Counter(r[4] for r in out).most_common(6))
json.dump(out,open(f'/workspace/nj-scenes/montclair-state/data/wh/survey_{TAG}.json','w'))

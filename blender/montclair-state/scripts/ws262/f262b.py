# ws262 M2c (merge208 CHAIN): merge the north file's police-lawn grass scatter (gd_grass_police_lawn_points, 31,694 points,
# GN gd_grass_lawn_instancer.002 + its blade instances) into main. probe262d (main EVALUATED ground, modifiers on in the lawn box):
# 27,618 points land on WS68_RHD_ground_northDTM, 4,073 on M3b_north_LiDAR_DTM_1m_west_rail_corridor, 3 on fp_police_parapet_coping,
# 0 on walks/paving. Snap every point to the evaluated top - 1 cm; drop points whose top is not one of the two ground meshes,
# or that moved > 0.5 m (none expected). Linked into WS68's collection. Edge feather (ws262e) thins the points over the outer 3 m.
import bpy, json, bmesh
TAG='F262B'; NF='/workspace/nj-scenes/montclair-state/north/montclair_north.blend'; ON='gd_grass_police_lawn_points'
if ON in bpy.data.objects: raise SystemExit('F262B already in main')
ng0={n.name for n in bpy.data.node_groups}; ob0={o.name for o in bpy.data.objects}; co0={c.name for c in bpy.data.collections}
with bpy.data.libraries.load(NF,link=False) as (src,dst): dst.objects=[ON]
o=dst.objects[0]
R=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws262/eval262d.json'))
GOOD=('WS68_RHD_ground_northDTM','M3b_north_LiDAR_DTM_1m_west_rail_corridor')
me=o.data; W=o.matrix_world; Wi=W.inverted()
assert len(me.vertices)==len(R), (len(me.vertices),len(R))
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); kill=[]; mv=[]
for v,(x,y,z,top,zt) in zip(bm.verts,R):
    g=W@v.co
    if abs(g.x-x)>0.01 or abs(g.y-y)>0.01: raise SystemExit('F262B point order mismatch')
    if top is None or not top.startswith(GOOD) or abs(zt-0.01-g.z)>0.5: kill.append(v); continue
    mv.append(zt-0.01-g.z); g.z=zt-0.01; v.co=Wi@g
# ws262e: from above the north set reads as dark rectangles with ruler-straight edges (its footprint is an L of axis-aligned
# blocks). Thin the points toward the footprint edge: 0.5 m occupancy grid, distance to the nearest empty cell d, keep with
# probability smoothstep(d / 3 m) (fixed seed), so the lawn grass fades out into the ortho ground over ~3 m instead of stopping.
import numpy as np
from mathutils.kdtree import KDTree
alive=[v for v in bm.verts if v not in set(kill)]
XY=np.array([tuple((W@v.co).xy) for v in alive]); gx0,gy0=XY.min(0)-2; GR=0.5
gi=((XY-[gx0,gy0])/GR).astype(int); occ=np.zeros(tuple(gi.max(0)+3)[::-1],bool); occ[gi[:,1],gi[:,0]]=True
nb=np.zeros_like(occ); nb[1:,:]|=occ[:-1,:]; nb[:-1,:]|=occ[1:,:]; nb[:,1:]|=occ[:,:-1]; nb[:,:-1]|=occ[:,1:]
ej,ei=np.where(~occ&nb); kd=KDTree(len(ej))
for n,(j,i) in enumerate(zip(ej,ei)): kd.insert((gx0+(i+.5)*GR,gy0+(j+.5)*GR,0),n)
kd.balance(); dp=np.array([kd.find((x,y,0))[2] for x,y in XY])-0.25; t=np.clip(dp/3.0,0,1); keep=t*t*(3-2*t)
rng=np.random.default_rng(262); thin=[v for v,k in zip(alive,keep) if rng.random()>k]
print(TAG,'edge-feather thinned',len(thin),'of',len(alive),flush=True)
kill=kill+thin
bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(me); bm.free(); me.update()
import statistics
print(TAG,'kept',len(me.vertices),'dropped',len(kill),'dz p50 %.3f min %.3f max %.3f'%(statistics.median(mv),min(mv),max(mv)),flush=True)
host=[x for x in bpy.data.objects if x.name.startswith('WS68_RHD_ground_northDTM')][0]
host.users_collection[0].objects.link(o)
print(TAG,'linked into',host.users_collection[0].name,'mods',[(m.name,getattr(m.node_group,'name',None)) for m in o.modifiers],flush=True)
print(TAG,'new node groups',sorted({n.name for n in bpy.data.node_groups}-ng0),'new objects',len({x.name for x in bpy.data.objects}-ob0),sorted({x.name for x in bpy.data.objects}-ob0)[:10],'new collections',sorted({c.name for c in bpy.data.collections}-co0),flush=True)
# merge208 turns modifiers off at load only; the appended GN modifier keeps its own Realtime bit (on) -> nothing to restore.

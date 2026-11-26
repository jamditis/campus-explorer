# ws252 read-only check (mods off, base meshes): ground under the new W63c pieces + anything else standing in their footprints
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; P=bpy.data.objects['WS251_W63b_passage_LiDAR2023_ground_patch_1m']
def bvh(o):
    M=o.matrix_world; me=o.data; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(-215<vs[i].x<-170 and 145<vs[i].y<175 for i in p.vertices)]
    return BVHTree.FromPolygons(vs,ps)
BT=bvh(T); BP=bvh(P)
def gz(x,y):
    zs=[h[0].z for b in (BT,BP) for h in [b.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)] if h[0]]
    return max(zs) if zs else np.nan
R={'plaza':[],'walk':[],'stairs':[]}
for x in np.arange(-204.9,-191.0,0.25):
    for y in np.arange(154.7,165.3,0.25):
        if x>-197.5 and y>163.8: continue
        R['plaza'].append(gz(x,y)-134.03)
for x in np.arange(-190.95,-189.6,0.2):
    for y in list(np.arange(154.7,155.9,0.2))+list(np.arange(158.7,163.8,0.2)): R['walk'].append(gz(x,y)-134.66)
NR=17; TR=6.8/16; RI=(136.56-134.03)/NR  # ws252e stairs: first riser x -190.3
for x in np.arange(-190.25,-182.6,0.2):
    k=min(NR-1,int((x+190.3)/TR))
    for y in np.arange(156.3,158.35,0.2): R['stairs'].append(gz(x,y)-(134.03+(k+1)*RI))
for k,v in R.items():
    v=np.array(v); print('Q252',k,'n',len(v),'ground-top min %.2f p50 %.2f max %.2f; poke(>-0.01) %d'%(np.nanmin(v),np.nanmedian(v),np.nanmax(v),(v>-0.01).sum()),'nan',int(np.isnan(v).sum()),flush=True)
# walk-top vs ground just east of the raised walk (x -189.4) = lip
lip=[gz(-189.4,y)-134.66 for y in np.arange(154.7,163.8,0.5) if not 155.9<y<158.7]
print('Q252 lip E of raised walk (ground - walk top)',[round(a,2) for a in lip],flush=True)
# stairs top landing vs ground east of it
print('Q252 landing E edge ground',[round(gz(-182.4,y),2) for y in (156.5,157.3,158.1)],'landing top 136.56',flush=True)
new=[o.name for o in bpy.data.objects if o.name.startswith('WS252')]
FP=[(-205,-191,154.6,165.4),(-191,-182.5,155.9,158.7)]
for o in bpy.data.objects:
    if o.type!='MESH' or o.name in new or o.name.startswith(('Terrain','WS251_W63b','WS250_W63','Footpaths_OSM','Roads_OSM')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if min(v.x for v in bb)>-190 and max(v.x for v in bb)<-150: pass
    hit=0
    for (x0,x1,y0,y1) in FP:
        if max(v.x for v in bb)<x0 or min(v.x for v in bb)>x1 or max(v.y for v in bb)<y0 or min(v.y for v in bb)>y1: continue
        if max(v.x for v in bb)-min(v.x for v in bb)>200: continue
        M=o.matrix_world
        for v in o.data.vertices:
            w=M@v.co
            if x0<w.x<x1 and y0<w.y<y1 and 133<w.z<140: hit+=1
    if hit: print('Q252 inside footprint',o.name,hit,flush=True)
os._exit(0)

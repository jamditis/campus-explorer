# ws232 probe b: W53b. For the CELS/Calcia walk overlays (OX_/OY_/PB2_/OW3_) find verts lying >3 m under the EVALUATED top ground
# in x 112..152, y 182..252 and compute their lifted z: dz = (evaluated Footpaths/Roads surface - raw base-mesh surface) at that xy
# (the overlays were built on the raw walk heights before the OO/OP redrape GN lifted the walks ~9 m onto the LiDAR/3DEP ground);
# verts with no paving under them take the nearest paving vert's dz, then are clamped to evaluated ground +0.005..+0.15 m.
import bpy,sys,os,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
M='/workspace/nj-scenes/montclair-state/'
G=['Terrain_LiDAR_DTM_1m','WS60_terrain_edge_apron_LiDAR_to_skirt','QG_north_strip_LiDAR_terrain_patch','QH_east_fan_LiDAR_terrain_patch','QI_east_edge_LiDAR_terrain_patch','QW_DTM_north_edge_ramp_UNVERIFIED','QM_terrain_band_underlay_UNVERIFIED','WU_richardson_reid_LiDAR_patch_UNVERIFIED']
PV=['Footpaths_OSM','Roads_OSM']
OV=['OW3_CELS_walk_road_curb_lip_UNVERIFIED','OX_CELS_walk_road_lip_smoothed_UNVERIFIED','OX_CELS_walk_edge_grime_feather_UNVERIFIED','OX_CELS_walk_scoring_joints_UNVERIFIED','OY_walk_panel_tone_CELS_Calcia_UNVERIFIED','OY_walk_scoring_joints_CELS_Calcia_UNVERIFIED','PB2_walk_lawn_fillet_UNVERIFIED']
with bpy.data.libraries.load(M+os.environ.get('PF','montclair_state.blend'),link=False) as (src,dst):
    dst.objects=[n for n in G+PV+OV if n in src.objects]
O={o.name:o for o in dst.objects if o}
for o in O.values(): bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o,ev=True):
    if ev:
        e=o.evaluated_get(dg); mm=e.to_mesh()
    else: mm=o.data
    W=o.matrix_world; b=BVHTree.FromPolygons([W@v.co for v in mm.vertices],[p.vertices[:] for p in mm.polygons])
    if ev: e.to_mesh_clear()
    return b
GB=[bvh(O[n]) for n in G if n in O]
PE={n:bvh(O[n]) for n in PV}; PR={n:bvh(O[n],False) for n in PV}
def top(bl,x,y):
    z=[h[0].z for h in (b.ray_cast(Vector((x,y,400)),Vector((0,0,-1))) for b in bl) if h[0] is not None]
    return max(z) if z else None
def rawhit(b,x,y,zref):
    # raw base surface nearest below/above zref (overlay sits on it)
    best=None; z=zref+3
    h=b.ray_cast(Vector((x,y,z)),Vector((0,0,-1)),6.0)
    return None if h[0] is None else h[0].z
out={}; rep={}
for n in OV:
    if n not in O: continue
    o=O[n]; W=o.matrix_world; Wi=W.inverted()
    cand=[]; pav={}
    for v in o.data.vertices:
        w=W@v.co
        if not (112<w.x<152 and 182<w.y<252): continue
        g=top(GB,w.x,w.y)
        if g is None or w.z>g-3: continue
        cand.append((v.index,w,g))
        for pn in PV:
            r=rawhit(PR[pn],w.x,w.y,w.z); e=PE[pn].ray_cast(Vector((w.x,w.y,400)),Vector((0,0,-1)))[0]
            if r is not None and e is not None and e.z>r+2: pav[v.index]=e.z-r; break
    if not cand: continue
    kd=KDTree(len(pav)); idx=list(pav)
    vco={v.index:(W@v.co) for v in o.data.vertices}
    for i,k in enumerate(idx): kd.insert(vco[k],i)
    kd.balance(); res={}; cl=0
    for vi,w,g in cand:
        if vi in pav: dz=pav[vi]; nz=w.z+dz
        elif idx:
            co,i,d=kd.find(w); dz=pav[idx[i]]; nz=w.z+dz
            lo,hi=g+0.005,g+0.15
            if nz<lo or nz>hi: nz=min(max(nz,lo),hi); cl+=1
        else: nz=g+0.01; cl+=1
        res[vi]=[round(nz,4),1 if vi in pav else 0]
    out[n]=res; rep[n]={'cand':len(cand),'on_paving':len(pav),'clamped':cl,'dz_min':round(min(pav.values()),2) if pav else None,'dz_max':round(max(pav.values()),2) if pav else None}
    print('P232B',n,rep[n],flush=True)
json.dump(out,open(M+'scripts/ws232/lift232_targets.json','w'))
print('P232B wrote',sum(len(v) for v in out.values()),flush=True)
sys.stdout.flush(); os._exit(0)

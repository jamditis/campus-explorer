"""wv fix2: (a) snap x=120 verts to WU's x=120 verts and x=155 verts to WN/WO's x=155 verts by matching y;
(b) recompute wv_in treating Stone-hole edges as non-open (3 m wall probe);
(c) north fade y312-320 toward skirt only where WF/WO do not cover y=320; grass follows;
(d) poke check. Save."""
import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R='/workspace/nj-scenes/montclair-state'
O=bpy.data.objects
E=O['WV_stone_west_LiDAR_patch_UNVERIFIED']; sk=O['Context_skirt_3DEP_ortho_4km']
WU=O['WU_richardson_reid_LiDAR_patch_UNVERIFIED']; WN=O['WN_south_wood_LiDAR_patch_ext_UNVERIFIED']; WO=O['WO_gully_head_LiDAR_patch_UNVERIFIED']; WF=O['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
def ss(t):
    t=min(max(t,0.0),1.0); return t*t*(3-2*t)
def bvh(o,ev=True):
    dg=bpy.context.evaluated_depsgraph_get()
    if ev:
        e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(b,x,y):
    h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
rep={}
me=E.data; mw=E.matrix_world; mi=mw.inverted()
def edge_snap(X,objs,tag):
    by={}
    for o in objs:
        for v in o.data.vertices:
            c=o.matrix_world@v.co
            if abs(c.x-X)<0.08: by.setdefault(round(c.y,2),[]).append(c.z)
    n=0;mx=0.0
    for v in me.vertices:
        c=mw@v.co
        if abs(c.x-X)>0.01: continue
        ys=[y for y in by if abs(y-c.y)<0.02]
        if not ys: continue
        zt=float(np.median(by[min(ys,key=lambda y:abs(y-c.y))])); d=zt-c.z
        if abs(d)>1e-4: c.z=zt; v.co=mi@c; n+=1; mx=max(mx,abs(d))
    rep['snap_'+tag]=[n,round(mx,4),len(by)]; print('SNAP',tag,n,round(mx,4),len(by),flush=True)
edge_snap(120.0,[WU],'x120_WU'); edge_snap(155.0,[WN,WO],'x155_WNWO')
me.update()
# (b)
cnt={}
for p in me.polygons:
    for ek in p.edge_keys: cnt[ek]=cnt.get(ek,0)+1
bv=set()
for ek,c in cnt.items():
    if c==1: bv.update(ek)
kt=KDTree(max(1,len(bv)))
for i in bv: kt.insert(me.vertices[i].co,i)
kt.balance()
GN=['WU_richardson_reid_LiDAR_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','RZ2_SC_LiDAR_ground_patch_UNVERIFIED','Terrain_LiDAR_DTM_1m','WN_south_wood_LiDAR_patch_ext_UNVERIFIED','WO_gully_head_LiDAR_patch_UNVERIFIED','WT_richardson_west_LiDAR_patch_UNVERIFIED']
if O.get('QG_north_strip_LiDAR_terrain_patch'): GN.append('QG_north_strip_LiDAR_terrain_patch')
grounds=[bvh(O[n]) for n in GN]
bld=[bvh(O['TI_Stone_Hall_313028565_lower_UNVERIFIED'],False)]
BE=bvh(E,False)
opn=[]
for i in bv:
    c=mw@me.vertices[i].co
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
        x,y=c.x+0.7*dx,c.y+0.7*dy
        if hz(BE,x,y) is not None: continue
        if any(hz(b,x,y) is not None for b in grounds): continue
        if any(hz(b,c.x+d*dx,c.y+d*dy) is not None for d in (0.5,1.0,1.5,2.0,2.5,3.0) for b in bld): continue
        opn.append(i); break
rep['open']=[len(opn),len(bv)]; print('OPEN',len(opn),'of',len(bv),flush=True)
OPN=[[round((mw@me.vertices[i].co).x,1),round((mw@me.vertices[i].co).y,1)] for i in opn]
rep['open_xy_sample']=OPN[:60]
ko=KDTree(max(1,len(opn)))
for i in opn: ko.insert(me.vertices[i].co,i)
ko.balance()
a=me.attributes['wv_in']
for v in me.vertices:
    _,_,d=kt.find(v.co); w=ss(d/0.8)
    if opn:
        _,_,do=ko.find(v.co); w=min(w,ss((do-4.5)/4.0))
    a.data[v.index].value=0.40*w
me.update()
# (c) north fade where WF/WO don't cover
bpy.context.view_layer.update()
BS=bvh(sk); BWF=bvh(WF); BWO=bvh(WO); BE0=bvh(E)
n=0;mx=0.0;skn=0
for v in me.vertices:
    c=mw@v.co
    if c.y<312: continue
    if hz(BWF,c.x,320.4) is not None or hz(BWF,c.x,c.y+0.8) is not None or hz(BWO,c.x,c.y+0.8) is not None or hz(BWO,c.x+0.8,c.y) is not None:
        skn+=1; continue
    s=hz(BS,c.x,320.6) or hz(BS,c.x,c.y)
    if s is None: continue
    w=ss((c.y-312.0)/8.0)
    if w<=1e-4: continue
    nz=c.z*(1-w)+s*w; d=nz-c.z
    if abs(d)>1e-4: c.z=nz; v.co=mi@c; n+=1; mx=max(mx,abs(d))
me.update(); rep['north_fade']=[n,round(mx,3),skn]; print('NFADE',n,round(mx,3),skn,flush=True)
bpy.context.view_layer.update(); BE2=bvh(E)
if n:
    for name in ('QS_Richardson_lawn_grass_points_UNVERIFIED','QV_Richardson_NW_lawn_grass_points_UNVERIFIED'):
        o=O.get(name)
        if not o: continue
        meo=o.data; mwo=o.matrix_world; mio=mwo.inverted(); k=0
        for v in meo.vertices:
            c=mwo@v.co
            if not (120<=c.x<=155 and 312<=c.y<=320): continue
            a0=hz(BE0,c.x,c.y); a1=hz(BE2,c.x,c.y)
            if a0 is None or a1 is None or abs(a1-a0)<1e-4: continue
            c.z+=a1-a0; v.co=mio@c; k+=1
        meo.update(); rep['grass_nfade_'+name[:2]]=k
# (d) poke
bpy.context.view_layer.update(); BE3=bvh(E); BS=bvh(sk)
pk=0;pkmax=0.0;hist={}
for p in me.polygons:
    c=mw@p.center
    for fx,fy in ((0,0),(0.25,0.25),(-0.25,0.25),(0.25,-0.25),(-0.25,-0.25)):
        h=hz(BE3,c.x+fx,c.y+fy); s=hz(BS,c.x+fx,c.y+fy)
        if h is not None and s is not None and s>h-0.003:
            pk+=1; d=s-h; pkmax=max(pkmax,d); k=int(c.x)//4*4; hist.setdefault(k,[0,0.0]); hist[k][0]+=1; hist[k][1]=max(hist[k][1],round(d,3))
rep['poke']=[pk,round(pkmax,3),sorted(hist.items())]; print('POKE',pk,round(pkmax,3),sorted(hist.items()),flush=True)
# step check at shared edges: neighbour vs patch z
def stepchk(X,objs):
    BN=[bvh(o) for o in objs]; out=[]
    for y in np.arange(245.5,320,1.0):
        a=hz(BE3,X+0.3*(1 if X<140 else -1),y); b=None
        for B in BN:
            z=hz(B,X-0.3*(1 if X<140 else -1),y)
            if z is not None: b=z
        if a is not None and b is not None: out.append(abs(a-b))
    return [len(out),round(float(np.max(out)),3) if out else None,round(float(np.median(out)),3) if out else None]
rep['step_x120']=stepchk(120.0,[WU]); rep['step_x155']=stepchk(155.0,[WN,WO]); print('STEPS',rep['step_x120'],rep['step_x155'],flush=True)
r=json.load(open(f'{R}/data/wv/fix_report.json')); r['fix2']=rep
json.dump(r,open(f'{R}/data/wv/fix_report.json','w'),indent=1)
bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)

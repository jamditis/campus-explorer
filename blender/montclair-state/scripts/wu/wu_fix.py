"""wu: Tile B 2017 B17 J5D6 1 m DTM patch, Richardson/Reid x80-120, y245-320.
Faces only where the top ground is still the 3DEP skirt (WT/QW/WF/RZ2/Terrain keep their cells);
Richardson footprints (plinth/glass piers/towers/G floor) masked — no in-scene Reid mesh;
1-cell tuck ring 3 cm under neighbours; WT x72-80 unfeathered to raw LiDAR and x=80 shared exactly
(no west feather); east edge x112->120 fades to skirt; QW east segment (x107-120, y248-276) unfeathered
+ tucked (not deleted); skirt GN copied from WT (subdiv 0, gated dip, Math.001 B=1 C=0.02);
apron + walks raised per-xy group (never lowered); grass re-projected; patch tucked 3 cm under
slabs; open (skirt-facing) edge snapped to skirt-1 cm; walls not pulled down.
"""
import bpy, bmesh, numpy as np, json, math, re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R='/workspace/nj-scenes/montclair-state'
X0,X1,Y0,Y1=80,120,245,320
GX0,GY0=40,140
FE0,FE1=112.0,120.0  # east fade
rep={}
g=np.load(f'{R}/data/wo/chm_grid_sw_1m.npz'); kd=[f for f in g.files if f.endswith('dtm')][0]; L=g[kd].copy()
for _ in range(40):
    n=np.isnan(L)
    if not n.any(): break
    P=np.pad(L,1,constant_values=np.nan)
    nb=np.stack([P[0:-2,1:-1],P[2:,1:-1],P[1:-1,0:-2],P[1:-1,2:],P[0:-2,0:-2],P[2:,2:],P[0:-2,2:],P[2:,0:-2]])
    with np.errstate(all='ignore'): m=np.nanmean(nb,axis=0)
    L[n]=m[n]
def lv(x,y):
    i=int(round(x))-GX0; j=int(round(y))-GY0
    zs=[L[jj,ii] for jj in (j-1,j) for ii in (i-1,i) if 0<=jj<L.shape[0] and 0<=ii<L.shape[1] and np.isfinite(L[jj,ii])]
    return float(np.mean(zs)) if zs else None
def ss(t):
    t=min(max(t,0.0),1.0); return t*t*(3-2*t)
def slug(n):
    return re.sub(r'[^A-Za-z0-9_-]+','_',n)[:90]
O=bpy.data.objects
sk=O['Context_skirt_3DEP_ortho_4km']; RZ=O['RZ2_SC_LiDAR_ground_patch_UNVERIFIED']
QW=O['QW_DTM_north_edge_ramp_UNVERIFIED']; WF=O['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
TL=O['Terrain_LiDAR_DTM_1m']; WT=O['WT_richardson_west_LiDAR_patch_UNVERIFIED']
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o,ev=True):
    if ev:
        e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(b,x,y):
    h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
BS=bvh(sk)
BN={n:bvh(o) for n,o in (('RZ2',RZ),('QW',QW),('WF',WF),('TL',TL),('WT',WT))}
FP=['QT_Richardson_base_plinth_UNVERIFIED','QP_Richardson_ground_storey_glass_piers_UNVERIFIED','QP_Richardson_white_corner_towers_UNVERIFIED','QU_G_floor_UNVERIFIED']
BF=[bvh(O[n]) for n in FP]
def inb(bl,x,y): return any(b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0] is not None for b in bl)
def drop_face(x,y):
    # Richardson (glass ground storey): drop if centre inside and >=3 corners inside. No slit buffer (wt review).
    # No in-scene Reid Hall mesh — do not invent an OSM-only hole.
    cs=[(x,y),(x+1,y),(x,y+1),(x+1,y+1)]
    if inb(BF,x+0.5,y+0.5) and sum(inb(BF,a,b) for a,b in cs)>=3: return True
    return False
def skz(x,y): return hz(BS,x,y)
def target(x,y):
    r=lv(x,y); s=skz(x,y)
    if r is None: return s
    if s is None: return r
    w=ss((x-FE0)/(FE1-FE0)); return r*(1-w)+s*w
def nbz(x,y):
    best=None;who=None
    for n,b in BN.items():
        z=hz(b,x,y)
        if z is not None and (best is None or z>best): best=z;who=n
    return best,who
# --- 1. classify faces
prim=set(); cov={}
for y in range(Y0,Y1):
    for x in range(X0,X1):
        if drop_face(x,y): continue
        z,w=nbz(x+0.5,y+0.5)
        if w is None: prim.add((x,y))
        else: cov[(x,y)]=w
ring=set()
for (x,y) in cov:
    if any((x+dx,y+dy) in prim for dx in (-1,0,1) for dy in (-1,0,1)): ring.add((x,y))
faces=prim|ring
rep['faces_prim']=len(prim); rep['faces_ring']=len(ring)
rep['ring_by']={k:sum(1 for f in ring if cov[f]==k) for k in BN}
rep['cov_by']={k:sum(1 for f in cov if cov[f]==k) for k in BN}
print('STEP faces prim',len(prim),'ring',len(ring),rep['ring_by'],flush=True)
if not prim:
    json.dump(rep,open(f'{R}/data/wu/fix_report.json','w'),indent=1)
    raise SystemExit('no primary faces')
# --- 2. neighbour unfeather toward raw LiDAR (within 6 m of primary centres)
kt=KDTree(len(prim))
for i,(x,y) in enumerate(prim): kt.insert(Vector((x+0.5,y+0.5,0)),i)
kt.balance()
def alpha(x,y):
    _,_,d=kt.find(Vector((x,y,0))); return 1-ss(max(0.0,d-0.71)/6.0)
# WT: especially x72-80 feather; QW east segment; WF south; RZ2/TL if any
for tag,o,box in (
    ('wt',WT,(70,90,238,330)),
    ('qw',QW,(100,130,240,285)),
    ('wf',WF,(78,130,312,330)),
    ('rz2',RZ,(78,90,238,330)),
):
    me=o.data; mw=o.matrix_world; mi=mw.inverted()
    np.save(f'{R}/data/wu/{tag}_verts_bak.npy',np.array([v.co[:] for v in me.vertices]))
    n=0;mx=0.0
    for v in me.vertices:
        c=mw@v.co
        if not (box[0]<=c.x<=box[1] and box[2]<=c.y<=box[3]): continue
        a=alpha(c.x,c.y)
        if a<=1e-4: continue
        t=target(c.x,c.y)
        if t is None: continue
        nz=c.z*(1-a)+t*a
        if abs(nz-c.z)>1e-4: n+=1; mx=max(mx,abs(nz-c.z))
        c.z=nz; v.co=mi@c
    me.update(); rep['unfeather_'+tag]=[n,round(mx,3)]
    print('UNFEATHER',tag,n,round(mx,3),flush=True)
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
BN={n:bvh(o) for n,o in (('RZ2',RZ),('QW',QW),('WF',WF),('TL',TL),('WT',WT))}
BWT=BN['WT']
# --- 3. patch mesh
vk=set()
for (x,y) in faces: vk.update({(x,y),(x+1,y),(x,y+1),(x+1,y+1)})
pv={(x,y) for (x,y) in prim for (x,y) in [(x,y),(x+1,y),(x,y+1),(x+1,y+1)]}
Z={}; tuck=0; shared=0
for (x,y) in vk:
    t=target(x,y)
    z,w=nbz(x,y)
    if abs(x-80)<0.01:
        zt=hz(BWT,80.0,y)
        if zt is not None: t=zt; shared+=1
    elif (x,y) not in pv and z is not None:
        t=z-0.03; tuck+=1
    elif z is not None and t is not None and abs(t-z)<0.6:
        t=min(t,z-0.005) if (x,y) not in pv else t
    Z[(x,y)]=t if t is not None else 137.0
rep['tuck_verts']=tuck; rep['shared_x80']=shared
bm=bmesh.new(); vid={}
for k,z in Z.items(): vid[k]=bm.verts.new((k[0],k[1],z))
for (x,y) in faces:
    f=bm.faces.new([vid[(x,y)],vid[(x+1,y)],vid[(x+1,y+1)],vid[(x,y+1)]]); f.smooth=True
# ortho UV from WT (same OW2 material / linear world fit)
me=WT.data; mw=WT.matrix_world; uvl=me.uv_layers['ortho']
A,U,V=[],[],[]
for li in range(0,len(me.loops),7):
    c=mw@me.vertices[me.loops[li].vertex_index].co; uv=uvl.data[li].uv; A.append([c.x,c.y,1]); U.append(uv[0]); V.append(uv[1])
A=np.array(A); cu=np.linalg.lstsq(A,np.array(U),rcond=None)[0]; cv=np.linalg.lstsq(A,np.array(V),rcond=None)[0]
rep['uv_fit_resid']=float(np.abs(A@cu-np.array(U)).max())
lay=bm.loops.layers.uv.new('ortho')
for f in bm.faces:
    for l in f.loops:
        c=l.vert.co; l[lay].uv=(cu[0]*c.x+cu[1]*c.y+cu[2],cv[0]*c.x+cv[1]*c.y+cv[2])
EN='WU_richardson_reid_LiDAR_patch_UNVERIFIED'
em=bpy.data.meshes.new(EN); bm.to_mesh(em); bm.free()
em.materials.append(WT.data.materials[0])
E=O.new(EN,em)
col=bpy.data.collections.new('WU_richardson_reid_LiDAR_UNVERIFIED'); bpy.context.scene.collection.children.link(col); col.objects.link(E)
E['wu_obj']=1
E['UNVERIFIED']='wu: 2017 B17 J5D6 class-2 1 m DTM, Tile B x80-120,y245-320 (only cells not already WT/QW/WF/RZ2/Terrain); Richardson masked (centre + >=3 corners; no upper-block, no invented Reid hole); tuck ring 3 cm; x=80 shared with WT (WT x72-80 unfeathered); east fade x112-120; material = OW2 ortho lawn'
ev=[E.matrix_world@v.co for v in em.vertices]
# attributes ou_edge / ow2_strip from WT + RZ2 + QW + eval skirt
e=sk.evaluated_get(dg); sm=e.to_mesh()
for an in ('ou_edge','ow2_strip'):
    pts=[];vals=[]
    for o,mm in ((WT,WT.data),(RZ,RZ.data),(QW,QW.data),(sk,sm)):
        a=mm.attributes.get(an)
        if not a or a.domain!='POINT': continue
        mwo=o.matrix_world
        for i,v in enumerate(mm.vertices):
            c=mwo@v.co
            if 50<c.x<160 and 220<c.y<350: pts.append(c.copy()); vals.append(a.data[i].value)
    rep['attr_src_'+an]=len(pts)
    if not pts: continue
    k2=KDTree(len(pts))
    for i,p in enumerate(pts): k2.insert(p,i)
    k2.balance()
    na=em.attributes.new(an,'FLOAT','POINT')
    for i,c in enumerate(ev):
        res=k2.find_n(c,4); ws=sum(1/(d+0.3) for _,_,d in res)
        na.data[i].value=sum(vals[j]/(d+0.3) for _,j,d in res)/ws
e.to_mesh_clear()
# wu_in: 0.40*ss(d_boundary/0.8), gated off within 4.5 m of open (skirt-facing) edges
cnt={}
for p in em.polygons:
    for ek in p.edge_keys: cnt[ek]=cnt.get(ek,0)+1
bv=set()
for ek,c in cnt.items():
    if c==1: bv.update(ek)
ktb=KDTree(max(1,len(bv)))
for i in bv: ktb.insert(em.vertices[i].co,i)
ktb.balance()
NB_open=[BN[n] for n in BN]+ [bvh(O[n],False) for n in FP]
BE0=BVHTree.FromPolygons([E.matrix_world@v.co for v in em.vertices],[tuple(p.vertices) for p in em.polygons])
def hit(b,x,y): return b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0] is not None
opn=[]
for i in bv:
    c=E.matrix_world@em.vertices[i].co
    for dx,dy in ((0.7,0),(-0.7,0),(0,0.7),(0,-0.7)):
        x,y=c.x+dx,c.y+dy
        if not hit(BE0,x,y) and not any(hit(b,x,y) for b in NB_open):
            opn.append(i); break
ko=KDTree(max(1,len(opn)))
for i in opn: ko.insert(em.vertices[i].co,i)
ko.balance()
ina=em.attributes.new('wu_in','FLOAT','POINT')
for v in em.vertices:
    _,_,d=ktb.find(v.co); w=ss(d/0.8)
    if opn:
        _,_,do=ko.find(v.co); w=min(w,ss((do-4.5)/4.0))
    ina.data[v.index].value=0.40*w
rep['open_boundary_verts']=len(opn); rep['boundary_verts']=len(bv)
rep['patch_faces']=len(em.polygons); rep['patch_verts']=len(em.vertices)
rep['zmin']=round(min(c.z for c in ev),2); rep['zmax']=round(max(c.z for c in ev),2)
print('PATCH',rep['patch_faces'],'verts',rep['patch_verts'],'open',len(opn),'shared',shared,'tuck',tuck,flush=True)
# --- 4. skirt GN (copy WT, already gated; remap x 20->60, 100->140)
src=bpy.data.node_groups['WT_skirt_under_richardson_west']
ng=src.copy(); ng.name='WU_skirt_under_richardson_reid'
mp={20.0:60.0,100.0:140.0}
for n in ng.nodes:
    if n.bl_idname=='GeometryNodeObjectInfo': n.inputs['Object'].default_value=E
    if n.bl_idname=='GeometryNodeInputNamedAttribute' and n.inputs['Name'].default_value in ('wt_in','wo_in'):
        n.inputs['Name'].default_value='wu_in'
    if n.bl_idname=='GeometryNodeSubdivideMesh': n.inputs['Level'].default_value=0
    if n.bl_idname=='FunctionNodeCompare':
        v=round(n.inputs[1].default_value,3)
        if v in mp: n.inputs[1].default_value=mp[v]
# keep Math.001 B=1 C=0.02 (copied from WT)
m001=ng.nodes.get('Math.001')
if m001:
    m001.inputs[1].default_value=1.0; m001.inputs[2].default_value=0.02
    rep['math001']=[round(m001.inputs[1].default_value,3),round(m001.inputs[2].default_value,3)]
rep['wu_cmp']=[(n.name,round(n.inputs[1].default_value,3)) for n in ng.nodes if n.bl_idname=='FunctionNodeCompare']
md=sk.modifiers.new('WU_skirt_under_richardson_reid','NODES'); md.node_group=ng
sk['UNVERIFIED_wu']='wu: skirt dipped (WT recipe, subdiv 0, gated) under WU Richardson/Reid LiDAR patch (GN, mesh unedited)'
# --- 4b. recompute WT wt_in now that WU covers x>=80 (x=80 no longer an open skirt edge)
mew=WT.data
cntw={}
for p in mew.polygons:
    for ek in p.edge_keys: cntw[ek]=cntw.get(ek,0)+1
bvw=set()
for ek,c in cntw.items():
    if c==1: bvw.update(ek)
ktw=KDTree(max(1,len(bvw)))
for i in bvw: ktw.insert(mew.vertices[i].co,i)
ktw.balance()
BEnow=BVHTree.FromPolygons([E.matrix_world@v.co for v in em.vertices],[tuple(p.vertices) for p in em.polygons])
NBw=[BN[n] for n in ('RZ2','QW','WF','TL')]+[bvh(O[n],False) for n in FP]+[BEnow]
def hit2(b,x,y): return b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0] is not None
BE_WT=BN['WT']
opnw=[]
for i in bvw:
    c=WT.matrix_world@mew.vertices[i].co
    for dx,dy in ((0.7,0),(-0.7,0),(0,0.7),(0,-0.7)):
        x,y=c.x+dx,c.y+dy
        if not hit2(BE_WT,x,y) and not any(hit2(b,x,y) for b in NBw):
            opnw.append(i); break
kow=KDTree(max(1,len(opnw)))
for i in opnw: kow.insert(mew.vertices[i].co,i)
kow.balance()
aw=mew.attributes.get('wt_in')
if aw:
    for v in mew.vertices:
        _,_,d=ktw.find(v.co); w=ss(d/0.8)
        if opnw:
            _,_,do=kow.find(v.co); w=min(w,ss((do-4.5)/4.0))
        aw.data[v.index].value=0.40*w
    mew.update()
rep['wt_open_after']=len(opnw)
print('WT open-after WU',len(opnw),'of',len(bvw),flush=True)
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
BE=bvh(E); BS2=bvh(sk)
BN={n:bvh(o) for n,o in (('RZ2',RZ),('QW',QW),('WF',WF),('TL',TL),('WT',WT))}
def gtop(x,y):
    zs=[hz(b,x,y) for b in [BE,BS2]+list(BN.values())]; zs=[z for z in zs if z is not None]; return max(zs) if zs else None
# poke-through
pk=0;pkmax=0.0;hist={}
for (x,y) in prim:
    for fx,fy in ((0.25,0.25),(0.75,0.25),(0.25,0.75),(0.75,0.75),(0.5,0.5)):
        a=hz(BE,x+fx,y+fy); s=hz(BS2,x+fx,y+fy)
        if a is not None and s is not None and s>a-0.003:
            pk+=1; d=s-a; pkmax=max(pkmax,d); k=int(x)//4*4; hist.setdefault(k,[0,0.0]); hist[k][0]+=1; hist[k][1]=max(hist[k][1],round(d,3))
rep['skirt_poke']=[pk,round(pkmax,3),sorted((k,v) for k,v in hist.items())]
print('POKE',pk,round(pkmax,3),flush=True)
# --- 5. apron + walks: raise per-xy group to ground + clearance (never lower)
def raise_obj(o,clr,box,tag):
    me=o.data; mw=o.matrix_world; mi=mw.inverted()
    np.save(f'{R}/data/wu/{tag}_verts_bak.npy',np.array([v.co[:] for v in me.vertices]))
    grp={}
    for v in me.vertices:
        c=mw@v.co
        if box[0]<=c.x<=box[1] and box[2]<=c.y<=box[3]: grp.setdefault((round(c.x,2),round(c.y,2)),[]).append((v,c))
    n=0;mx=0.0;before=[];after=[]
    for (x,y),lst in grp.items():
        top=max(c.z for _,c in lst); gz=gtop(x,y)
        if gz is None: continue
        before.append(top-gz)
        d=(gz+clr)-top
        if d>0.002:
            for v,c in lst: c.z+=d; v.co=mi@c
            n+=1; mx=max(mx,d); after.append(clr)
        else: after.append(top-gz)
    me.update()
    f=lambda a: [round(float(np.median(a)),3),round(float(np.percentile(a,5)),3),round(float(min(a)),3),round(float(max(a)),3)] if a else None
    rec={'groups':len(grp),'raised':n,'max_raise':round(mx,3),'dz_vs_ground_before[med,p5,min,max]':f(before),'after':f(after)}
    rep['raise_'+tag]=rec
    print('RAISE',tag,rec,flush=True)
box=(X0-0.5,X1+0.5,Y0-0.5,Y1+0.5)
raise_obj(O['QQ_Richardson_paved_apron_UNVERIFIED'],0.02,box,'apron')
for n in ('QS_footway_313027436_UNVERIFIED','QT_soil_edge_313027436_UNVERIFIED','QS_footway_313027437_UNVERIFIED','QT_soil_edge_313027437_UNVERIFIED','QS_service_546643370_UNVERIFIED'):
    o=O.get(n)
    if o: raise_obj(o,0.03 if ('footway' in n or 'service' in n) else 0.015,box,slug(n))
# --- 6. grass
for n in ('QS_Richardson_lawn_grass_points_UNVERIFIED','QV_Richardson_NW_lawn_grass_points_UNVERIFIED'):
    o=O.get(n)
    if not o: continue
    me=o.data; mw=o.matrix_world; mi=mw.inverted()
    np.save(f'{R}/data/wu/{slug(n)}_verts_bak.npy',np.array([v.co[:] for v in me.vertices]))
    k=0;mx=0.0
    for v in me.vertices:
        c=mw@v.co
        if (int(math.floor(c.x)),int(math.floor(c.y))) not in faces: continue
        a=hz(BE,c.x,c.y); s=skz(c.x,c.y)
        if a is None or s is None: continue
        d=a-s; c.z+=d; v.co=mi@c; k+=1; mx=max(mx,abs(d))
    me.update(); rep['grass_'+n[:2]]=[k,round(mx,3)]
    print('GRASS',n[:2],k,round(mx,3),flush=True)
# --- 7. tuck patch 3 cm under walk/apron slabs (only lowering <=0.15 m)
np.save(f'{R}/data/wu/wu_patch_pre_tuck.npy',np.array([v.co[:] for v in em.vertices]))
dg=bpy.context.evaluated_depsgraph_get()
SL=[o for o in (O.get(n) for n in ('QS_footway_313027436_UNVERIFIED','QT_soil_edge_313027436_UNVERIFIED','QS_footway_313027437_UNVERIFIED','QT_soil_edge_313027437_UNVERIFIED','QS_service_546643370_UNVERIFIED','QQ_Richardson_paved_apron_UNVERIFIED')) if o]
SB=[bvh(o) for o in SL]
mw=E.matrix_world; mi=mw.inverted(); n=0;mx=0.0; CAP=0.15
for v in em.vertices:
    c=mw@v.co; lo=None
    for dx,dy in ((0,0),(0.5,0),(-0.5,0),(0,0.5),(0,-0.5)):
        for b in SB:
            h=b.ray_cast(Vector((c.x+dx,c.y+dy,500)),Vector((0,0,-1)))[0]
            if h is not None and (lo is None or h.z<lo): lo=h.z
    if lo is not None and c.z>lo-0.03 and c.z-(lo-0.03)<=CAP:
        d=c.z-(lo-0.03); c.z=lo-0.03; v.co=mi@c; n+=1; mx=max(mx,d)
em.update(); rep['walk_tuck']=[n,round(mx,3)]
print('TUCK slabs',n,round(mx,3),flush=True)
# --- 8. snap open (skirt-facing) boundary to eval skirt - 1 cm; |offset|<=0.20 m
dg=bpy.context.evaluated_depsgraph_get(); BS3=bvh(sk); BE3=bvh(E)
NB3=[BN[n] for n in BN]+[bvh(O[n],False) for n in FP]
off={}; BIG=[]
for i in bv:
    c=mw@em.vertices[i].co
    for dx,dy in ((0.7,0),(-0.7,0),(0,0.7),(0,-0.7)):
        x,y=c.x+dx,c.y+dy
        if hz(BE3,x,y) is None and not any(hz(b,x,y) is not None for b in NB3):
            h=hz(BS3,c.x,c.y)
            if h is not None:
                d0=(h-0.01)-c.z
                if abs(d0)<=0.20: off[i]=d0
                else: BIG.append([round(c.x,1),round(c.y,1),round(d0,2)])
            break
if off:
    kto=KDTree(len(off))
    for i in off: kto.insert(em.vertices[i].co,i)
    kto.balance()
    mx=0.0; n=0
    for v in em.vertices:
        if v.index in off: d=off[v.index]
        else:
            res=kto.find_n(v.co,3); ws=0; s=0
            for _,j,dd in res:
                if dd<3.0: w=1-ss(dd/3.0); ws+=w; s+=w*off[j]
            d=s/ws*min(1,ws) if ws>0 else 0.0
        if abs(d)>1e-4:
            c=mw@v.co; c.z+=d; v.co=mi@c; n+=1; mx=max(mx,abs(d))
    em.update()
    vals=list(off.values())
    rep['open_snap']={'open':len(off),'moved':n,'max':round(mx,3),'off_min':round(min(vals),3),'off_max':round(max(vals),3),'skipped_gt_0.20m':BIG[:30]}
    print('SNAP',rep['open_snap'],flush=True)
else:
    rep['open_snap']={'open':0,'skipped_gt_0.20m':BIG[:30]}; print('SNAP none',BIG[:10],flush=True)
# --- 9. wall feet (report only)
wf={}
def infp(x,y): return inb(BF,x,y)
for n in FP:
    o=O[n]; mw=o.matrix_world; feet=[]
    for v in o.data.vertices:
        c=mw@v.co
        if X0-1<=c.x<=X1+1 and Y0<=c.y<=Y1: feet.append(c)
    if not feet: continue
    zmin=min(c.z for c in feet); bot=[c for c in feet if c.z<zmin+0.05]; gaps=[]
    for c in bot:
        best=None
        for dx,dy in ((0.6,0),(-0.6,0),(0,0.6),(0,-0.6)):
            if infp(c.x+dx,c.y+dy): continue
            gz=gtop(c.x+dx,c.y+dy)
            if gz is not None: best=gz if best is None else min(best,gz)
        if best is not None: gaps.append(best-c.z)
    wf[n[:50]]={'foot_z':round(zmin,3),'n':len(bot),'ground_minus_foot[min,med,max]':[round(min(gaps),3),round(float(np.median(gaps)),3),round(max(gaps),3)] if gaps else None}
rep['wall_feet']=wf
# --- 10. door sills vs raised apron / ground
doors=O['QQ_Richardson_entrance_doors_UNVERIFIED']
apron=O['QQ_Richardson_paved_apron_UNVERIFIED']
BA=bvh(apron); mw=doors.matrix_world
sill=[]
zmin=min((mw@v.co).z for v in doors.data.vertices)
for v in doors.data.vertices:
    c=mw@v.co
    if c.z>zmin+0.08: continue
    if not (70<=c.x<=90 and 235<=c.y<=300): continue
    az=hz(BA,c.x,c.y); gz=gtop(c.x,c.y)
    sill.append({'xy':[round(c.x,2),round(c.y,2)],'sill':round(c.z,3),'apron':None if az is None else round(az,3),'ground':None if gz is None else round(gz,3),'apron_minus_sill':None if az is None else round(az-c.z,3)})
rep['door_sills_sample']=sill[:40]
rep['door_sill_zmin_all']=round(zmin,3)
if sill:
    ams=[s['apron_minus_sill'] for s in sill if s['apron_minus_sill'] is not None]
    rep['door_apron_minus_sill']={'n':len(ams),'min':round(min(ams),3),'med':round(float(np.median(ams)),3),'max':round(max(ams),3)} if ams else None
    print('DOORS',rep.get('door_apron_minus_sill'),'n_bot_in_box',len(sill),flush=True)
# --- 11. trees near
tr=[]
for o in O:
    if o.type!='MESH' or 'tree' not in o.name.lower(): continue
    t=o.matrix_world.translation
    if not (X0-5<=t.x<=X1+5 and Y0-5<=t.y<=Y1+5): continue
    zmin=min((o.matrix_world@Vector(c)).z for c in o.bound_box); gz=gtop(t.x,t.y)
    tr.append([o.name,round(t.x,1),round(t.y,1),round(zmin-gz,2) if gz else None])
rep['trees_near']=tr
rep['objs']=len(O)
json.dump(rep,open(f'{R}/data/wu/fix_report.json','w'),indent=1)
print('REP faces',rep['faces_prim'],rep['faces_ring'],'poke',rep['skirt_poke'][:2],'objs',rep['objs'],flush=True)
bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)

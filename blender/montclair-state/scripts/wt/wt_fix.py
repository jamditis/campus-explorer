"""wt: Tile A 2017 B17 J5D6 1 m DTM patch, Richardson west strip x40-80, y245-320 (only skirt-top cells; x40-58 RZ2 cells untouched).
Faces only where the top ground is still the 3DEP skirt (RZ2/QW/WF/Terrain keep their cells), building footprints
(plinth/glass piers/towers/G floor/MO walls) masked +0.5 m; 1-cell tuck ring 3 cm under neighbours; neighbours
RZ2/QW/WF unfeathered toward raw LiDAR within 6 m of the new faces (position-based alpha, coincident verts stay
coincident); east edge x72->80 fades to skirt; skirt GN dip copied from WO (subdivide level 0); apron + walks raised
by per-xy group delta to ground+2/3 cm (never lowered); grass points re-projected; wall feet checked."""
import bpy, bmesh, numpy as np, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R='/workspace/nj-scenes/montclair-state'
X0,X1,Y0,Y1=40,80,245,320
GX0,GY0=40,140
rep={}
g=np.load(f'{R}/data/wo/chm_grid_sw_1m.npz'); kd=[f for f in g.files if f.endswith('dtm')][0]; L=g[kd].copy()
raw=g[kd]
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
O=bpy.data.objects
sk=O['Context_skirt_3DEP_ortho_4km']; RZ=O['RZ2_SC_LiDAR_ground_patch_UNVERIFIED']; QW=O['QW_DTM_north_edge_ramp_UNVERIFIED']
WF=O['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']; TL=O['Terrain_LiDAR_DTM_1m']
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o,ev=True):
    if ev:
        e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(b,x,y):
    h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
BS=bvh(sk); BN={n:bvh(o) for n,o in (('RZ2',RZ),('QW',QW),('WF',WF),('TL',TL))}
FP=['QT_Richardson_base_plinth_UNVERIFIED','QP_Richardson_ground_storey_glass_piers_UNVERIFIED','QP_Richardson_white_corner_towers_UNVERIFIED','QU_G_floor_UNVERIFIED','MO Health Drop-In Center walls+parapet+roof (best-effort; UNVER']
BF=[bvh(O[n]) for n in FP]
def infp(x,y):
    for b in BF:
        if b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0] is not None: return True
    return False
def infp_buf(x,y,r=0.5):
    return any(infp(x+dx,y+dy) for dx,dy in ((0,0),(r,0),(-r,0),(0,r),(0,-r),(r*.7,r*.7),(-r*.7,r*.7),(r*.7,-r*.7),(-r*.7,-r*.7)))
BF_MO=BF[4:]; BF_RH=BF[:4]
def inb(bl,x,y): return any(b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0] is not None for b in bl)
def drop_face(x,y):
    """review fix: no +0.5 m buffer slit (skirt showed as dark wedges at the MO wall foot). MO (opaque CMU, foot buried):
    drop only faces fully inside. Richardson (glass ground storey): drop if centre inside and >=3 corners inside."""
    cs=[(x,y),(x+1,y),(x,y+1),(x+1,y+1)]
    if inb(BF_MO,x+0.5,y+0.5) and all(inb(BF_MO,a,b) for a,b in cs): return True
    if inb(BF_RH,x+0.5,y+0.5) and sum(inb(BF_RH,a,b) for a,b in cs)>=3: return True
    return False
def skz(x,y): return hz(BS,x,y)
def target(x,y):
    r=lv(x,y); s=skz(x,y)
    if r is None: return s
    if s is None: return r
    w=ss((x-72.0)/8.0); return r*(1-w)+s*w
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
        cx,cy=x+0.5,y+0.5
        if drop_face(x,y): continue
        z,w=nbz(cx,cy)
        if w is None: prim.add((x,y))
        else: cov[(x,y)]=w
ring=set()
for (x,y) in cov:
    if any((x+dx,y+dy) in prim for dx in (-1,0,1) for dy in (-1,0,1)): ring.add((x,y))
faces=prim|ring
rep['faces_prim']=len(prim); rep['faces_ring']=len(ring); rep['ring_by']={k:sum(1 for f in ring if cov[f]==k) for k in BN}
print('STEP faces',len(prim),len(ring),flush=True)
# --- 2. neighbour unfeather toward raw LiDAR (within 6 m of primary face centres)
kt=KDTree(len(prim))
for i,(x,y) in enumerate(prim): kt.insert(Vector((x+0.5,y+0.5,0)),i)
kt.balance()
def alpha(x,y):
    _,_,d=kt.find(Vector((x,y,0))); return 1-ss(max(0.0,d-0.71)/6.0)
for tag,o in (('rz2',RZ),('qw',QW),('wf',WF)):
    me=o.data; mw=o.matrix_world; mi=mw.inverted()
    np.save(f'{R}/data/wt/{tag}_verts_bak.npy',np.array([v.co[:] for v in me.vertices]))
    n=0;mx=0.0
    for v in me.vertices:
        c=mw@v.co
        if not (30<=c.x<=90 and 238<=c.y<=330): continue
        a=alpha(c.x,c.y)
        if a<=1e-4: continue
        t=target(c.x,c.y)
        if t is None: continue
        nz=c.z*(1-a)+t*a
        if abs(nz-c.z)>1e-4: n+=1; mx=max(mx,abs(nz-c.z))
        c.z=nz; v.co=mi@c
    me.update(); rep['unfeather_'+tag]=[n,round(mx,3)]
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
BN={n:bvh(o) for n,o in (('RZ2',RZ),('QW',QW),('WF',WF),('TL',TL))}
# --- 3. patch mesh
vk=set()
for (x,y) in faces: vk.update({(x,y),(x+1,y),(x,y+1),(x+1,y+1)})
pv={(x,y) for (x,y) in prim for (x,y) in [(x,y),(x+1,y),(x,y+1),(x+1,y+1)]}
Z={}; tuck=0
for (x,y) in vk:
    t=target(x,y)
    z,w=nbz(x,y)
    if (x,y) not in pv and z is not None:
        t=z-0.03; tuck+=1
    elif z is not None and t is not None and abs(t-z)<0.6:
        t=min(t,z-0.005) if (x,y) not in pv else t
    Z[(x,y)]=t if t is not None else 137.0
rep['tuck_verts']=tuck
bm=bmesh.new(); vid={}
for k,z in Z.items(): vid[k]=bm.verts.new((k[0],k[1],z))
for (x,y) in faces:
    f=bm.faces.new([vid[(x,y)],vid[(x+1,y)],vid[(x+1,y+1)],vid[(x,y+1)]]); f.smooth=True
me=RZ.data; mw=RZ.matrix_world; uvl=me.uv_layers['ortho']
A,U,V=[],[],[]
for li in range(0,len(me.loops),11):
    c=mw@me.vertices[me.loops[li].vertex_index].co; uv=uvl.data[li].uv; A.append([c.x,c.y,1]); U.append(uv[0]); V.append(uv[1])
A=np.array(A); cu=np.linalg.lstsq(A,np.array(U),rcond=None)[0]; cv=np.linalg.lstsq(A,np.array(V),rcond=None)[0]
rep['uv_fit_resid']=float(np.abs(A@cu-np.array(U)).max())
lay=bm.loops.layers.uv.new('ortho')
for f in bm.faces:
    for l in f.loops:
        c=l.vert.co; l[lay].uv=(cu[0]*c.x+cu[1]*c.y+cu[2],cv[0]*c.x+cv[1]*c.y+cv[2])
EN='WT_richardson_west_LiDAR_patch_UNVERIFIED'
em=bpy.data.meshes.new(EN); bm.to_mesh(em); bm.free()
em.materials.append(RZ.data.materials[0])
E=O.new(EN,em)
col=bpy.data.collections.new('WT_richardson_west_LiDAR_UNVERIFIED'); bpy.context.scene.collection.children.link(col); col.objects.link(E)
E['wt_obj']=1; E['UNVERIFIED']='wt: 2017 B17 J5D6 class-2 1 m DTM, Tile A x40-80,y245-320 (only cells not already RZ2/QW/WF/Terrain) (Richardson west) where top ground was 3DEP skirt; buildings masked (MO: faces fully inside; Richardson: centre + >=3 corners inside; no slit buffer); tuck ring 3 cm under RZ2/QW/WF; east edge fades to skirt x72-80; material = RZ2/skirt ortho lawn'
ev=[E.matrix_world@v.co for v in em.vertices]
# attributes ou_edge / ow2_strip from evaluated skirt + RZ2 + QW (inverse-distance, 4 nearest)
e=sk.evaluated_get(dg); sm=e.to_mesh()
for an in ('ou_edge','ow2_strip'):
    pts=[];vals=[]
    for o,mm in ((RZ,RZ.data),(QW,QW.data),(sk,sm)):
        a=mm.attributes.get(an)
        if not a or a.domain!='POINT': continue
        mwo=o.matrix_world
        for i,v in enumerate(mm.vertices):
            c=mwo@v.co
            if 20<c.x<120 and 220<c.y<350: pts.append(c.copy()); vals.append(a.data[i].value)
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
ina=em.attributes.new('wt_in','FLOAT','POINT')
for i,c in enumerate(ev): ina.data[i].value=1.0-ss((c.x-72.0)/8.0)*0.0
rep['patch_faces']=len(em.polygons); rep['patch_verts']=len(em.vertices); rep['zmin']=round(min(c.z for c in ev),2); rep['zmax']=round(max(c.z for c in ev),2)
# --- 4. skirt GN dip (copy WO, subdiv 0)
src=bpy.data.node_groups['WO_skirt_under_gully_head']
rep['wo_cmp']=[round(n.inputs[1].default_value,3) for n in src.nodes if n.bl_idname=='FunctionNodeCompare']
ng=src.copy(); ng.name='WT_skirt_under_richardson_west'
mp={155-20:X0-20,182+20:X1+20,292-20:Y0-20,320+20:Y1+20}
for n in ng.nodes:
    if n.bl_idname=='GeometryNodeObjectInfo': n.inputs['Object'].default_value=E
    if n.bl_idname=='GeometryNodeInputNamedAttribute' and n.inputs['Name'].default_value=='wo_in': n.inputs['Name'].default_value='wt_in'
    if n.bl_idname=='GeometryNodeSubdivideMesh': n.inputs['Level'].default_value=0
    if n.bl_idname=='FunctionNodeCompare':
        v=round(n.inputs[1].default_value,3)
        if v in mp: n.inputs[1].default_value=mp[v]
rep['wt_cmp']=[round(n.inputs[1].default_value,3) for n in ng.nodes if n.bl_idname=='FunctionNodeCompare']
rep['wt_subdiv']=[n.inputs['Level'].default_value for n in ng.nodes if n.bl_idname=='GeometryNodeSubdivideMesh']
md=sk.modifiers.new('WT_skirt_under_richardson_west','NODES'); md.node_group=ng
sk['UNVERIFIED_wt']='wt: skirt dipped (WO recipe, subdiv 0) under WT Richardson-west LiDAR patch (GN, mesh unedited)'
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
BE=bvh(E); BS2=bvh(sk)
BN={n:bvh(o) for n,o in (('RZ2',RZ),('QW',QW),('WF',WF),('TL',TL))}
def gtop(x,y):
    zs=[hz(b,x,y) for b in [BE,BS2]+list(BN.values())]; zs=[z for z in zs if z is not None]; return max(zs) if zs else None
# poke-through check
pk=0;pkmax=0.0
for (x,y) in prim:
    for fx,fy in ((0.25,0.25),(0.75,0.25),(0.25,0.75),(0.75,0.75),(0.5,0.5)):
        a=hz(BE,x+fx,y+fy); s=hz(BS2,x+fx,y+fy)
        if a is not None and s is not None and s>a-0.003: pk+=1; pkmax=max(pkmax,s-a)
rep['skirt_poke']=[pk,round(pkmax,3)]
# --- 5. apron + walks: raise per-xy group to ground + clearance (never lower)
def raise_obj(o,clr,box,tag):
    me=o.data; mw=o.matrix_world; mi=mw.inverted()
    np.save(f'{R}/data/wt/{tag}_verts_bak.npy',np.array([v.co[:] for v in me.vertices]))
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
    rep['raise_'+tag]={'groups':len(grp),'raised':n,'max_raise':round(mx,3),'dz_vs_ground_before[med,p5,min,max]':f(before),'after':f(after)}
box=(X0-0.5,X1+0.5,Y0-0.5,Y1+0.5)
raise_obj(O['QQ_Richardson_paved_apron_UNVERIFIED'],0.02,box,'apron')
for n in ('QS_footway_313027428_UNVERIFIED','QT_soil_edge_313027428_UNVERIFIED','QS_footway_313027430_UNVERIFIED','QT_soil_edge_313027430_UNVERIFIED','QS_footway_313027432_UNVERIFIED','QT_soil_edge_313027432_UNVERIFIED','QW_footway_313027428_ext_UNVERIFIED','QW_soil_edge_313027428_ext_UNVERIFIED','QS_footway_313027436_UNVERIFIED','QS_footway_313027437_UNVERIFIED','QS_footway_313027429_UNVERIFIED','QS_footway_313027435_UNVERIFIED','QT_soil_edge_313027436_UNVERIFIED','QT_soil_edge_313027437_UNVERIFIED','QT_soil_edge_313027429_UNVERIFIED','QT_soil_edge_313027435_UNVERIFIED'):
    o=O.get(n)
    if o: raise_obj(o,0.03 if ('footway' in n) else 0.015,box,n[:2]+n.split('_')[2])
# --- 6. grass points re-projected (delta new ground - old skirt) inside primary faces
for n in ('QS_Richardson_lawn_grass_points_UNVERIFIED','QV_Richardson_NW_lawn_grass_points_UNVERIFIED'):
    o=O.get(n)
    if not o: continue
    me=o.data; mw=o.matrix_world; mi=mw.inverted(); np.save(f'{R}/data/wt/{n[:2]}_grass_verts_bak.npy',np.array([v.co[:] for v in me.vertices]))
    k=0;mx=0.0
    for v in me.vertices:
        c=mw@v.co
        if (int(math.floor(c.x)),int(math.floor(c.y))) not in faces: continue
        a=hz(BE,c.x,c.y); s=skz(c.x,c.y)
        if a is None or s is None: continue
        d=a-s
        c.z+=d; v.co=mi@c; k+=1; mx=max(mx,abs(d))
    me.update(); rep['grass_'+n[:2]]=[k,round(mx,3)]
# --- 7. wall feet
wf={}
for n in FP:
    o=O[n]; mw=o.matrix_world; feet=[]
    for v in o.data.vertices:
        c=mw@v.co
        if X0-1<=c.x<=X1+1 and Y0<=c.y<=Y1:
            feet.append(c)
    if not feet: continue
    zmin=min(c.z for c in feet)
    bot=[c for c in feet if c.z<zmin+0.05]
    gaps=[]
    for c in bot:
        best=None
        for dx,dy in ((0.6,0),(-0.6,0),(0,0.6),(0,-0.6)):
            if infp(c.x+dx,c.y+dy): continue
            gz=gtop(c.x+dx,c.y+dy)
            if gz is not None: best=gz if best is None else min(best,gz)
        if best is not None: gaps.append(best-c.z)
    wf[n[:40]]={'foot_z':round(zmin,3),'n':len(bot),'ground_minus_foot[min,med,max]':[round(min(gaps),3),round(float(np.median(gaps)),3),round(max(gaps),3)] if gaps else None}
rep['wall_feet']=wf
# --- 8. trees near
tr=[]
for o in O:
    if o.type!='MESH' or 'tree' not in o.name.lower(): continue
    t=o.matrix_world.translation
    if not (50<=t.x<=88 and 240<=t.y<=328): continue
    zmin=min((o.matrix_world@Vector(c)).z for c in o.bound_box); gz=gtop(t.x,t.y)
    tr.append([o.name,round(t.x,1),round(t.y,1),round(zmin-gz,2) if gz else None])
rep['trees_near']=tr
rep['objs']=len(O)
json.dump(rep,open(f'{R}/data/wt/fix_report.json','w'),indent=1)
print('REP',json.dumps(rep)[:4000],flush=True)
bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)

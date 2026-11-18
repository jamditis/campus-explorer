"""wo: fill the 3DEP strip x155-182, y292-320 (gully head between WF/WJ/WN) with 2017 B17 J5D6 1 m DTM.
Neighbours unfeathered toward raw LiDAR at the old gap edges; new patch west edge (x=155) fades to skirt over 8 m;
shared edges snapped to the neighbours' actual verts; skirt GN dip; trees reseated by lowest point."""
import bpy, bmesh, numpy as np, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'
X0,X1,Y0,Y1=155,182,292,320
GX0,GY0=40,140
rep={}
g=np.load(f'{R}/data/wo/chm_grid_sw_1m.npz'); kd=[f for f in g.files if 'J5D6' in f and f.endswith('dtm')][0]; L=g[kd].copy()
for _ in range(30):
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
WF=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
WJ=bpy.data.objects['WJ_south_gully_LiDAR_patch_ext_UNVERIFIED']
WN=bpy.data.objects['WN_south_wood_LiDAR_patch_ext_UNVERIFIED']
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
dg=bpy.context.evaluated_depsgraph_get()
e=sk.evaluated_get(dg); me_=e.to_mesh(); BS=BVHTree.FromPolygons([sk.matrix_world@v.co for v in me_.vertices],[tuple(p.vertices) for p in me_.polygons]); e.to_mesh_clear()
def skz(x,y):
    h=BS.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return (h[0].z,h[1]) if h[0] is not None else (None,None)
def wx(x): return ss((x-X0)/8.0)
def target(x,y):
    r=lv(x,y); s,_=skz(x,y)
    if r is None: return s
    if s is None: return r
    w=wx(x); return s*(1-w)+r*w
print('STEP','# --- 1. neighbour',flush=True)
# --- 1. neighbour unfeather
def edit(obj,sel,alpha,tag):
    me=obj.data; mw=obj.matrix_world; mi=mw.inverted()
    np.save(f'{R}/data/wo/{tag}_verts_bak.npy',np.array([v.co[:] for v in me.vertices]))
    n=0; mx=0.0
    for v in me.vertices:
        c=mw@v.co
        if not sel(c.x,c.y): continue
        t=target(c.x,c.y)
        if t is None: continue
        a=alpha(c.x,c.y); nz=c.z*(1-a)+t*a
        if abs(nz-c.z)>1e-4: n+=1; mx=max(mx,abs(nz-c.z))
        w=mw@v.co; w.z=nz; v.co=mi@w
    me.update(); rep[tag]=[n,round(mx,2)]
# WN north rows (y284-292) in x155-182: replace north fade by west fade only -> alpha 1 inside 8 m of y=292
edit(WN,lambda x,y: X0-0.05<=x<=X1+0.05 and 283.9<=y<=292.05, lambda x,y: 1-ss((292-y)/8.0) if y<291.95 else 1.0,'wn')
# WJ west cols (x182-190) y292-320
edit(WJ,lambda x,y: 181.95<=x<=190.05 and 291.95<=y<=320.05, lambda x,y: 1-ss((x-182)/8.0) if x>182.05 else 1.0,'wj')
# WF south rows (y320-328) x150-190
edit(WF,lambda x,y: X0-0.05<=x<=190.05 and 319.95<=y<=328.05, lambda x,y: (1-ss((y-320)/8.0))*(1.0 if x<=182 else 1-ss((x-182)/8.0)),'wf')
bpy.context.view_layer.update()
def edgemap(obj,cond,key):
    d={}; mw=obj.matrix_world
    for v in obj.data.vertices:
        c=mw@v.co
        if cond(c): d[key(c)]=c.z
    return d
eN=edgemap(WN,lambda c: X0-0.05<=c.x<=X1+0.05 and abs(c.y-Y0)<0.06,lambda c:(int(round(c.x)),Y0))
eJ=edgemap(WJ,lambda c: abs(c.x-X1)<0.06 and Y0-0.05<=c.y<=Y1+0.05,lambda c:(X1,int(round(c.y))))
eF=edgemap(WF,lambda c: X0-0.05<=c.x<=X1+0.05 and abs(c.y-Y1)<0.06,lambda c:(int(round(c.x)),Y1))
rep['edge_n']=[len(eN),len(eJ),len(eF)]
fixed={}; fixed.update(eN); fixed.update(eJ); fixed.update(eF)
print('STEP','# --- 2. patch',flush=True)
# --- 2. patch mesh
Z={}
for y in range(Y0,Y1+1):
    for x in range(X0,X1+1):
        t=target(x,y); Z[(x,y)]=t if t is not None else 120.0
# offset ramp so edges match neighbours exactly
off={}
for k,z in fixed.items():
    if k in Z: off[k]=z-Z[k]
rep['edge_off_max']=round(max(abs(v) for v in off.values()),3) if off else None
ok=list(off.items())
for (x,y) in Z:
    if (x,y) in off: Z[(x,y)]+=off[(x,y)]; continue
    ws=0; s=0
    for (kx,ky),o in ok:
        d=math.hypot(kx-x,ky-y)
        if d<6: w=(1-d/6)**2; ws+=w; s+=w*o
    if ws>0: Z[(x,y)]+=s/ws*min(1,ws)
bm=bmesh.new(); vid={}
for (x,y),z in Z.items(): vid[(x,y)]=bm.verts.new((x,y,z))
for y in range(Y0,Y1):
    for x in range(X0,X1):
        f=bm.faces.new([vid[(x,y)],vid[(x+1,y)],vid[(x+1,y+1)],vid[(x,y+1)]]); f.smooth=True
me=WF.data; mw=WF.matrix_world; uvl=me.uv_layers.get('ortho') or me.uv_layers[0]
A,U,V=[],[],[]
for li in range(0,len(me.loops),37):
    c=mw@me.vertices[me.loops[li].vertex_index].co; uv=uvl.data[li].uv; A.append([c.x,c.y,1]); U.append(uv[0]); V.append(uv[1])
A=np.array(A); cu=np.linalg.lstsq(A,np.array(U),rcond=None)[0]; cv=np.linalg.lstsq(A,np.array(V),rcond=None)[0]
lay=bm.loops.layers.uv.new(uvl.name)
for f in bm.faces:
    for l in f.loops:
        c=l.vert.co; l[lay].uv=(cu[0]*c.x+cu[1]*c.y+cu[2],cv[0]*c.x+cv[1]*c.y+cv[2])
EN='WO_gully_head_LiDAR_patch_UNVERIFIED'
em=bpy.data.meshes.new(EN); bm.to_mesh(em); bm.free()
for m in WN.data.materials: em.materials.append(m)
E=bpy.data.objects.new(EN,em)
col=bpy.data.collections.new('WO_gully_head_LiDAR_UNVERIFIED'); bpy.context.scene.collection.children.link(col); col.objects.link(E)
E['wo_obj']=1; E['UNVERIFIED']='wo: 2017 B17 J5D6 class-2 1 m DTM over the 3DEP gap x155-182,y292-320 (head of the south ravine) between WF/WJ/WN; west edge fades to skirt over 8 m; shared edges snapped to neighbours'
ev=[E.matrix_world@v.co for v in em.vertices]
# attributes copied in kind from WN
src=WN.data
for an in ('ou_edge','wh_edge','wh_sn','wk_litter'):
    a=src.attributes.get(an)
    if not a or a.domain!='POINT': continue
    # sample nearest WN/WJ/WF value approx: use fit/nearest from WN for ou_edge, recompute others
    na=em.attributes.new(an,a.data_type,'POINT')
    for i,c in enumerate(ev):
        if an=='wh_edge': na.data[i].value=1-ss((c.x-X0)/12.0)
        elif an=='wh_sn':
            _,n=skz(c.x,c.y); na.data[i].vector=tuple(n) if n is not None else (0,0,1)
        else:
            # nearest vertex value from WN (cheap: KD)
            pass
from mathutils.kdtree import KDTree
for an in ('ou_edge','wk_litter'):
    vals=[];pts=[]
    for obj in (WN,WJ,WF):
        a=obj.data.attributes.get(an)
        if not a or a.domain!='POINT': continue
        mwo=obj.matrix_world
        for i,v in enumerate(obj.data.vertices):
            c=mwo@v.co
            if 140<c.x<200 and 280<c.y<335: pts.append(c.copy()); vals.append(a.data[i].value)
    if an in em.attributes and pts:
        kt=KDTree(len(pts))
        for i,p in enumerate(pts): kt.insert(p,i)
        kt.balance()
        for i,c in enumerate(ev):
            res=kt.find_n(Vector((c.x,c.y,c.z)),4); ws=sum(1/(d+0.3) for _,_,d in res)
            em.attributes[an].data[i].value=sum(vals[j]/(d+0.3) for _,j,d in res)/ws
rep['attrs']=[a.name for a in em.attributes if not a.name.startswith('.')]
ina=em.attributes.new('wo_in','FLOAT','POINT')
for i,c in enumerate(ev): ina.data[i].value=ss((c.x-X0)/4.0)
# lower wh_edge on neighbours now interior (union boundary lost the gap)
POLY=[(50,320),(155,320),(155,228),(245,228),(245,292),(258,292),(258,320),(300,320),(300,509),(50,509)]
def dseg(px,py,a,b):
    ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay;den=dx*dx+dy*dy
    t=0 if den<1e-12 else min(max(((px-ax)*dx+(py-ay)*dy)/den,0),1); return math.hypot(px-ax-t*dx,py-ay-t*dy)
def dpoly(x,y): return min(dseg(x,y,POLY[i],POLY[(i+1)%len(POLY)]) for i in range(len(POLY)))
nl=0
for obj in (WN,WJ,WF):
    a=obj.data.attributes.get('wh_edge')
    if not a or a.domain!='POINT': continue
    mwo=obj.matrix_world
    for i,v in enumerate(obj.data.vertices):
        c=mwo@v.co
        if 150<=c.x<=200 and 278<=c.y<=334:
            nv=min(a.data[i].value,1-ss(dpoly(c.x,c.y)/12.0))
            if nv<a.data[i].value-1e-4: nl+=1
            a.data[i].value=nv
rep['wh_edge_lowered']=nl
rep['ext_faces']=len(em.polygons); rep['zmin']=round(min(c.z for c in ev),2); rep['zmax']=round(max(c.z for c in ev),2)
print('STEP','# --- 3. skirt',flush=True)
# --- 3. skirt GN dip (copy WN's node group, retarget object + attribute)
src_ng=bpy.data.node_groups['WN_skirt_under_south_wood']
ng=src_ng.copy(); ng.name='WO_skirt_under_gully_head'
for n in ng.nodes:
    if n.bl_idname=='GeometryNodeObjectInfo': n.inputs['Object'].default_value=E
    if n.bl_idname=='GeometryNodeInputNamedAttribute': n.inputs['Name'].default_value='wo_in'
    if n.bl_idname=='GeometryNodeSubdivideMesh': n.inputs['Level'].default_value=0
    if n.bl_idname=='FunctionNodeCompare' and not n.inputs[0].is_linked is False:
        pass
# retarget box compares (EX0-20 etc.): values 135,265,208,312 in WN -> ours
mp={135.0:X0-20,265.0:X1+20,208.0:Y0-20,312.0:Y1+20}
for n in ng.nodes:
    if n.bl_idname=='FunctionNodeCompare':
        v=n.inputs[1].default_value
        if round(v,3) in mp: n.inputs[1].default_value=mp[round(v,3)]
md=sk.modifiers.new('WO_skirt_under_gully_head','NODES'); md.node_group=ng
sk['UNVERIFIED_wo']='wo: skirt dipped 2-8 cm (edge-faded) under WO gully-head LiDAR patch (GN, mesh unedited)'
bpy.context.view_layer.update()
print('STEP','# --- 4. reseat',flush=True)
# --- 4. reseat trees by lowest point
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
GB=[bvh(o) for o in (E,WN,WJ,WF)]+[bvh(sk)]
def gz(x,y):
    best=None
    for b in GB:
        h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
        if h[0] is not None and (best is None or h[0].z>best): best=h[0].z
    return best
moved=[]
for o in bpy.data.objects:
    if o.type!='MESH' or not ('tree' in o.name.lower()): continue
    t=o.matrix_world.translation
    if not (147<=t.x<=192 and 284<=t.y<=330): continue
    zmin=min((o.matrix_world@Vector(c)).z for c in o.bound_box)
    gzz=gz(t.x,t.y)
    if gzz is None: continue
    dz=(gzz-0.25)-zmin
    if abs(dz)>0.05:
        o.matrix_world.translation.z+=dz; o['wo_dz']=round(dz,3); moved.append([o.name,round(dz,2)])
rep['trees_moved']=moved
# other objects in the strip (report only)
rep['others']=[o.name for o in bpy.data.objects if o.type=='MESH' and X0<=o.matrix_world.translation.x<=X1 and Y0<=o.matrix_world.translation.y<=Y1 and o!=E][:40]
print('STEP',"rep['objs']",flush=True)
rep['objs']=len(bpy.data.objects)
json.dump(rep,open(f'{R}/data/wo/fix_report.json','w'),indent=1)
print('REP',json.dumps(rep)[:3000])
bpy.ops.wm.save_mainfile(); print('SAVED')

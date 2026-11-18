"""wa0 fix: (1) fill the WU building-mask void outside Richardson's walls (east tower corner slot) with a 0.1 m
2017-DTM-interpolated fill sheet 4 mm under WU; (2) tuck the QW ramp's floating x>=120 north strip under WV/WU
(dark crack lines in the E eye view); (3) seed QS grass points on the new bare fill. SAVE=1 to save."""
import bpy, bmesh, os, json, math, random
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R='/workspace/nj-scenes/montclair-state'; os.chdir(R)
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get(); rep={}
def bvh(names):
    V=[];P=[]
    for n in names:
        o=O[n]; e=o.evaluated_get(dg); m=e.to_mesh(); off=len(V)
        V+= [o.matrix_world@v.co for v in m.vertices]; P+=[tuple(off+i for i in p.vertices) for p in m.polygons]; e.to_mesh_clear()
    return BVHTree.FromPolygons(V,P)
WUN='WU_richardson_reid_LiDAR_patch_UNVERIFIED'; WVN='WV_stone_west_LiDAR_patch_UNVERIFIED'; QWN='QW_DTM_north_edge_ramp_UNVERIFIED'
WU=O[WUN]; B_WU=bvh([WUN]); B_WV=bvh([WVN]); B_QQ=bvh(['QQ_Richardson_paved_apron_UNVERIFIED'])
B_IN=bvh(['QU_G_floor_UNVERIFIED','QU_R_floor_UNVERIFIED','QP_Richardson_white_corner_towers_UNVERIFIED','QR_Richardson_tower_coping_lips_UNVERIFIED'])
B_TW=bvh(['QP_Richardson_white_corner_towers_UNVERIFIED','QR_Richardson_tower_coping_lips_UNVERIFIED'])
DN=Vector((0,0,-1)); UP=Vector((0,0,1))
def hz(b,x,y):
    h=b.ray_cast(Vector((x,y,400)),DN); return None if h[0] is None else h[0].z
def inside(b,x,y): return b.ray_cast(Vector((x,y,130.0)),UP)[0] is not None
# ---------- (2) QW tuck ----------
qme=O[QWN].data; qv=np.array([v.co[:] for v in qme.vertices]); np.save('data/wa0/QW_verts_pre_wa0.npy',qv)
moved=0; mx=0
for v in qme.vertices:
    x,y,z=v.co
    if x>=119.99 and 274.5<=y<=277.2:
        g=hz(B_WV,x,y)
        if g is None: g=hz(B_WU,x,y)
        if g is None: continue
        if z>g-0.01:
            mx=max(mx,z-(g-0.01)); v.co.z=g-0.01; moved+=1
qme.update(); rep['qw_tuck']=dict(moved=moved,max_drop_cm=round(mx*100,1)); print('QW',rep['qw_tuck'],flush=True)
# ---------- (1) WU fill ----------
wv=[WU.matrix_world@v.co for v in WU.data.vertices]; kd=KDTree(len(wv))
for i,c in enumerate(wv): kd.insert(c.to_2d().to_3d(),i)
kd.balance()
def idw(x,y):
    L=kd.find_range(Vector((x,y,0)),2.0)
    if len(L)<3: L=kd.find_n(Vector((x,y,0)),6)
    w=[1/max(d,0.05)**2 for _,_,d in L]; return sum(wi*wv[i].z for wi,(_,i,_) in zip(w,L))/sum(w)
S=0.1; X0,X1,Y0,Y1=80.0,120.0,247.0,320.0
nx=int(round((X1-X0)/S)); ny=int(round((Y1-Y0)/S))
cover=[]
for o in O:
    if o.type!='MESH' or o.name in (WUN,'QQ_Richardson_paved_apron_UNVERIFIED') or 'grass_points' in o.name or o.name.startswith(('Context_skirt','cx_grass','QP_Richardson','QT_Richardson','QU_','QR_Richardson')): continue
    if len(o.data.polygons)==0 and not o.modifiers: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[c.x for c in bb]; ys=[c.y for c in bb]; zs=[c.z for c in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1 or min(zs)>140: continue
    if (max(xs)-min(xs))>2000: continue
    cover.append(o.name)
print('cover objs',len(cover),flush=True); rep['cover_n']=len(cover)
B_CV=bvh(cover)
walls=[]
for o in O:
    if o.type!='MESH' or 'Richardson' not in o.name or not o.name.startswith('Q') or 'apron' in o.name: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; zs=[c.z for c in bb]
    if min(zs)<137.9<max(zs) and len(o.data.polygons)>0: walls.append(o.name)
print('walls',walls,flush=True); rep['walls']=walls
B_WL=bvh(walls)
def front_of_wall(x,y):
    if True: return False  # disabled: pier boxes give front faces from inside the glass storey (verified 276 faces up to 2.1 m inside the floor)
    best=None
    for k in range(16):
        a=k*math.pi/8; d=Vector((math.cos(a),math.sin(a),0))
        h=B_WL.ray_cast(Vector((x,y,137.9)),d,0.6)
        if h[0] is None: continue
        if best is None or h[3]<best[0]: best=(h[3],d.dot(h[1]))
    return best is not None and best[1]<0
void=set()
for j in range(ny):
    for i in range(nx):
        cx=X0+(i+.5)*S; cy=Y0+(j+.5)*S
        if hz(B_WU,cx,cy) is not None: continue
        if kd.find(Vector((cx,cy,0)))[2]>1.5: continue
        if B_CV.ray_cast(Vector((cx,cy,idw(cx,cy)+1.0)),DN,3.0)[0] is not None: continue
        corners=[(X0+(i+a)*S,Y0+(j+b)*S) for a in (0,1) for b in (0,1)]
        cin=inside(B_IN,cx,cy)
        if cin and not inside(B_TW,cx,cy):
            if not front_of_wall(cx,cy): continue
            rep.setdefault('wall_front_kept',0); rep['wall_front_kept']+=1
        elif cin:
            if all(inside(B_IN,*c) for c in corners): continue
        void.add((i,j))
print('void cells',len(void),flush=True)
def cz(i,j):
    cx=X0+(i+.5)*S; cy=Y0+(j+.5)*S; return cx,cy
keep=set(); skipped_apron=0
for (i,j) in void:
    cx,cy=cz(i,j); zf=idw(cx,cy)-0.004; za=hz(B_QQ,cx,cy)
    if za is not None and za>=zf-0.03: skipped_apron+=1; continue
    keep.add((i,j))
bare=set(keep)
# dilate 2 cells under WU
ring=set()
for (i,j) in keep:
    for di in range(-2,3):
        for dj in range(-2,3):
            k=(i+di,j+dj)
            if k in keep or k in ring or not(0<=k[0]<nx and 0<=k[1]<ny): continue
            cx,cy=cz(*k)
            if hz(B_WU,cx,cy) is not None: ring.add(k)
cells=keep|ring
print('keep',len(keep),'apron-skip',skipped_apron,'ring',len(ring),flush=True)
bm=bmesh.new(); vid={}
def vert(i,j):
    if (i,j) in vid: return vid[(i,j)]
    x=X0+i*S; y=Y0+j*S; g=hz(B_WU,x,y); z=(g if g is not None else idw(x,y))-0.004
    v=bm.verts.new((x,y,z)); vid[(i,j)]=v; return v
for (i,j) in cells:
    bm.faces.new([vert(i,j),vert(i+1,j),vert(i+1,j+1),vert(i,j+1)])
me=bpy.data.meshes.new('WA0_richardson_wall_foot_fill_UNVERIFIED'); bm.to_mesh(me); bm.free()
# uv: least-squares linear fit from WU loops
wme=WU.data; uvl=wme.uv_layers['ortho'].data
A=[];U=[]
for li,l in enumerate(wme.loops):
    c=wv[l.vertex_index]; A.append([c.x,c.y,1]); U.append(uvl[li].uv[:])
A=np.array(A);U=np.array(U); coef,res,_,_=np.linalg.lstsq(A,U,rcond=None)
resid=float(np.abs(A@coef-U).max()); rep['uv_fit_max_resid']=resid
uvn=me.uv_layers.new(name='ortho')
for li,l in enumerate(me.loops):
    c=me.vertices[l.vertex_index].co; uvn.data[li].uv=tuple(np.array([c.x,c.y,1])@coef)
for an in ('ou_edge','ow2_strip','wu_in'):
    src=wme.attributes[an]; dst=me.attributes.new(an,'FLOAT','POINT')
    for vi,v in enumerate(me.vertices):
        dst.data[vi].value=src.data[kd.find(Vector((v.co.x,v.co.y,0)))[1]].value
    if an=='ou_edge':
        for d in dst.data: d.value=0.0
me.materials.append(wme.materials[0])
for p in me.polygons: p.use_smooth=wme.polygons[0].use_smooth
ob=bpy.data.objects.new(me.name,me); WU.users_collection[0].objects.link(ob); ob['wa0_obj']=1
ob.visible_shadow=WU.visible_shadow
rep['fill']=dict(faces=len(me.polygons),verts=len(me.vertices),bare_cells=len(bare),ring=len(ring),apron_skip=skipped_apron)
xs=[X0+(i+.5)*S for i,j in bare]; ys=[Y0+(j+.5)*S for i,j in bare]
rep['fill']['bare_bbox']=[round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1)] if xs else None
print('FILL',rep['fill'],'uvres',resid,flush=True)
# ---------- (3) grass points ----------
B_F=bvh([ob.name])
qs=O['QS_Richardson_lawn_grass_points_UNVERIFIED'].data
P=np.array([v.co[:] for v in qs.vertices]); n0=len(P)
sel=P[(P[:,0]>80)&(P[:,0]<120)&(P[:,1]>247)&(P[:,1]<320)]
# local density: points per m2 in 1 m bins (nonzero median), offset above WU
bins={}
for x,y,z in sel: bins[(int(x),int(y))]=bins.get((int(x),int(y)),0)+1
dens=float(np.median(list(bins.values()))) if bins else 0
offs=[]
for x,y,z in sel[::max(1,len(sel)//400)]:
    g=hz(B_WU,x,y)
    if g is not None: offs.append(z-g)
off=float(np.median(offs)) if offs else 0.0
rng=random.Random(20261108); new=[]
for (i,j) in bare:
    lam=dens*S*S; k=int(lam)+(1 if rng.random()<lam-int(lam) else 0)
    for _ in range(k):
        x=X0+(i+rng.random())*S; y=Y0+(j+rng.random())*S; g=hz(B_F,x,y)
        if g is None: continue
        za=hz(B_QQ,x,y)
        if za is not None and za>g-0.01: continue
        new.append((x,y,g+off))
qs.vertices.add(len(new))
for k,c in enumerate(new): qs.vertices[n0+k].co=c
qs.update(); rep['grass']=dict(density_per_m2=dens,offset_m=round(off,4),added=len(new),qs_before=n0,qs_after=len(qs.vertices))
print('GRASS',rep['grass'],flush=True)
json.dump(rep,open('data/wa0/fix_report.json','w'),indent=1)
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(compress=True); print('SAVED',flush=True)

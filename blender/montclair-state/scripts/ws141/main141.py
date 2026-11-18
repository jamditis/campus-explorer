# ws141: UNIFY #48 -- BK NE-corner concrete pad (L: widening W of the Skyline W walk + apron along the BK N face),
# BK E-wall foot: graded lawn plane (2 % up to the wall), mulch drip bed + plinth skirt (fills the dark slot), shrubs;
# walk N bridge extended over the old walk (step at y -199).
import bpy, bmesh, os, math, json, random, numpy as np
from mathutils import Vector
SAVE=os.environ.get('SAVE','0')=='1'; OUT=os.environ.get('OUT','')
D='/workspace/nj-scenes/montclair-state/scripts/ws134/'
exec(open(D+'dtm_helpers.py').read())
OB=bpy.data.objects; random.seed(141)
def get(p): return [o for o in OB if o.name.startswith(p)]
for o in get('WS141_'): OB.remove(o)
wk=get('WS136a_Skyline_W_walk_N_of_-248')[0]; wm=wk.matrix_world
CON=wk.data.materials[0]; MUL=bpy.data.materials['WS3_Mulch_bark_dark_brown']
col=wk.users_collection[0]
# walk W-edge top z by y
tops=[wm@v.co for v in wk.data.vertices]
we=[p for p in tops if p.x<-72.4]
we=sorted(we,key=lambda p:p.y); wy=np.array([p.y for p in we]); 
# keep top (max z) per y station
st={}
for p in we:
    k=round(p.y,2); st[k]=max(st.get(k,-1e9),p.z)
ky=np.array(sorted(st)); kz=np.array([st[k] for k in ky])
def wtop(y): return float(np.interp(y,ky,kz))
def wtopN(y):  # N of the W-edge station range: walk top nearest the walk's W edge at that y
    c=[p for p in tops if abs(p.y-y)<0.3]
    if not c: return wtop(y)
    xm=min(p.x for p in c); return max(p.z for p in c if p.x<xm+0.1)
wxw=float(np.median([p.x for p in we]));
_mx={}
for p in tops:
    if p.y>-222: k=round(p.y,2); _mx[k]=min(_mx.get(k,1e9),p.x)
_ey=np.array(sorted(_mx)); _ex=np.array([_mx[k] for k in _ey])
_T=np.array([(p.x,p.y) for p in tops if p.y>-224])
def wedge(y):
    m=np.abs(_T[:,1]-y)<0.35
    return float(_T[m,0].min()) if m.any() else float(np.interp(y,_ey,_ex))
print('WEDGE',[(y,round(wedge(y),2)) for y in (-218,-212,-206,-205)],'walk N y',_ey.max())
print('WALK W edge x',round(wxw,3),'y',ky.min(),ky.max())
def mk(name,bm,mat,uvs=0.5):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    uvl=me.uv_layers.new(name='UVMap')
    for lp in me.loops:
        p=me.vertices[lp.vertex_index].co; uvl.data[lp.index].uv=(p.x*uvs,p.y*uvs)
    o=OB.new(name,me); col.objects.link(o); return o
# ---- BK geometry (OSM 312845862 = LiDAR-matched massing); N face (-73.2,-218.5)->(-88.3,-214.9); E face (-73.2,-218.5)->(-79.3,-243.9)
NE=np.array([-73.2,-218.5]); NW=np.array([-88.3,-214.9]); SE=np.array([-79.3,-243.9])
bk=get('WS134_Balance_Kitchen_Freeman_dining_massing')[0]; bmw=bk.matrix_world
bv=[bmw@v.co for v in bk.data.vertices]
near=[p for p in bv if -80<p.x<-72 and -245<p.y<-217]
bkmin=min(p.z for p in near) if near else None
# distance of massing verts from the OSM E-face line (sanity)
eu=(SE-NE)/np.linalg.norm(SE-NE); en=np.array([eu[1],-eu[0]])  # outward normal (points E)
if en[0]<0: en=-en
dd=[float(np.dot(np.array([p.x,p.y])-NE,en)) for p in near]
print('BK verts near E face',len(near),'min z',bkmin,'offset from OSM line min/max',round(min(dd),2) if dd else None,round(max(dd),2) if dd else None)
# use the real massing face: max outward offset of massing verts within the face span
foff=max([d for d in dd if d<1.5] or [0.0]); print('FACE offset used',round(foff,3))
def facept(t): return NE+(SE-NE)*t+en*foff
# ---- 1. concrete pad (L)  -- 2020 ortho pale L + 2023 LiDAR bright flat ground (int 9-13) x -74.6..-72.9 y -205..-214, band along N face to x -78.5
nu=(NW-NE)/np.linalg.norm(NW-NE); nn=np.array([-nu[1],nu[0]])
if nn[1]<0: nn=-nn   # outward (N)
def nface(x):  # y of N face at x
    t=(x-NE[0])/(NW[0]-NE[0]); return NE[1]+(NW[1]-NE[1])*t
XW=-74.6; XL=-78.5; WE=wxw+0.04  # tuck 4 cm under the walk edge
poly=[(WE,-205.0),(XW,-205.0),(XW,nface(XW)+2.26),(XL,nface(XL)+2.26),(XL,nface(XL)-0.05),(NE[0]+0.0,NE[1]-0.12),(WE,NE[1]-0.12)]
# z: walk-edge top at the joint, LiDAR/DTM plane elsewhere (smoothed), +0.07 finished
def zpad(x,y):
    zw=wtop(min(max(y,ky.min()),ky.max())) if y<ky.max() else wtopN(y)
    # dtm average 1.5 m
    zd=np.mean([dtm(x+a,y+b) for a in (-0.75,0,0.75) for b in (-0.75,0,0.75)])+0.07
    t=min(max((wedge(y)-x)/1.6,0),1); t=t*t*(3-2*t)
    return zw*(1-t)+zd*t
bm=bmesh.new()
def grid(x0,x1,ylo,yhi,nu,nv):
    G={}
    for i in range(nu+1):
        x=x0+(x1-x0)*i/nu
        for j in range(nv+1):
            y=ylo(x)+(yhi(x)-ylo(x))*j/nv; G[i,j]=bm.verts.new((x,y,zpad(x,y)))
    for i in range(nu):
        for j in range(nv): bm.faces.new((G[i,j],G[i+1,j],G[i+1,j+1],G[i,j+1]))
GA={}
yA=np.linspace(nface(-73.0)-0.12,-205.0,28)
for j,y in enumerate(yA):
    xe=wedge(y)+0.04
    for i in range(5):
        x=XW+(xe-XW)*i/4; GA[i,j]=bm.verts.new((x,y,zpad(x,y)))
for i in range(4):
    for j in range(len(yA)-1): bm.faces.new((GA[i,j],GA[i+1,j],GA[i+1,j+1],GA[i,j+1]))
grid(XL,XW,lambda x:nface(x)-0.05,lambda x:nface(x)+2.26,8,5)  # apron along the BK N face
# clip-free boundary skirt 0.25 m
bnd=[e for e in bm.edges if e.is_boundary]
for e in bnd:
    a,b=e.verts; a2=bm.verts.new(a.co-Vector((0,0,0.25))); b2=bm.verts.new(b.co-Vector((0,0,0.25))); bm.faces.new((a,b,b2,a2))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if abs(f.normal.z)>0.5 and f.normal.z<0: f.normal_flip()
pad=mk('WS141_BK_NE_concrete_pad_L_ortho2020_LiDAR2023int_UNVERIFIEDjoints',bm,CON,0.5)
print('PAD faces',len(pad.data.polygons))
# sawcut joints: offset by panels via UV scale 0.5 -> 2 m panels (same as walk)
# ---- 2. E-wall foot strip: lawn plane rising 2 % from the walk edge to the wall
Y0,Y1=-243.4,-218.9
def zlawn(x,y):
    zw=wtop(min(max(y,ky.min()),ky.max()))-0.03
    return zw+0.02*max(0.0,wxw-x)
def inBK(x,y): return pip(OSMBK,x,y)
OSMBK=[(a,b) for a,b in json.load(open(D+'osm134.json'))['312845862'][:-1]]
tot={}
for o in OB:
    if o.type!='MESH' or not o.name.startswith(('Terrain','WS114','WS134_ground','WS133b_ground','WS110_ground')): continue
    mw_=o.matrix_world; mi=mw_.inverted(); n=0
    for v in o.data.vertices:
        p=mw_@v.co
        if not (-81<p.x<wxw-0.08 and Y0<p.y<Y1): continue
        d=float(np.dot(np.array([p.x,p.y])-NE,en))
        if d<foff-0.3: continue  # under the building
        z=zlawn(p.x,p.y)
        if abs(p.z-z)>1.5: continue
        p.z=z; v.co=mi@p; n+=1
    # under the pad: keep ground 8 cm below the pad top
    for v in o.data.vertices:
        p=mw_@v.co
        if XL-0.2<p.x<WE and nface(p.x)-0.3<p.y<-204.8 and pip(poly,p.x,p.y):
            zt=zpad(p.x,p.y)-0.08
            if p.z>zt: p.z=zt; v.co=mi@p; n+=1
    if n: o.data.update(); tot[o.name[:40]]=n
print('GRADE',tot)
# ---- 3. mulch drip bed 1.0 m wide along the E face + plinth skirt (hides the slot under the massing)
bm=bmesh.new(); T=np.linspace(0.0,1.0,51); rows=[]
for t in T:
    f=facept(t); r=[]
    Wt=max(0.25,min(2.0,(wxw-0.06-f[0])/en[0]))
    for w in (-0.05,0.5*Wt,Wt):
        x,y=f+en*w; r.append(bm.verts.new((x,y,zlawn(x,y)+0.05)))
    rows.append(r)
for i in range(len(rows)-1):
    for j in range(2): bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
# outer edge: low steel-edge lip 4 cm; wall side: skirt down 0.9 m
for i in range(len(rows)-1):
    a,b=rows[i][2],rows[i+1][2]; a2=bm.verts.new(a.co-Vector((0,0,0.12))); b2=bm.verts.new(b.co-Vector((0,0,0.12))); bm.faces.new((a,b,b2,a2))
    a,b=rows[i][0],rows[i+1][0]; a2=bm.verts.new(a.co-Vector((0,0,0.9))); b2=bm.verts.new(b.co-Vector((0,0,0.9))); bm.faces.new((a,b,b2,a2))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if abs(f.normal.z)>0.5 and f.normal.z<0: f.normal_flip()
mk('WS141_BK_E_wall_shrub_bed_mulch_ortho2020_LiDARnoground_UNVERIFIEDplanting',bm,MUL,0.5)
# plinth: concrete band on the face from bed top -0.3 up to max(bed top +0.25, massing bottom +0.1)
bm=bmesh.new(); pr=[]
for t in T:
    f=facept(t)+en*0.012; zb=zlawn(*f)+0.05
    ztop=max(zb+0.25,(bkmin+0.1) if bkmin is not None else zb+0.25)
    pr.append((bm.verts.new((f[0],f[1],zb-0.3)),bm.verts.new((f[0],f[1],ztop))))
for i in range(len(pr)-1): bm.faces.new((pr[i][0],pr[i+1][0],pr[i+1][1],pr[i][1]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
mk('WS141_BK_E_wall_foundation_plinth_concrete_UNVERIFIED',bm,CON,0.5)
# ---- 4. shrubs in the bed (ortho: dark crowns along the wall y -228..-243); reuse WS138a bed shrubs (linked data)
src=[o for o in OB if o.name.startswith('WS138a_bed_shrub_')][:6]
ns=0
for t in np.linspace(0.30,0.80,9):
    if not src: break
    t2=t+random.uniform(-0.03,0.03); Wt=max(0.25,min(2.0,(wxw-0.06-facept(t2)[0])/en[0])); f=facept(t2)+en*Wt*random.uniform(0.35,0.6)
    s=random.choice(src); o=s.copy(); o.name='WS141_BK_E_bed_shrub_'+s.name.split('.')[0][-12:]
    o.location=Vector((f[0],f[1],zlawn(*f)+0.04)); o.rotation_euler.z=random.uniform(0,6.28)
    k=random.uniform(0.85,1.15); o.scale=s.scale*k
    col.objects.link(o); ns+=1
print('SHRUBS',ns,[s.name for s in src][:3])
# ---- 5. walk N bridge: extend over the old walk to y -197.4, matched to the old-walk surface
fp=OB.get('Footpaths_OSM'); b=get('WS139_walk_N_bridge')
if fp and b:
    b=b[0]; fmi=fp.matrix_world.inverted()
    def oldz(x,y):
        o=fmi@Vector((x,y,200)); d=(fmi.to_3x3()@Vector((0,0,-1))).normalized()
        h=fp.ray_cast(o,d)
        return (fp.matrix_world@h[1]).z if h[0] else None
    zo=[oldz(-71.0,y) for y in (-198.9,-198.4,-197.9,-197.4)]
    bz=max(v.co.z for v in b.data.vertices if v.co.y>-199.0)
    print('BRIDGE oldz',zo,'bridge N z',round(bz,3))
    xw=min(v.co.x for v in b.data.vertices); xe=max(v.co.x for v in b.data.vertices)
    if all(z is not None for z in zo):
        zS=max(v.co.z for v in b.data.vertices if v.co.y<-203.0)
        zN=zo[-1]+0.012
        bm=bmesh.new(); ys=np.linspace(-203.1,-197.4,12); xs_=np.linspace(xw,xe,5); V={}
        def zf(y): t=(y+203.1)/5.7; t=t*t*(3-2*t); return zS+(zN-zS)*t
        for i,y in enumerate(ys):
            for j,x in enumerate(xs_):
                z=zf(y); oz=oldz(x,y) if y>-199.2 else None
                if oz is not None: z=max(z,oz+0.012)
                V[i,j]=bm.verts.new((x,y,z))
        for i in range(len(ys)-1):
            for j in range(4): bm.faces.new((V[i,j],V[i,j+1],V[i+1,j+1],V[i+1,j]))
        for j_ in (0,4):
            for i in range(len(ys)-1):
                a=V[i,j_];c=V[i+1,j_]; a2=bm.verts.new(a.co-Vector((0,0,0.12))); c2=bm.verts.new(c.co-Vector((0,0,0.12))); bm.faces.new((a,c,c2,a2))
        # N lip: feathered 2 cm nosing into the old walk
        bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
        for f in bm.faces:
            if abs(f.normal.z)>0.5 and f.normal.z<0: f.normal_flip()
        bm.to_mesh(b.data); bm.free(); b.data.update()
        uvl=b.data.uv_layers[0] if b.data.uv_layers else b.data.uv_layers.new(name='UVMap')
        for lp in b.data.loops:
            p=b.data.vertices[lp.vertex_index].co; uvl.data[lp.index].uv=(p.x*0.25,p.y*0.25)
        print('BRIDGE rebuilt to -197.4 zS',round(zS,3),'zN',round(zN,3))
if SAVE:
    if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED',OUT)

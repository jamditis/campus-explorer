# ws163: UNIFY #67 part — Normal Ave W extension (x -270 -> -346) + Lot 3 aisle S drive (OSM 232846667, y -235 -> Normal Ave)
# Run on a main that already has WS162_ (ws162c/ws162d). Idempotent for WS163_ objects (ground push / retire is not undone; run once per base).
# Evidence (prep/ws163_lot3S/REFS.md): 2023 NJ LiDAR class-2 intensity + DTM (las163.npy, dtm163.npy 0.5 m x -350..-270, y -290..-140),
# NJOGIS 2020 ortho (ortho_S_grid.png), OSM aisle 232846667 + Normal Ave ws81 centreline (W end -268.8,-268.5).
import bpy, bmesh, os, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import tessellate_polygon
OUT=os.environ.get('OUT',''); OB=bpy.data.objects
P='/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/'
D=np.load(P+'dtm163.npy')[0].copy(); X0,Y0,R=-350.0,-290.0,0.5
nan=np.isnan(D)
if nan.any():
    from collections import deque
    jj,ii=np.nonzero(~nan)
    for j,i in zip(*np.nonzero(nan)):
        for rr in range(1,12):
            sub=D[max(j-rr,0):j+rr+1,max(i-rr,0):i+rr+1]
            if np.isfinite(sub).any(): D[j,i]=float(np.nanmedian(sub)); break
def dz(x,y):
    fi=(x-X0)/R-0.5; fj=(y-Y0)/R-0.5
    i=int(min(max(math.floor(fi),0),D.shape[1]-2)); j=int(min(max(math.floor(fj),0),D.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(D[j,i]*(1-tx)*(1-ty)+D[j,i+1]*tx*(1-ty)+D[j+1,i]*(1-tx)*ty+D[j+1,i+1]*tx*ty)
for o in [o for o in OB if o.name.startswith('WS163_')]: OB.remove(o)
col=bpy.data.collections.get('WS163_NormalAve_W_LotS') or bpy.data.collections.new('WS163_NormalAve_W_LotS')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
def getmat(n,rgb,rough=0.85):
    m=bpy.data.materials.get(n)
    if m: return m
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=rough; return m
asm=getmat('WS27_CollegeAve_asphalt_2020ortho',(0.08,0.08,0.085)); cm=getmat('WS27_curb_concrete_UNVERIFIED',(0.55,0.54,0.51))
wk=bpy.data.materials.get('SC_walk_concrete_joints_UNVERIFIED') or getmat('WS162_walk_concrete_UNVERIFIED',(0.36,0.35,0.33),0.92)
def mkobj(name,bm,mat,uvs=0.25):
    for f in bm.faces:
        f.normal_update()
        if f.normal.z<0: f.normal_flip()
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    uv=me.uv_layers.new(name='UVMap')
    for lp in me.loops:
        p=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(p.x*uvs,p.y*uvs)
    o=OB.new(name,me); col.objects.link(o); return o
# ---- road frame: N curb line from the LiDAR intensity edge (x -340:-246.5, -320:-251.5, -285:-259.5) == WS110/ws84 N edge at x -268.8 (y -262.9); slope 0.236
SL=0.236; dv=np.array([-1.0,SL]); dv/=np.linalg.norm(dv); nv=np.array([SL,1.0]); nv/=np.linalg.norm(nv)   # dv points W, nv points N
A0=np.array([-268.8,-262.9])   # N edge point at the WS110 W end
WROAD=11.3; XE,XW=-269.6,-346.0   # 0.8 m overlap under the WS110 end
def npt(x):  # N edge point at x
    t=(A0[0]-x)/(-dv[0]); return A0+dv*t
MOUTH=(-315.2,-305.6)   # aisle mouth x-range on the N curb (LiDAR dark column x -313..-306 + flares)
# ---- 1. carriageway: longitudinal profile = median LiDAR ground across the road at each 1 m station, smoothed over 7 m;
#      2 % crown (5.65 m half-width -> edges 11 cm below the crown) — clean CAD section instead of DTM noise (0.5 m cells smear the 15 cm curb)
XS=np.arange(XE,XW-0.01,-1.0)
cz=np.array([np.median([dz(*(npt(x)-nv*s_)) for s_ in np.linspace(1.5,WROAD-1.5,7)]) for x in XS])
k=7; czs=np.convolve(np.pad(cz,(k//2,k//2),mode='edge'),np.ones(k)/k,mode='valid')+0.02
def cz_at(x): return float(np.interp(-x,-XS,czs))
def sec(x,s_):   # s_ = distance from the N edge (0..WROAD)
    return cz_at(x)-0.02*abs(s_-WROAD/2)
bm=bmesh.new(); rows=[]
for x in XS:
    p=npt(x); r=[]
    for s_ in (0,1.9,3.8,5.65,7.5,9.4,WROAD):
        q=p-nv*s_; r.append(bm.verts.new((q[0],q[1],sec(x,s_))))
    rows.append(r)
for i in range(len(rows)-1):
    for j in range(6): bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
road=mkobj('WS163_NormalAve_W_carriageway_LiDAR2023_int_edges_W11p3_UNVERIFIED',bm,asm)
REV=0.15; DREV=0.03
def ztop_curb(x,side):
    ze=sec(x,0 if side>0 else WROAD)
    if side>0:
        if MOUTH[0]<=x<=MOUTH[1]: return ze+DREV
        f=min(abs(x-MOUTH[0]),abs(x-MOUTH[1]))
        if f<1.5 and not (MOUTH[0]<=x<=MOUTH[1]): return ze+DREV+(REV-DREV)*f/1.5
    return ze+REV
# ---- 2. curbs: top at walk height (DTM+4 cm behind the curb line), face down to the gutter; depressed (3 cm) across the aisle mouth
def curb(name,side):
    bm=bmesh.new(); rings=[]
    for x in np.arange(XE,XW-0.01,-0.5):
        p=npt(x) if side>0 else npt(x)-nv*WROAD; o=nv*side
        a=p; b=p+o*0.18; zr=sec(x,0 if side>0 else WROAD); zt=ztop_curb(x,side)
        zb=zr-0.30
        rings.append([bm.verts.new((a[0],a[1],zb)),bm.verts.new((a[0],a[1],zt)),bm.verts.new((b[0],b[1],zt)),bm.verts.new((b[0],b[1],zb))])
    for i in range(len(rings)-1):
        for j in range(3): bm.faces.new((rings[i][j],rings[i+1][j],rings[i+1][j+1],rings[i][j+1]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(cm); o=OB.new(name,me); col.objects.link(o); return o
curb('WS163_NormalAve_W_N_curb_depressed_at_Lot3_aisle_UNVERIFIEDsection',1)
curb('WS163_NormalAve_W_S_curb_UNVERIFIEDsection',-1)
# ---- 3. N sidewalk: bright 3-4 m LiDAR band behind the N curb (x -340: y -246..-242; -320: -251..-248) -> 3.2 m concrete walk, continuous across the drive (apron)
def walk(name,side,w):
    bm=bmesh.new(); rows=[]
    for x in np.arange(XE,XW-0.01,-0.75):
        p=(npt(x) if side>0 else npt(x)-nv*WROAD)+nv*side*0.18; r=[]
        for s in np.linspace(0,w,4):
            q=p+nv*side*s; z=ztop_curb(x,side)+0.02*s   # 2 % cross-slope up from the curb top
            r.append(bm.verts.new((q[0],q[1],z)))
        rows.append(r)
    for i in range(len(rows)-1):
        for j in range(3): bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
    return mkobj(name,bm,wk,0.4)
walk('WS163_NormalAve_W_N_sidewalk_3p2m_LiDAR2023_int_UNVERIFIED',1,3.2)
walk('WS163_NormalAve_W_S_sidewalk_1p6m_UNVERIFIED',-1,1.6)
# ---- 4. Lot 3 aisle S drive: OSM 232846667 continues from the Lot 3 S end to Normal Ave; ortho 2020 + LiDAR dark column x -313..-306;
#      starts under the WS162 S feather (y -234/-236) and stops at the N sidewalk back edge
def wb(x): return (npt(x)+nv*(0.18+3.2))[1]
DW=[(-311.2,-234.6),(-312.6,-240.0),(-313.6,-245.0),(-315.2,wb(-315.2))]
DE=[(-305.6,wb(-305.6)),(-306.0,-245.0),(-305.0,-240.0),(-303.0,-235.2)]
POLY=DW+DE+[(-306.0,-234.2)]
tris=tessellate_polygon([[Vector((x,y,0)) for x,y in POLY]])
bm=bmesh.new(); vs=[bm.verts.new((x,y,0)) for x,y in POLY]
for t in tris:
    try: bm.faces.new([vs[i] for i in t])
    except ValueError: pass
for _ in range(8):
    long=[e for e in bm.edges if e.calc_length()>1.2]
    if not long: break
    bmesh.ops.subdivide_edges(bm,edges=long,cuts=1,use_grid_fill=True); bmesh.ops.triangulate(bm,faces=list(bm.faces))
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.01)
def wz(x): return ztop_curb(x,1)+0.02*3.2
for v in bm.verts:
    x,y=v.co.x,v.co.y; z0=dz(x,y)+0.045; d_=y-wb(x)
    v.co.z=z0 if d_>3.0 else wz(x)+(z0-wz(x))*max(d_,0)/3.0   # ramp from the walk back edge over 3 m
drive=mkobj('WS163_Lot3_aisle_S_drive_to_NormalAve_OSM232846667_LiDAR2023_UNVERIFIEDedges',bm,asm)
print('ROAD faces',len(road.data.polygons),'DRIVE faces',len(drive.data.polygons))
# ---- 5. retire OSM drape faces and push ground sheets 10 cm under the new surfaces
NEW=[o for o in col.objects if o.type=='MESH']
V=[];F=[]
for o in NEW:
    b=len(V); V+= [o.matrix_world@v.co for v in o.data.vertices]; F+= [[b+i for i in p.vertices] for p in o.data.polygons]
T=BVHTree.FromPolygons(V,F)
def ztop(x,y):
    h=T.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
BX=(-347,-268,-276,-232)
for ro in [o for o in OB if o.type=='MESH' and (o.name in ('Roads_OSM','Footpaths_OSM') or o.name.startswith('UA_'))]:
    rb=bmesh.new(); rb.from_mesh(ro.data); rw=ro.matrix_world; k=[]
    for f in rb.faces:
        c=rw@f.calc_center_median()
        if BX[0]<c.x<-270.5 and BX[2]<c.y<BX[3]:
            zt=ztop(c.x,c.y)
            if zt is not None and abs(c.z-zt)<1.5: k.append(f)
    if k: bmesh.ops.delete(rb,geom=k,context='FACES'); rb.to_mesh(ro.data); ro.data.update(); print('retired',ro.name,len(k))
    rb.free()
nd=0
for g in [o for o in OB if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS114_terrain_fan_fill','WS110_ground_patch','WS110_NormalAve_verge','WS133b_','WS134_ground','WS60_terrain_edge_apron','WS68_RHD_ground','Terrain_far','Skirt','WS112','WS162_Lot3_S_end_apron'))]:
    me=g.data; mw=np.array(g.matrix_world); n=len(me.vertices)
    co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); Wc=co@mw[:3,:3].T+mw[:3,3]
    idx=np.nonzero((Wc[:,0]>BX[0])&(Wc[:,0]<BX[1])&(Wc[:,1]>BX[2])&(Wc[:,1]<BX[3]))[0]; c=0
    for i in idx:
        x,y,z=Wc[i]; best=None
        for ddx,ddy in ((0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3)):
            zt=ztop(x+ddx,y+ddy)
            if zt is not None: best=zt if best is None else min(best,zt)
        if best is not None and z>best-0.06: Wc[i,2]=best-0.06; c+=1
    if c:
        L=(Wc-mw[:3,3])@np.linalg.inv(mw[:3,:3]).T; me.vertices.foreach_set('co',L.ravel()); me.update(); print('pushed',g.name,c); nd+=c
print('ground pushed',nd)
px=OB.get('WS113_paving_tops_proxy')
if px:
    pbm=bmesh.new(); pbm.from_mesh(px.data); pmi=px.matrix_world.inverted(); n0=len(pbm.faces)
    for o in NEW:
        for p in o.data.polygons: pbm.faces.new([pbm.verts.new(pmi@(o.matrix_world@o.data.vertices[i].co)) for i in p.vertices])
    pbm.to_mesh(px.data); pbm.free(); print('proxy',n0,'->',len(px.data.polygons))
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED',OUT)

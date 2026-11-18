# ws162: UNIFY #66 Panzer W side — Lot 3 (OSM 312847995, amenity=parking) + aisle, never modelled (W of Panzer was far-field lawn skirt).
# Evidence (prep/ws162_lot3/): NJOGIS 2020 ortho (ortho_lot3_grid.png / ortho_lot3N_grid.png) + 2023 LiDAR class-2 intensity (lot3_lidar_int_grid.png,
# las162.npy) + class-2 DTM (scripts/ws162/dtm162.npy, 0.5 m, x -330..-270, y -250..-165).
#  - asphalt (dark in LiDAR intensity) from a bright concrete band on the W (x -307 at y -233 .. -297 at y -176) to Panzer's W wall (LiDAR class-6 edge);
#  - 90-degree stalls against the wall (ortho: white ticks x -296..-290, y -209..-232, pitch ~2.7 m) — positions by eye, UNVERIFIED;
#  - concrete curb along the W edge (the bright intensity band; section UNVERIFIED); N end meets the W door landing at y -171.5.
# Idempotent: removes WS162_ objects first. OUT env var -> save copy.
import bpy, bmesh, os, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import tessellate_polygon
OUT=os.environ.get('OUT',''); OB=bpy.data.objects
W='/workspace/nj-scenes/montclair-state/scripts/ws162/'
ZS=np.load(W+'dtm162.npy')[1]; X0,Y1,R=-330.0,-165.0,0.5
def dz(x,y):
    fi=(x-X0)/R; fj=(Y1-y)/R
    i=int(min(max(math.floor(fi),0),ZS.shape[1]-2)); j=int(min(max(math.floor(fj),0),ZS.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(ZS[j,i]*(1-tx)*(1-ty)+ZS[j,i+1]*tx*(1-ty)+ZS[j+1,i]*(1-tx)*ty+ZS[j+1,i+1]*tx*ty)
def lz(x,y): return dz(x,y)+0.04
for o in [o for o in OB if o.name.startswith('WS162_')]: OB.remove(o)
col=bpy.data.collections.get('WS162_Lot3_W_side') or bpy.data.collections.new('WS162_Lot3_W_side')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
def getmat(n,rgb,rough=0.85):
    m=bpy.data.materials.get(n)
    if m: return m
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=rough; return m
asm=getmat('WS27_CollegeAve_asphalt_2020ortho',(0.08,0.08,0.085)); cm=getmat('WS27_curb_concrete_UNVERIFIED',(0.55,0.54,0.51))
pm=getmat('WS162_paint_white_stall_lines',(0.85,0.85,0.82),0.55)
# outline (scene xy), W edge S->N then N edge, E edge (Panzer W wall + 0.3 m under the wall) N->S, S edge
WEDGE=[(-307.2,-234.0),(-306.4,-231.5),(-303.2,-215.0),(-301.4,-205.0),(-300.2,-199.0),(-298.6,-190.0),(-297.4,-182.0),(-296.6,-176.0),(-296.4,-171.5)]
EEDGE=[(-285.6,-171.5),(-288.0,-182.0),(-288.3,-190.0),(-289.4,-205.0),(-289.7,-207.0),(-291.2,-235.0),(-291.2,-236.0)]
POLY=WEDGE+EEDGE
def wallx(y):
    pts=[(p[1],p[0]) for p in EEDGE[:-1]][::-1]
    for k in range(len(pts)-1):
        if pts[k][0]<=y<=pts[k+1][0]:
            t=(y-pts[k][0])/(pts[k+1][0]-pts[k][0]); return pts[k][1]+(pts[k+1][1]-pts[k][1])*t
    return pts[0][1] if y<pts[0][0] else pts[-1][1]
# ---- 1. asphalt: tessellate, refine to ~1 m, drape on LiDAR DTM + 4 cm
tris=tessellate_polygon([[Vector((x,y,0)) for x,y in POLY]])
bm=bmesh.new(); vs=[bm.verts.new((x,y,0)) for x,y in POLY]
for t in tris: bm.faces.new([vs[i] for i in t])
for _ in range(9):
    long=[e for e in bm.edges if e.calc_length()>1.3]
    if not long: break
    bmesh.ops.subdivide_edges(bm,edges=long,cuts=1,use_grid_fill=True)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.01)
for v in bm.verts: v.co.z=lz(v.co.x,v.co.y)
for f in bm.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS162_Lot3_asphalt_OSM312847995_LiDAR2023int_ortho2020_UNVERIFIEDedges'); bm.to_mesh(me); bm.free(); me.materials.append(asm)
uv=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    p=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(p.x*0.25,p.y*0.25)
lot=OB.new(me.name,me); col.objects.link(lot); print('LOT verts',len(me.vertices),'faces',len(me.polygons))
# ---- 2. W curb (concrete band in the LiDAR intensity), 0.15 m wide, 12 cm reveal
def curbmesh(name,LS,sgn,rev,mat,w=0.18,step=0.5):
    bm=bmesh.new(); pts=[]
    for k in range(len(LS)-1):
        a=np.array(LS[k],float); b=np.array(LS[k+1],float); L=np.linalg.norm(b-a); n=max(1,int(math.ceil(L/step)))
        for s in range(n): pts.append(a+(b-a)*s/n)
    pts.append(np.array(LS[-1],float)); rings=[]
    for k,p in enumerate(pts):
        q=pts[min(k+1,len(pts)-1)]-pts[max(k-1,0)]; d=q/np.linalg.norm(q); n=np.array([d[1],-d[0]])*sgn
        z=lz(p[0],p[1]); a=p; b=a+n*w; zb=z-0.30
        rings.append([bm.verts.new((a[0],a[1],zb)),bm.verts.new((a[0],a[1],z+rev)),bm.verts.new((b[0],b[1],z+rev)),bm.verts.new((b[0],b[1],zb))])
    for i in range(len(rings)-1):
        for j in range(3): bm.faces.new((rings[i][j],rings[i+1][j],rings[i+1][j+1],rings[i][j+1]))
        bm.faces.new((rings[i][3],rings[i+1][3],rings[i+1][0],rings[i][0]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    m=bpy.data.meshes.new(name); bm.to_mesh(m); bm.free(); m.materials.append(mat); o=OB.new(name,m); col.objects.link(o); return o
curbmesh('WS162_Lot3_W_curb_LiDAR2023_concrete_band_UNVERIFIEDsection',WEDGE[:-1],-1,0.12,cm)
# ---- 2b. W walk: the bright 3-5 m concrete band W of the lot in the LiDAR intensity (x -314..-307 at y -235..-200) = sidewalk/gutter (UNVERIFIED material/width)
def walkmesh(name,LS,w0,w1,mat,lift=0.03,step=0.75):
    bm=bmesh.new(); pts=[]
    for k in range(len(LS)-1):
        a=np.array(LS[k],float); b=np.array(LS[k+1],float); L=np.linalg.norm(b-a); n=max(1,int(math.ceil(L/step)))
        for s_ in range(n): pts.append(a+(b-a)*s_/n)
    pts.append(np.array(LS[-1],float)); rows=[]
    for k,p in enumerate(pts):
        q=pts[min(k+1,len(pts)-1)]-pts[max(k-1,0)]; d=q/np.linalg.norm(q); n=np.array([-d[1],d[0]])   # points W
        r=[]
        for t in np.linspace(w0,w1,4):
            x,y=p+n*t; r.append(bm.verts.new((x,y,lz(x,y)-0.04+lift)))
        rows.append(r)
    for i in range(len(rows)-1):
        for j in range(len(rows[i])-1): bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
    for f in bm.faces:
        f.normal_update()
        if f.normal.z<0: f.normal_flip()
    m=bpy.data.meshes.new(name); bm.to_mesh(m); bm.free(); m.materials.append(mat)
    uvl=m.uv_layers.new(name='UVMap')
    for lp in m.loops:
        p=m.vertices[lp.vertex_index].co; uvl.data[lp.index].uv=(p.x*0.4,p.y*0.4)
    o=OB.new(name,m); col.objects.link(o); return o
walkc=getmat('WS162_walk_concrete_UNVERIFIED',(0.36,0.35,0.33),0.92)
walkmesh('WS162_Lot3_W_walk_band_LiDAR2023_intensity_UNVERIFIED',[WEDGE[0],WEDGE[1],WEDGE[2],WEDGE[3],WEDGE[4]],0.18,4.2,walkc)
# ---- 2d. W shoulder: the evaluated far-field skirt lies below the LiDAR ground here -> graded lawn bank from the walk's outer edge down onto the skirt (ray-cast)
dg=bpy.context.evaluated_depsgraph_get(); skirt=OB.get('Context_skirt_3DEP_ortho_4km')
sk=None
if skirt:
    se=skirt.evaluated_get(dg); sme=se.to_mesh(); smw=skirt.matrix_world
    sk=BVHTree.FromPolygons([smw@v.co for v in sme.vertices],[p.vertices for p in sme.polygons])
def skz(x,y):
    if sk is None: return None
    h=sk.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
LS=[WEDGE[0],WEDGE[1],WEDGE[2],WEDGE[3],WEDGE[4]]; pts=[]
for k in range(len(LS)-1):
    a=np.array(LS[k],float); b=np.array(LS[k+1],float); n=max(1,int(math.ceil(np.linalg.norm(b-a)/0.75)))
    for s_ in range(n): pts.append(a+(b-a)*s_/n)
pts.append(np.array(LS[-1],float)); sb=bmesh.new(); rows=[]; nz=0
for k,p in enumerate(pts):
    q=pts[min(k+1,len(pts)-1)]-pts[max(k-1,0)]; d=q/np.linalg.norm(q); n=np.array([-d[1],d[0]]); r=[]
    x,y=p+n*4.2; ze=lz(x,y)-0.04+0.03; r.append(sb.verts.new((x,y,ze)))
    for t,fr in ((6.0,0.5),(9.0,1.0)):
        x,y=p+n*(4.2+t); zs=skz(x,y); z2=(min(zs,ze)-0.02) if zs is not None else dz(x,y)-0.3
        if zs is not None and zs>ze: nz+=1
        r.append(sb.verts.new((x,y,z2)))
    rows.append(r)
for i in range(len(rows)-1):
    for j in range(len(rows[i])-1): sb.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
for f in sb.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
shm=bpy.data.meshes.new('WS162_Lot3_W_shoulder_lawn_bank_to_skirt_UNVERIFIED'); sb.to_mesh(shm); sb.free()
lm=bpy.data.materials.get('COLE_lawn_post2020_bs') or getmat('WS162_lawn',(0.12,0.2,0.07),0.95); shm.materials.append(lm)
uvs=shm.uv_layers.new(name='UVMap')
for lp in shm.loops:
    pp=shm.vertices[lp.vertex_index].co; uvs.data[lp.index].uv=(pp.x*0.25,pp.y*0.25)
col.objects.link(OB.new(shm.name,shm)); print('SHOULDER rows',len(rows),'skirt higher than edge at',nz)
# ---- 2c. S-end apron: Lot 3 / the aisle continue S (OSM 232846667 to y -258) but that stretch is not modelled yet -> feather the S edge into the ground over 3 m
ab=bmesh.new(); xs_=np.linspace(WEDGE[0][0],EEDGE[-1][0],18); r0=[];r1=[]; r2=[]
for x in xs_:
    t=(x-WEDGE[0][0])/(EEDGE[-1][0]-WEDGE[0][0]); y=-234.0+(-236.0+234.0)*t
    r0.append(ab.verts.new((x,y,lz(x,y)))); y1=y-1.5; r1.append(ab.verts.new((x,y1,dz(x,y1)-0.02))); y2=y-3.2; r2.append(ab.verts.new((x,y2,dz(x,y2)-0.30)))
for rr in ((r0,r1),(r1,r2)):
    for i in range(len(xs_)-1): ab.faces.new((rr[0][i],rr[0][i+1],rr[1][i+1],rr[1][i]))
for f in ab.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
am=bpy.data.meshes.new('WS162_Lot3_S_end_apron_feather_UNVERIFIED'); ab.to_mesh(am); ab.free(); am.materials.append(asm); col.objects.link(OB.new(am.name,am))
# ---- 3. stall paint: 90-degree stalls against the wall, pitch 2.7 m, 5.0 m deep, 0.10 m lines (ortho ticks; UNVERIFIED)
pb=bmesh.new()
def strip(a,b,w=0.13,lift=0.014):
    a=np.array(a,float); b=np.array(b,float); L=np.linalg.norm(b-a); d=(b-a)/L; n=np.array([-d[1],d[0]])*w/2; k=max(1,int(L/0.5)); prev=None
    for s in range(k+1):
        p=a+(b-a)*s/k; r=[pb.verts.new((q[0],q[1],lz(q[0],q[1])+lift)) for q in (p-n,p+n)]
        if prev: pb.faces.new((prev[0],r[0],r[1],prev[1]))
        prev=r
Bx=np.array([math.cos(math.radians(76.8-90)),math.sin(math.radians(76.8-90))])   # building 'b' axis, points E
SY=[-208.9+(-2.7)*k for k in range(10)]
for y in SY:
    xa=wallx(y)-0.35; xa_y=y; a=np.array([xa,xa_y]); b=a-Bx*5.0
    if (xa-5.0*Bx[0])>-300.0: pass
    strip(a,b)
for f in pb.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
pmesh=bpy.data.meshes.new('WS162_Lot3_stall_lines_ortho2020_10lines_2p7m_UNVERIFIED'); pb.to_mesh(pmesh); pb.free(); pmesh.materials.append(pm)
col.objects.link(OB.new(pmesh.name,pmesh))
# ---- 4. retire OSM drape faces inside the lot, push ground (terrain sheets) 10 cm below it
T=BVHTree.FromPolygons([lot.matrix_world@v.co for v in lot.data.vertices],[p.vertices for p in lot.data.polygons])
def ztop(x,y):
    h=T.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
for ro in [o for o in OB if o.type=='MESH' and (o.name in ('Roads_OSM','Footpaths_OSM') or o.name.startswith('UA_'))]:
    rb=bmesh.new(); rb.from_mesh(ro.data); rw=ro.matrix_world; k=[]
    for f in rb.faces:
        c=rw@f.calc_center_median()
        if -312<c.x<-284 and -238<c.y<-170:
            zt=ztop(c.x,c.y)
            if zt is not None and abs(c.z-zt)<1.5: k.append(f)
    if k: bmesh.ops.delete(rb,geom=k,context='FACES'); rb.to_mesh(ro.data); ro.data.update(); print('retired',ro.name,len(k))
    rb.free()
nd=0
for g in [o for o in OB if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS114_terrain_fan_fill','WS110_ground_patch','WS133b_','WS134_ground','WS60_terrain_edge_apron','Terrain_far','Skirt','WS112'))]:
    me=g.data; mw=np.array(g.matrix_world); n=len(me.vertices)
    co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); Wc=co@mw[:3,:3].T+mw[:3,3]
    idx=np.nonzero((Wc[:,0]>-309)&(Wc[:,0]<-285)&(Wc[:,1]>-238)&(Wc[:,1]<-170))[0]; c=0
    for i in idx:
        x,y,z=Wc[i]; best=None
        for ddx,ddy in ((0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3)):
            zt=ztop(x+ddx,y+ddy)
            if zt is not None: best=zt if best is None else min(best,zt)
        if best is not None and z>best-0.10: Wc[i,2]=best-0.10; c+=1
    if c:
        L=(Wc-mw[:3,3])@np.linalg.inv(mw[:3,:3]).T; me.vertices.foreach_set('co',L.ravel()); me.update(); print('pushed',g.name,c); nd+=c
print('ground pushed',nd)
px=OB.get('WS113_paving_tops_proxy')
if px:
    pbm=bmesh.new(); pbm.from_mesh(px.data); pmi=px.matrix_world.inverted(); n0=len(pbm.faces)
    for p in lot.data.polygons: pbm.faces.new([pbm.verts.new(pmi@(lot.matrix_world@lot.data.vertices[i].co)) for i in p.vertices])
    pbm.to_mesh(px.data); pbm.free(); print('proxy',n0,'->',len(px.data.polygons))
# ---- 5. seat the WS161 W door landing: pad is O+A*a+B*b; sink its underside to the lot (pad top 118.50 stays as a 5-10 cm stoop)
th=math.radians(76.8); A=Vector((math.cos(th),math.sin(th),0)); Bv=Vector((math.cos(th-math.pi/2),math.sin(th-math.pi/2),0)); O=Vector((-238.1,-180.2,0))
c=O+A*-6.0+Bv*-48.0; print('W DOOR PAD centre',round(c.x,2),round(c.y,2),'lot top',ztop(c.x,c.y),'dtm',round(dz(c.x,c.y),3))
ng=0
for o in [o for o in OB if o.name.startswith('WS161_') and o.type=='MESH']:
    me=o.data; mw=np.array(o.matrix_world); n=len(me.vertices); co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); Wc=co@mw[:3,:3].T+mw[:3,3]
    m=(np.abs(Wc[:,0]-c.x)<2.4)&(np.abs(Wc[:,1]-c.y)<2.4)&(Wc[:,2]<118.58)&(Wc[:,2]>117.9)
    # pad underside verts (z <= 118.35): drop 25 cm below local ground
    for i in np.nonzero(m&(Wc[:,2]<118.36))[0]: Wc[i,2]=min(Wc[i,2],dz(Wc[i,0],Wc[i,1])-0.25); ng+=1
    if m.any(): L=(Wc-mw[:3,3])@np.linalg.inv(mw[:3,:3]).T; me.vertices.foreach_set('co',L.ravel()); me.update()
print('pad underside verts sunk',ng)
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED',OUT)

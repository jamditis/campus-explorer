# ws142: UNIFY #49 root cause = Lot 9 (OSM 312845867, amenity=parking) was never modelled. 2023 LiDAR class-2 intensity:
# asphalt ~2k E of a concrete band (10-13k) along Freeman's E face; 2020 ortho: 9 white stall lines (2.73 m pitch) x -78.5..-72.8.
# Builds lot asphalt + stall paint + low curb on the concrete edge + S curb at the tree bed; retires OSM drape faces in the lot;
# removes WS139 walk N bridge (it sat on lot asphalt); pushes ground under. #49 pad N end now meets asphalt (no lawn skirt).
import bpy, bmesh, os, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=os.environ.get('OUT','')
OB=bpy.data.objects
W='/workspace/nj-scenes/montclair-state/scripts/ws142/'
DD=np.load(W+'dtm142.npy'); ZS=DD[1]; X0,Y1,R=-95.0,-162.0,0.5
def dz(x,y):
    fi=(x-X0)/R; fj=(Y1-y)/R
    i=int(min(max(math.floor(fi),0),ZS.shape[1]-2)); j=int(min(max(math.floor(fj),0),ZS.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(ZS[j,i]*(1-tx)*(1-ty)+ZS[j,i+1]*tx*(1-ty)+ZS[j+1,i]*(1-tx)*ty+ZS[j+1,i+1]*tx*ty)
def lz(x,y): return dz(x,y)+0.04
for o in [o for o in OB if o.name.startswith('WS142_')]: OB.remove(o)
col=bpy.data.collections.get('WS142_Lot9') or bpy.data.collections.new('WS142_Lot9')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
asm=bpy.data.materials['WS27_CollegeAve_asphalt_2020ortho']; cm=bpy.data.materials['WS27_curb_concrete_UNVERIFIED']
pm=bpy.data.materials.get('fo_cogen_white_paint') or bpy.data.materials.get('WS130_lot_paint_white')
# concrete/asphalt boundary from LiDAR intensity (x at y): (-76.7,-185) (-77.3,-190) (-77.9,-195) (-78.4,-200)
def xw(y): return -76.7+(y+185.0)*0.1133
XE=-68.25; YN=-178.6; YS_BED=-203.2; XPW=-74.6; XPE=-72.9; YPAD=-205.0; YWALK=-202.8
def ys(x):  # S edge of the lot
    if x<XPW: return YS_BED
    if x<XPE: return YPAD-0.05
    return YWALK+0.0
def inlot(x,y): return (YN>=y>=ys(x)) and (xw(y)<=x<=XE)
# ---- 1. asphalt: column strips 0.5 m with exact edges
bm=bmesh.new()
# param by (u in 0..1 between W edge and E) and v rows: build rows y, per row x from xw(y) to XE, with breaks at XPW/XPE
ys_rows=list(np.arange(YN,YS_BED-1e-6,-0.5))
if ys_rows[-1]>YS_BED+1e-6: ys_rows.append(YS_BED)
def row_x(y):
    a=xw(y); pts=sorted(set([round(x,3) for x in [a]+[x for x in np.arange(math.ceil(a*2)/2,XE,0.5) if x>a+0.05]+[XPW,XPE,XE]]))
    return pts
grid=[]
for y in ys_rows:
    grid.append([bm.verts.new((x,y,lz(x,y))) for x in row_x(y)])
# connect consecutive rows by matching x
def connect(r0,r1):
    i=j=0
    while i<len(r0)-1 or j<len(r1)-1:
        if i<len(r0)-1 and (j>=len(r1)-1 or r0[i+1].co.x<=r1[j+1].co.x):
            bm.faces.new((r0[i],r0[i+1],r1[j])); i+=1
        else:
            bm.faces.new((r0[i],r1[j],r1[j+1])); j+=1
for k in range(len(grid)-1): connect(grid[k],grid[k+1])
# S extension E of XPW: rows y YS_BED -> YPAD (x XPW..XE but walk part only to YWALK)
def strip_ext(xa,xb,y0,y1):
    xsx=[xa]+[x for x in np.arange(math.ceil(xa*2)/2,xb,0.5) if xa+0.05<x<xb-0.05]+[xb]
    rows=[]
    for y in np.linspace(y0,y1,max(2,int(abs(y1-y0)/0.5)+1)):
        rows.append([bm.verts.new((x,y,lz(x,y))) for x in xsx])
    for k in range(len(rows)-1):
        for i in range(len(xsx)-1): bm.faces.new((rows[k][i],rows[k][i+1],rows[k+1][i+1],rows[k+1][i]))
strip_ext(XPW,XPE,YS_BED,YPAD-0.05)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.02)
for f in bm.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS142_Lot9_asphalt_OSM312845867_LiDAR2023int_ortho2020_UNVERIFIEDNend'); bm.to_mesh(me); bm.free(); me.materials.append(asm)
uvl=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    p=me.vertices[lp.vertex_index].co; uvl.data[lp.index].uv=(p.x*0.25,p.y*0.25)
lot=OB.new(me.name,me); col.objects.link(lot)
# ---- 2. curbs
def curbmesh(name,LS,sgn,rev,mat,w=0.15,step=0.5):
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
# W curb on the concrete/asphalt boundary: curb sits on the concrete side (W), reveal = LiDAR step ~0.10 m
cW=curbmesh('WS142_Lot9_W_curb_Freeman_E_concrete_edge_LiDAR2023step0p10_UNVERIFIEDsection',[(xw(YN),YN),(xw(YS_BED),YS_BED)],1,0.10,cm)
cS=curbmesh('WS142_Lot9_S_curb_tree_bed_edge_UNVERIFIED',[(xw(YS_BED),YS_BED),(XPW,YS_BED)],1,0.12,cm)
print('CURB W x range',round(min(v.co.x for v in cW.data.vertices),2),round(max(v.co.x for v in cW.data.vertices),2),'S y range',round(min(v.co.y for v in cS.data.vertices),2),round(max(v.co.y for v in cS.data.vertices),2))
# ---- 3. stall paint (2020 ortho lines, pitch 2.73 m), 0.10 m wide, 1 cm proud
pb=bmesh.new()
def strip(a,b,w=0.10,lift=0.010):
    a=np.array(a,float); b=np.array(b,float); L=np.linalg.norm(b-a); d=(b-a)/L; n=np.array([-d[1],d[0]])*w/2; k=max(1,int(L/0.5)); prev=None
    for s in range(k+1):
        p=a+(b-a)*s/k; r=[pb.verts.new((q[0],q[1],lz(q[0],q[1])+lift)) for q in (p-n,p+n)]
        if prev: pb.faces.new((prev[0],r[0],r[1],prev[1]))
        prev=r
# y at x=-76 (ortho peaks), lines perpendicular to the W curb (ortho slope -0.11 m/m eastward, matches the curb bearing)
SL=[-181.0,-183.7,-186.5,-189.2,-191.9,-194.8,-197.5,-200.2,-202.85]
for y in SL:
    xa=xw(y)+0.2; strip((xa,y-0.1133*(xa+76.0)),(-72.8,y-0.1133*(-72.8+76.0)))
for f in pb.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
pmesh=bpy.data.meshes.new('WS142_Lot9_stall_lines_ortho2020_9lines_2p73m_UNVERIFIEDends'); pb.to_mesh(pmesh); pb.free()
if pm: pmesh.materials.append(pm)
col.objects.link(OB.new(pmesh.name,pmesh))
# ---- 4. remove WS139 walk N bridge (it covered y -203.1..-197.4 = lot asphalt per LiDAR int 2k)
for o in [o for o in OB if o.name.startswith('WS139_walk_N_bridge')]: print('REMOVED',o.name); OB.remove(o)
# ---- 5. retire drape faces inside the lot, push ground below
T=BVHTree.FromPolygons([lot.matrix_world@v.co for v in lot.data.vertices],[p.vertices for p in lot.data.polygons])
def ztop(x,y):
    h=T.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
for ro in [o for o in OB if o.type=='MESH' and (o.name in ('Roads_OSM','Footpaths_OSM') or o.name.startswith('UA_'))]:
    rb=bmesh.new(); rb.from_mesh(ro.data); rw=ro.matrix_world; k=[]
    for f in rb.faces:
        c=rw@f.calc_center_median()
        if -80<c.x<XE-0.05 and YS_BED-2.5<c.y<YN+0.5:
            zt=ztop(c.x,c.y)
            if zt is not None and abs(c.z-zt)<1.5: k.append(f)
    if k: bmesh.ops.delete(rb,geom=k,context='FACES'); rb.to_mesh(ro.data); ro.data.update(); print('retired',ro.name,len(k))
    rb.free()
nd=0
for g in [o for o in OB if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS114_terrain_fan_fill','WS110_ground_patch','WS133b_','WS134_ground','WS60_terrain_edge_apron'))]:
    me=g.data; mw=np.array(g.matrix_world); n=len(me.vertices)
    co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); Wc=co@mw[:3,:3].T+mw[:3,3]
    idx=np.nonzero((Wc[:,0]>-80)&(Wc[:,0]<XE+0.3)&(Wc[:,1]>YPAD-0.5)&(Wc[:,1]<YN+0.5))[0]; c=0
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
# ---- 6. probe: neighbours' tops vs lot edge
for nm in ('WS136a_Skyline','WS141_BK_NE_concrete_pad','WS135a_Skyline_Way_asphalt'):
    o=[o for o in OB if o.name.startswith(nm)]
    if not o: print('MISSING',nm); continue
    o=o[0]; tr=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons])
    for (x,y) in ((-71.5,-202.6),(-73.5,-205.2),(-68.1,-195),(-68.1,-185),(-74.0,-204.9)):
        h=tr.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); print('NB',nm[:20],x,y,round(h[0].z,3) if h[0] else None,'lot',ztop(x,y))
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws143/forecourt143.py').read())
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED',OUT)

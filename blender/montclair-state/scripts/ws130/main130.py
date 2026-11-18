# ws130: UNIFY #36. Evidence: 2023 LiDAR class-2 intensity grid (scripts/ws130/las130.npy, 1 m class map in LOG) + 2020 ortho
# (scripts/ws130/ortho_E.png, ortho_stalls.png). Findings: (1) WS129e strip x -203.6..-201 (y -232.5..-244) and x -193..-190
# (y -232.5..-236.8) lay on LAWN (Chapin S lawn E corner + the planted bed E of the drive) -> asphalt removed there, lawn restored,
# lawn E curb added (ortho pale curb line x=-199.9-0.2(-230.6-y)). (2) Asphalt service drive E of Chapin from the lot N to y -211
# between the facade (LiDAR class-6 edge (-200.3,-227.5)->(-194.4,-210)) and an E curb x=-192.6+0.19(y+235) (ortho + LiDAR).
# (3) Stall bay E of x -190 to the bed curb x -186.9 (y -236.9..-243.7) with 3 stalls (ortho lines); lot continues E y -243.7..-255.
# (4) Ladder hatch strip along the facade y -222..-230.3 (ortho). Roads_OSM drape faces under the new asphalt retired.
import bpy, bmesh, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE','0')=='1'
D='/workspace/nj-scenes/montclair-state/scripts/'
A=np.vstack([np.load(D+'ws129/las129.npy'),np.load(D+'ws130/las130.npy')]); G=A[A[:,3]==2][:,:3]
def lz(x,y,r=0.8):
    d2=(G[:,0]-x)**2+(G[:,1]-y)**2; m=d2<r*r
    if m.sum()<3: m=d2<(2.5*r)**2
    w=1/(d2[m]+0.05); return float((G[m,2]*w).sum()/w.sum())
yN=lambda x:-239.0-0.233*(x+232.0)
xL=lambda y:-199.9-max(0.0,(-230.6-y))*0.2          # S-lawn E curb front
xF=lambda y:-200.3+(y+227.5)*(5.9/17.5)              # Chapin E facade (LiDAR)
xE=lambda y:-192.6+(y+235.0)*0.19                    # drive E curb front
YBS=-236.85                                           # bed S curb front
XBE=-186.9                                            # bed/plaza W curb front (stall E end)
YBE=-243.7                                            # bed S edge E of the stalls
col=bpy.data.collections.get('WS130_Chapin_E_drive') or bpy.data.collections.new('WS130_Chapin_E_drive')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in [o for o in bpy.data.objects if o.name.startswith('WS130_')]: bpy.data.objects.remove(o)
asm=bpy.data.materials.get('WS27_CollegeAve_asphalt_2020ortho'); cm=bpy.data.materials.get('WS27_curb_concrete_UNVERIFIED')
pm=None
for m in bpy.data.materials:
    n=m.name.lower()
    if ('paint' in n or 'stripe' in n or 'zebra' in n) and 'white' in n: pm=m; break
if pm is None:
    pm=bpy.data.materials.get('WS130_lot_paint_white') or bpy.data.materials.new('WS130_lot_paint_white'); pm.use_nodes=True
    b=pm.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(0.78,0.78,0.74,1); b.inputs['Roughness'].default_value=0.75
print('M130 paint mat',pm.name)
def inlawn(x,y): return y>-244.6 and x<xL(y)+0.05 and y<-228.0
def inbed(x,y): return y>YBS-0.05 and x>xE(y)-0.05 and y<-226
# ---- 1. trim WS129e
e=[o for o in bpy.data.objects if o.name.startswith('WS129e_Chapin_S_lot_E_part')][0]
bm=bmesh.new(); bm.from_mesh(e.data); mw=e.matrix_world
kill=[f for f in bm.faces if f.normal.z<0.5]
ntop=0
for f in bm.faces:
    if f.normal.z<0.5: continue
    c=mw@f.calc_center_median()
    if inlawn(c.x,c.y) or inbed(c.x,c.y): kill.append(f); ntop+=1
bmesh.ops.delete(bm,geom=kill,context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
for ed in [ed for ed in bm.edges if ed.is_boundary]:
    a,b=ed.verts; a2=bm.verts.new(a.co-Vector((0,0,0.12))); b2=bm.verts.new(b.co-Vector((0,0,0.12))); bm.faces.new((a,b,b2,a2))
bm.to_mesh(e.data); bm.free(); e.data.update(); print('M130 WS129e top faces removed',ntop)
# ---- 2. new asphalt patches
bm=bmesh.new()
def patch(xa,xb,y0,y1,nu,nv,dz=0.01):
    Z=np.zeros((nv+1,nu+1)); XY=[]
    for j in range(nv+1):
        y=y0+(y1-y0)*j/nv; r=[]
        for i in range(nu+1):
            x0=xa(y); x1=xb(y); x=x0+(x1-x0)*i/nu; r.append((x,y)); Z[j,i]=lz(x,y)
        XY.append(r)
    for _ in range(3): Z[1:-1,1:-1]=(Z[1:-1,1:-1]*2+Z[:-2,1:-1]+Z[2:,1:-1]+Z[1:-1,:-2]+Z[1:-1,2:])/6
    vv=[[bm.verts.new((XY[j][i][0],XY[j][i][1],Z[j,i]-dz)) for i in range(nu+1)] for j in range(nv+1)]
    for j in range(nv):
        for i in range(nu): bm.faces.new((vv[j][i],vv[j][i+1],vv[j+1][i+1],vv[j+1][i]))
xW=lambda y: xL(y)+0.08 if y<-228.3 else xF(y)-0.4
patch(xW,lambda y:xE(y)+0.07,-232.75,-211.0,10,44,0.025)       # drive (2.5 cm under WS129e at the overlap)
patch(lambda y:-190.06,lambda y:XBE+0.07,YBE-0.05,YBS-0.07,6,14) # stall bay E of x -190
patch(lambda y:-190.06,lambda y:-181.0,-255.0,YBE+0.06,18,22)     # lot E continuation (construction end x -181)
bm.normal_update()
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
for ed in [ed for ed in bm.edges if ed.is_boundary]:
    a,b=ed.verts; a2=bm.verts.new(a.co-Vector((0,0,0.12))); b2=bm.verts.new(b.co-Vector((0,0,0.12))); bm.faces.new((a,b,b2,a2))
me=bpy.data.meshes.new('WS130_drive_asphalt'); bm.to_mesh(me); bm.free(); me.materials.append(asm)
dr=bpy.data.objects.new('WS130_Chapin_E_service_drive_and_stall_bay_LiDAR2023_ortho2020_UNVERIFIEDedges',me); col.objects.link(dr)
TD=BVHTree.FromPolygons([v.co for v in me.vertices],[p.vertices for p in me.polygons if p.normal.z>0.5])
TE=BVHTree.FromPolygons([mw@v.co for v in e.data.vertices],[p.vertices for p in e.data.polygons if p.normal.z>0.5])
def zpav(x,y):
    best=None
    for T in (TE,TD):
        h=T.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]
        if h is not None: best=h.z if best is None else max(best,h.z)
    return best
# ---- 3. curbs (polyline, back side given by sign)
def curb(name,pts,side,rev=0.14,w=0.15,cap0=True,cap1=True):
    P=[Vector((p[0],p[1])) for p in pts]; L=[0]
    for i in range(1,len(P)): L.append(L[-1]+(P[i]-P[i-1]).length)
    n=max(4,int(L[-1]/0.4)); S=np.linspace(0,L[-1],n+1); Q=[]
    for s in S:
        k=min(np.searchsorted(L,s,side='right')-1,len(P)-2); t=(s-L[k])/max(1e-6,L[k+1]-L[k]); Q.append(P[k].lerp(P[k+1],t))
    zs=[]
    for i,q in enumerate(Q):
        d=(Q[min(i+1,n)]-Q[max(i-1,0)]).normalized(); nn=Vector((-d.y,d.x))*side
        zp=zpav(q.x-nn.x*0.1,q.y-nn.y*0.1); zs.append(zp if zp is not None else lz(q.x,q.y)-0.01)
    zs=np.array(zs); k=9 if n>20 else 3; zs=0.5*np.convolve(np.pad(zs,k//2,mode='edge'),np.ones(k)/k,mode='valid')+0.5*np.polyval(np.polyfit(np.arange(n+1),zs,2),np.arange(n+1))
    bm=bmesh.new(); prev=None; rings=[]
    for i,q in enumerate(Q):
        d=(Q[min(i+1,n)]-Q[max(i-1,0)]).normalized(); nn=Vector((-d.y,d.x))*side; q2=q+nn*w; z=zs[i]
        ring=[bm.verts.new((q.x,q.y,z-0.2)),bm.verts.new((q.x,q.y,z+rev)),bm.verts.new((q2.x,q2.y,z+rev)),bm.verts.new((q2.x,q2.y,z-0.2))]
        if prev:
            for j in range(3): bm.faces.new((prev[j],ring[j],ring[j+1],prev[j+1]))
        prev=ring; rings.append(ring)
    if cap0: bm.faces.new(rings[0][::-1])
    if cap1: bm.faces.new(rings[-1])
    m=bpy.data.meshes.new(name); bm.normal_update(); bm.to_mesh(m); bm.free(); m.materials.append(cm)
    for f in m.polygons: pass
    o=bpy.data.objects.new(name,m); col.objects.link(o); return o
ys=np.linspace(-228.3,-244.3,30); lawnpts=[(xL(y),y) for y in ys]+[(-203.55,-244.55)]
c1=curb('WS130_S_lawn_E_curb_ortho2020_LiDAR_UNVERIFIEDreveal',lawnpts,+1)
ys=np.linspace(-211.3,-235.9,40); epts=[(xE(y),y) for y in ys]
# rounded bed SW corner R 0.9 then E along the bed S edge, S along the bed W edge (stall E end), E along y -243.7
cx,cy=xE(-235.95)+0.9,YBS+0.9
epts+=[(cx-0.9*np.cos(a),cy-0.9*np.sin(a)) for a in np.linspace(0.25,np.pi/2,5)]
epts+=[(x,YBS) for x in np.linspace(cx+0.3,XBE-0.9,8)]
epts+=[(XBE-0.9+0.9*np.sin(a),YBS-0.9+0.9*np.cos(a)) for a in np.linspace(0.3,np.pi/2,4)]
epts+=[(XBE,y) for y in np.linspace(YBS-1.2,YBE+0.9,6)]
epts+=[(XBE+0.9-0.9*np.cos(a),YBE+0.9-0.9*np.sin(a)) for a in np.linspace(0.3,np.pi/2,4)]
epts+=[(x,YBE) for x in np.linspace(XBE+1.2,-181.2,8)]
c2=curb('WS130_drive_E_bed_curb_ortho2020_LiDAR_UNVERIFIEDreveal',epts,-1)
# ---- 4. paint: 3 stalls (lines between y -236.9 and -245.4) + ladder hatch along the facade
pb=bmesh.new()
def strip(p0,p1,w):
    p0=Vector(p0); p1=Vector(p1); d=(p1-p0); L=d.length; d.normalize(); nn=Vector((-d.y,d.x))*w/2; n=max(1,int(L/0.5)); r=[]
    for i in range(n+1):
        q=p0+d*(L*i/n); pair=[]
        for s in (-1,1):
            u=q+nn*s; z=zpav(u.x,u.y); z=(z if z is not None else lz(u.x,u.y))+0.006; pair.append(pb.verts.new((u.x,u.y,z)))
        r.append(pair)
    for i in range(n): pb.faces.new((r[i][0],r[i+1][0],r[i+1][1],r[i][1]))
for y in (-239.6,-242.4,-245.2): strip((-192.5+(y+235)*0.0,y),(XBE-0.05,y),0.10)
# ladder hatch: strip 1.9 m wide along the facade y -222..-230.3, rungs every 0.9 m
for y in np.arange(-222.3,-230.31,-0.9):
    a=xF(y)+0.15; strip((a,y),(a+1.9,y-0.35),0.30)
for off in (0.15,2.05):
    strip((xF(-222.0)+off,-222.0),(xF(-230.3)+off,-230.3),0.10)
pmesh=bpy.data.meshes.new('WS130_paint'); pb.normal_update(); pb.to_mesh(pmesh); pb.free(); pmesh.materials.append(pm)
po=bpy.data.objects.new('WS130_stall_lines_and_facade_hatch_paint_ortho2020_UNVERIFIEDcount',pmesh); col.objects.link(po)
# ---- 5. retire Roads_OSM faces under the new asphalt
ro=bpy.data.objects.get('Roads_OSM'); nr=0
if ro:
    rbm=bmesh.new(); rbm.from_mesh(ro.data); rw=ro.matrix_world; k=[]
    for f in rbm.faces:
        c=rw@f.calc_center_median()
        if -202<c.x<-180 and -256<c.y<-210 and zpav(c.x,c.y) is not None: k.append(f)
    nr=len(k); bmesh.ops.delete(rbm,geom=k,context='FACES'); rbm.to_mesh(ro.data); rbm.free(); ro.data.update()
print('M130 Roads_OSM faces retired',nr)
# ---- 6. ground: lawn restored where WS129e was removed; pushed under the new asphalt; graded to curb tops
TC=[BVHTree.FromPolygons([v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons]) for o in (c1,c2)]
nu=nd=ng=0
for g in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS110_ground_patch'))]:
    gw=g.matrix_world; gi=gw.inverted()
    for v in g.data.vertices:
        p=gw@v.co
        if not (-206<p.x<-180 and -256<p.y<-210): continue
        best=None
        for dx,dy in ((0,0),(0.35,0),(-0.35,0),(0,0.35),(0,-0.35)):
            z=zpav(p.x+dx,p.y+dy)
            if z is not None: best=z if best is None else min(best,z)
        if best is not None:
            if p.z>best-0.12: p.z=best-0.12; v.co=gi@p; nd+=1
            continue
        if inlawn(p.x,p.y) or inbed(p.x,p.y):
            z=lz(p.x,p.y)-0.02
            if abs(z-p.z)>0.01: p.z=z; v.co=gi@p; nu+=1
print('M130 ground pushed',nd,'restored',nu)
# ---- 7. proxy: drop removed WS129e faces, add new tops
px=bpy.data.objects.get('WS113_paving_tops_proxy')
if px and not px.get('ws130'):
    px['ws130']=1; pbm=bmesh.new(); pbm.from_mesh(px.data); pw=px.matrix_world; pmi=pw.inverted(); n0=len(pbm.faces)
    k=[f for f in pbm.faces if (lambda c:(inlawn(c.x,c.y) or inbed(c.x,c.y)) and c.x>-203.7)(pw@f.calc_center_median())]
    bmesh.ops.delete(pbm,geom=k,context='FACES')
    for o in (dr,c1,c2):
        for p in o.data.polygons:
            if p.normal.z>0.5: pbm.faces.new([pbm.verts.new(pmi@(o.matrix_world@o.data.vertices[i].co)) for i in p.vertices])
    pbm.to_mesh(px.data); pbm.free(); print('M130 proxy',n0,'-',len(k),'->',len(px.data.polygons))
print('M130 drive faces',len(me.polygons),'paint',len(pmesh.polygons))
if SAVE: bpy.ops.wm.save_mainfile(); print('M130 SAVED')

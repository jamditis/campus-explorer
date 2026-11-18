# ws129: UNIFY #35 Chapin S lot. 2023 LiDAR class-2 (asphalt-low intensity ~25-35 vs lawn ~100+; 11-17 cm curb steps) +
# 2020 ortho (to y -250 only; uniform asphalt tone, no stall paint visible x -228..-202). Lot = asphalt from the WS128 drive N curb
# line (y=-239-0.233(x+232)) S to a parallel S curb (y=-255.5-0.233(x+218); LiDAR steps at (-224,-254.5),(-218,-255.5),(-212,-257.5)),
# W to the island E curb x -228.5 (LiDAR bright island x -240..-229, y -246..-255), E to x -202 (Roads_OSM). No markings (no ortho/photo).
import bpy, bmesh, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE','0')=='1'
D='/workspace/nj-scenes/montclair-state/scripts/ws129/'
A=np.load(D+'las129.npy'); G=A[A[:,3]==2][:,:3]
def lz(x,y,r=0.8):
    d2=(G[:,0]-x)**2+(G[:,1]-y)**2; m=d2<r*r
    if m.sum()<3: m=d2<(2.5*r)**2
    w=1/(d2[m]+0.05); return float((G[m,2]*w).sum()/w.sum())
yN=lambda x:-239.0-0.233*(x+232.0)
yS=lambda x:-255.5-0.233*(x+218.0)
XW,XM,XE=-228.5,-218.15,-202.0; YB=-246.8
for o in [o for o in bpy.data.objects if o.name.startswith('WS129_')]: bpy.data.objects.remove(o)
col=bpy.data.collections.get('WS129_Chapin_S_lot') or bpy.data.collections.new('WS129_Chapin_S_lot')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
w128=next(o for o in bpy.data.objects if o.name.startswith('WS128_Chapin_S_drive_mouth'))
m128=w128.matrix_world
T128=BVHTree.FromPolygons([m128@v.co for v in w128.data.vertices],[p.vertices for p in w128.data.polygons if p.normal.z>0.5])
bm=bmesh.new()
def patch(x0,x1,ntop,nbot,nu,nv,dz=0.0):
    Z=np.zeros((nv+1,nu+1)); XY=[]
    for j in range(nv+1):
        row=[]
        for i in range(nu+1):
            x=x0+(x1-x0)*i/nu; yt=ntop(x); yb=nbot(x); y=yt+(yb-yt)*j/nv; row.append((x,y)); Z[j,i]=lz(x,y)
        XY.append(row)
    for _ in range(3):
        Z[1:-1,1:-1]=(Z[1:-1,1:-1]*2+Z[:-2,1:-1]+Z[2:,1:-1]+Z[1:-1,:-2]+Z[1:-1,2:])/6
    vv=[]
    for j in range(nv+1):
        r=[]
        for i in range(nu+1):
            x,y=XY[j][i]; z=Z[j,i]-0.01+dz
            h=T128.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]
            if h is not None: z=min(z,h.z-0.015)
            r.append(bm.verts.new((x,y,z)))
        vv.append(r)
    for j in range(nv):
        for i in range(nu): bm.faces.new((vv[j][i],vv[j+1][i],vv[j+1][i+1],vv[j][i+1]))
patch(XM,XE,lambda x:yN(x)+0.06,yS,64,26)           # main lot, N edge tucked 6 cm under the drive N curb
patch(XW,XM+0.1,lambda x:YB,yS,42,14,dz=-0.003)     # W bay S of the WS128 drive, overlaps it (dropped under its footprint)
bm.normal_update()
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
for e in [e for e in bm.edges if e.is_boundary]:
    a,b=e.verts; a2=bm.verts.new(a.co-Vector((0,0,0.12))); b2=bm.verts.new(b.co-Vector((0,0,0.12))); bm.faces.new((a,b,b2,a2))
me=bpy.data.meshes.new('WS129_lot_asphalt'); bm.to_mesh(me); bm.free()
am=bpy.data.materials.get('WS27_CollegeAve_asphalt_2020ortho'); me.materials.append(am)
lot=bpy.data.objects.new('WS129_Chapin_S_lot_asphalt_LiDAR2023int_ortho2020_UNVERIFIEDedges',me); col.objects.link(lot)
TL=BVHTree.FromPolygons([v.co for v in me.vertices],[p.vertices for p in me.polygons if p.normal.z>0.5])
def zlot(x,y):
    h=TL.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]; return h.z if h is not None else lz(x,y)
cm=bpy.data.materials.get('WS27_curb_concrete_UNVERIFIED')
def curb(name,pl,zf,w=0.15,rev=0.14,side=1,taper=(0,0)):
    bm=bmesh.new(); prev=None; n=len(pl); rings=[]
    for k,p in enumerate(pl):
        a=pl[min(k+1,n-1)]-pl[max(k-1,0)]; t=a.normalized(); nn=Vector((-t.y,t.x))*side
        f=1.0
        if taper[0]: f=min(f,k/taper[0])
        if taper[1]: f=min(f,(n-1-k)/taper[1])
        z=zf(p.x,p.y); r=rev*f; q2=p+nn*w
        ring=[bm.verts.new((p.x,p.y,z-0.2)),bm.verts.new((p.x,p.y,z+r)),bm.verts.new((q2.x,q2.y,z+r)),bm.verts.new((q2.x,q2.y,z-0.2))]
        if prev:
            for i in range(3): bm.faces.new((prev[i],ring[i],ring[i+1],prev[i+1]))
        prev=ring; rings.append(ring)
    for rg in (rings[0],rings[-1]): bm.faces.new(rg)
    m=bpy.data.meshes.new(name); bm.normal_update(); bm.to_mesh(m); bm.free(); m.materials.append(cm)
    o=bpy.data.objects.new(name,m); col.objects.link(o); return o
# S curb (back = S side), island E curb (back = W side), N curb continuation x -218 -> -205.2 (ends at the walk tip, tapered)
S=[Vector((x,yS(x))) for x in np.linspace(XW-0.15,XE,80)]
cS=curb('WS129_Chapin_S_lot_S_curb_LiDARstep_UNVERIFIED',S,lambda x,y:zlot(x,y+0.05),side=-1)
I=[Vector((XW,y)) for y in np.linspace(-246.2,yS(XW),24)]
cI=curb('WS129_Chapin_S_lot_island_E_curb_LiDAR_UNVERIFIED',I,lambda x,y:zlot(x+0.05,y),side=-1,taper=(3,0))
Nn=[Vector((x,yN(x))) for x in np.linspace(-218.0,-205.2,34)]
w=next((o for o in bpy.data.objects if o.name.startswith('WS128_Chapin_S_drive_N_curb')),None)
if w and w.get('tapered') and not w.get('ws129_Eopen'):
    n=len(w.data.vertices)//4
    for k in range(n-3,n):
        f=min(1.0,k/3.0,(n-1-k)/2.0)
        for i in (1,2): w.data.vertices[4*k+i].co.z+=0.14*(1-f)
    w['ws129_Eopen']=1; print('M129 WS128 curb E end restored to full reveal')
cN=curb('WS129_Chapin_S_lot_N_curb_continuation_LiDARstep_UNVERIFIED',Nn,lambda x,y:zlot(x,y-0.03),side=1,taper=(0,2))
print('M129 lot faces',len(me.polygons))
# ground under paving/curbs
allT=[TL]+[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons]) for o in (cS,cI,cN)]
nl=0; ng=0
for g in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS110_ground_patch'))]:
    mw=g.matrix_world; mi=mw.inverted()
    for v in g.data.vertices:
        p=mw@v.co
        if not (XW-2<p.x<XE+0.5 and yS(p.x)-1.5<p.y<yN(p.x)+0.5): continue
        best=None
        for dx,dy in ((0,0),(0.35,0),(-0.35,0),(0,0.35),(0,-0.35)):
            for T in allT:
                h=T.ray_cast(Vector((p.x+dx,p.y+dy,200)),Vector((0,0,-1)))[0]
                if h is not None: best=h.z if best is None else min(best,h.z)
        if best is not None:
            if p.z>best-0.12: p.z=best-0.12; v.co=mi@p; nl+=1
            continue
        # lawn just S of the S curb / W of the island curb: grade up to curb top over 1 m
        dS=yS(p.x)-0.15-p.y; dI=XW-0.15-p.x
        if 0<dS<1.0 and p.x>XW: zt=zlot(p.x,yS(p.x)+0.05)+0.13; t=dS
        elif 0<dI<0.9 and yS(XW)<p.y<-246.2: zt=zlot(XW+0.05,p.y)+0.13; t=dI/0.9
        else: continue
        z2=zt*(1-t)+p.z*t
        if abs(z2-p.z)>0.005: p.z=z2; v.co=mi@p; ng+=1
print('M129 ground lowered',nl,'graded',ng)
px=bpy.data.objects.get('WS113_paving_tops_proxy')
if px and not px.get('ws129'):
    px['ws129']=1; pbm=bmesh.new(); pbm.from_mesh(px.data); pmi=px.matrix_world.inverted(); n0=len(pbm.faces)
    for o in (lot,cS,cI,cN):
        for p in o.data.polygons:
            if p.normal.z>0.5: pbm.faces.new([pbm.verts.new(pmi@(o.matrix_world@o.data.vertices[i].co)) for i in p.vertices])
    pbm.to_mesh(px.data); pbm.free(); print('M129 proxy',n0,'->',len(px.data.polygons))
if SAVE: bpy.ops.wm.save_mainfile(); print('M129 SAVED')

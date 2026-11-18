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

col=bpy.data.collections.get('WS129_Chapin_S_lot')
for o in [o for o in bpy.data.objects if o.name.startswith('WS129e_')]: bpy.data.objects.remove(o)
OLD=[o for o in bpy.data.objects if o.name.startswith(('WS129_Chapin_S_lot_asphalt','WS128_Chapin_S_drive_mouth'))]
TO=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons if p.normal.z>0.5]) for o in OLD]
bm=bmesh.new()
def patch(x0,x1,ntop,nbot,nu,nv):
    Z=np.zeros((nv+1,nu+1)); XY=[]
    for j in range(nv+1):
        row=[]
        for i in range(nu+1):
            x=x0+(x1-x0)*i/nu; yt=ntop(x); yb=nbot(x); y=yt+(yb-yt)*j/nv; row.append((x,y)); Z[j,i]=lz(x,y)
        XY.append(row)
    for _ in range(3): Z[1:-1,1:-1]=(Z[1:-1,1:-1]*2+Z[:-2,1:-1]+Z[2:,1:-1]+Z[1:-1,:-2]+Z[1:-1,2:])/6
    vv=[]
    for j in range(nv+1):
        r=[]
        for i in range(nu+1):
            x,y=XY[j][i]; z=Z[j,i]-0.01
            for T in TO:
                h=T.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]
                if h is not None: z=min(z,h.z-0.012)
            r.append(bm.verts.new((x,y,z)))
        vv.append(r)
    for j in range(nv):
        for i in range(nu): bm.faces.new((vv[j][i],vv[j+1][i],vv[j+1][i+1],vv[j][i+1]))
YT=-232.5
patch(-203.6,-202.0,lambda x:YT,lambda x:yN(x)+0.06,3,26)
patch(-202.1,-190.0,lambda x:YT,yS,24,56)
bm.normal_update()
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
for e in [e for e in bm.edges if e.is_boundary]:
    a,b=e.verts; a2=bm.verts.new(a.co-Vector((0,0,0.12))); b2=bm.verts.new(b.co-Vector((0,0,0.12))); bm.faces.new((a,b,b2,a2))
me=bpy.data.meshes.new('WS129e_lot_asphalt'); bm.to_mesh(me); bm.free(); me.materials.append(bpy.data.materials.get('WS27_CollegeAve_asphalt_2020ortho'))
lot=bpy.data.objects.new('WS129e_Chapin_S_lot_E_part_to_x-190_LiDAR2023int_UNVERIFIEDedges',me); col.objects.link(lot)
TL=BVHTree.FromPolygons([v.co for v in me.vertices],[p.vertices for p in me.polygons if p.normal.z>0.5])
def zlot(x,y):
    h=TL.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]; return h.z if h is not None else lz(x,y)-0.01
cm=bpy.data.materials.get('WS27_curb_concrete_UNVERIFIED')
bm=bmesh.new(); prev=None; rings=[]
for x in np.linspace(-202.0,-190.0,30):
    p=Vector((x,yS(x))); nn=Vector((-0.233,-1)).normalized()*-1
    nn=Vector((0.233,-1)).normalized()  # back (S) side
    z=zlot(x,p.y+0.05); q2=p+nn*0.15
    ring=[bm.verts.new((p.x,p.y,z-0.2)),bm.verts.new((p.x,p.y,z+0.14)),bm.verts.new((q2.x,q2.y,z+0.14)),bm.verts.new((q2.x,q2.y,z-0.2))]
    if prev:
        for i in range(3): bm.faces.new((prev[i],ring[i],ring[i+1],prev[i+1]))
    prev=ring; rings.append(ring)
bm.faces.new(rings[-1])
m=bpy.data.meshes.new('WS129e_S_curb'); bm.normal_update(); bm.to_mesh(m); bm.free(); m.materials.append(cm)
cE=bpy.data.objects.new('WS129e_Chapin_S_lot_S_curb_E_ext_LiDARstep_UNVERIFIED',m); col.objects.link(cE)
allT=[TL,BVHTree.FromPolygons([v.co for v in m.vertices],[p.vertices for p in m.polygons])]
nl=0; ng=0
for g in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS110_ground_patch'))]:
    mw=g.matrix_world; mi=mw.inverted()
    for v in g.data.vertices:
        p=mw@v.co
        if not (-205<p.x<-188.5 and yS(p.x)-1.5<p.y<YT+0.5): continue
        best=None
        for dx,dy in ((0,0),(0.35,0),(-0.35,0),(0,0.35),(0,-0.35)):
            for T in allT:
                h=T.ray_cast(Vector((p.x+dx,p.y+dy,200)),Vector((0,0,-1)))[0]
                if h is not None: best=h.z if best is None else min(best,h.z)
        if best is not None:
            if p.z>best-0.12: p.z=best-0.12; v.co=mi@p; nl+=1
            continue
        dS=yS(p.x)-0.15-p.y
        if 0<dS<1.0 and p.x<-190:
            zt=zlot(p.x,yS(p.x)+0.05)+0.13; z2=zt*(1-dS)+p.z*dS
            if abs(z2-p.z)>0.005: p.z=z2; v.co=mi@p; ng+=1
print('M129e faces',len(me.polygons),'ground lowered',nl,'graded',ng)
px=bpy.data.objects.get('WS113_paving_tops_proxy')
if px and not px.get('ws129e'):
    px['ws129e']=1; pbm=bmesh.new(); pbm.from_mesh(px.data); pmi=px.matrix_world.inverted(); n0=len(pbm.faces)
    for o in (lot,cE):
        for p in o.data.polygons:
            if p.normal.z>0.5: pbm.faces.new([pbm.verts.new(pmi@(o.matrix_world@o.data.vertices[i].co)) for i in p.vertices])
    pbm.to_mesh(px.data); pbm.free(); print('M129e proxy',n0,'->',len(px.data.polygons))
if SAVE: bpy.ops.wm.save_mainfile(); print('M129e SAVED')

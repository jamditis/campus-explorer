# ws131: UNIFY #39 parts. (A) Chapin S-wing S facade foundation strip: 2020 ortho shows a bright ~0.6 m concrete band
# (S edge y=-229.4-0.22(x+213)) S of the eave line, LiDAR 2023 class-2 ground between wall and band is low-intensity (dark)
# -> dark stone drip bed wall->band + concrete edge band, x -214.6 .. S-lawn E curb (UNVERIFIED material/width).
# (B) Lot E continuation: LiDAR asphalt-low continues E along y -255..-251.6 past x -170 (drive along the S side of the
# unmodelled E building, class-6 W face x~-176 for y -242..-251) -> asphalt extended to x -170 (construction end);
# between y -251.6 and the bed edge y -243.7 asphalt extended to x -180.3 with a curb, then a mulch bed to the building
# foot x -176.3 holding T_RedMaple_L1_0001 (canopy class-1 points to 6 m over it; no ground for a trunk in the aisle; UNVERIFIED).
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
col=bpy.data.collections.get('WS131_Chapin_S_facade_and_lot_E') or bpy.data.collections.new('WS131_Chapin_S_facade_and_lot_E')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in [o for o in bpy.data.objects if o.name.startswith('WS131_')]: bpy.data.objects.remove(o)
asm=bpy.data.materials.get('WS27_CollegeAve_asphalt_2020ortho'); cm=bpy.data.materials.get('WS27_curb_concrete_UNVERIFIED')
def findmat(keys,new,col_):
    for k in keys:
        for m in bpy.data.materials:
            if k in m.name.lower(): return m
    m=bpy.data.materials.new(new); m.use_nodes=True; b=m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value=col_; b.inputs['Roughness'].default_value=0.9; return m
stm=bpy.data.materials.get('WS131_drip_stone_dark_UNVERIFIED')
if stm is None:
    stm=bpy.data.materials.new('WS131_drip_stone_dark_UNVERIFIED'); stm.use_nodes=True; nt=stm.node_tree; b=nt.nodes.get('Principled BSDF')
    tc=nt.nodes.new('ShaderNodeTexCoord'); vn=nt.nodes.new('ShaderNodeTexVoronoi'); vn.inputs['Scale'].default_value=28.0
    nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=60.0
    cr=nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.06,0.058,0.055,1); cr.color_ramp.elements[1].color=(0.22,0.21,0.19,1)
    bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.6
    nt.links.new(tc.outputs['Object'],vn.inputs['Vector']); nt.links.new(tc.outputs['Object'],nz.inputs['Vector'])
    nt.links.new(nz.outputs['Fac'],cr.inputs['Fac']); nt.links.new(cr.outputs['Color'],b.inputs['Base Color'])
    nt.links.new(vn.outputs['Distance'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    b.inputs['Roughness'].default_value=0.85
mum=findmat(('mulch',),'WS131_mulch',(0.12,0.07,0.04,1))
print('M131 mats',stm.name,mum.name)
yW=lambda x:-227.33-0.24*(x+208.0)            # S facade wall (raycast: -226.37@-212 .. -229.25@-200)
yS=lambda x:-229.4-0.22*(x+213.0)             # ortho band S edge
xL=lambda y:-199.9-max(0.0,(-230.6-y))*0.2    # ws130 S-lawn E curb front
_xs=np.linspace(-214.6,-200.0,40); _zs=np.array([lz(x,yS(x)+0.8,1.2) for x in _xs]); _pc=np.polyfit(_xs,_zs,2)
print('M131 facade z fit',_pc,'resid max %.3f'%np.abs(np.polyval(_pc,_xs)-_zs).max())
def grid(name,xs,ylo,yhi,dz,mat,skirt=0.08):
    bm=bmesh.new(); vv=[]
    for x in xs:
        a,b=ylo(x),yhi(x); row=[]
        for t in (0,0.5,1):
            y=a+(b-a)*t; row.append(bm.verts.new((x,y,float(np.polyval(_pc,x))+dz+0.01*(y-yS(x)-0.8))))
        vv.append(row)
    for i in range(len(vv)-1):
        for j in range(2): bm.faces.new((vv[i][j],vv[i+1][j],vv[i+1][j+1],vv[i][j+1]))
    bm.normal_update()
    for f in bm.faces:
        if f.normal.z<0: f.normal_flip()
    for ed in [ed for ed in bm.edges if ed.is_boundary]:
        a,b=ed.verts; a2=bm.verts.new(a.co-Vector((0,0,skirt))); b2=bm.verts.new(b.co-Vector((0,0,skirt))); bm.faces.new((a,b,b2,a2))
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o
# ---- A. S facade strip
xe=-200.05
xs=list(np.linspace(-214.6,xe,30))
bed=grid('WS131_Chapin_S_facade_drip_bed_dark_stone_LiDAR2023int_UNVERIFIEDmaterial',xs,lambda x:yS(x)+0.6,lambda x:yW(x)+0.02,0.012,stm,0.15)
band=grid('WS131_Chapin_S_facade_concrete_edge_band_ortho2020_UNVERIFIEDwidth',xs,lambda x:yS(x),lambda x:yS(x)+0.6,0.045,cm,0.15)
# ---- B. lot E continuation
def patch(name,xa,xb,y0,y1,nu,nv,dz,mat,skirt=0.12):
    bm=bmesh.new(); Z=np.zeros((nv+1,nu+1)); XY=[]
    for j in range(nv+1):
        y=y0+(y1-y0)*j/nv; r=[]
        for i in range(nu+1):
            x=xa+(xb-xa)*i/nu; r.append((x,y)); Z[j,i]=lz(x,y)
        XY.append(r)
    for _ in range(3): Z[1:-1,1:-1]=(Z[1:-1,1:-1]*2+Z[:-2,1:-1]+Z[2:,1:-1]+Z[1:-1,:-2]+Z[1:-1,2:])/6
    vv=[[bm.verts.new((XY[j][i][0],XY[j][i][1],Z[j,i]-dz)) for i in range(nu+1)] for j in range(nv+1)]
    for j in range(nv):
        for i in range(nu): bm.faces.new((vv[j][i],vv[j][i+1],vv[j+1][i+1],vv[j+1][i]))
    bm.normal_update()
    for f in bm.faces:
        if f.normal.z<0: f.normal_flip()
    for ed in [ed for ed in bm.edges if ed.is_boundary]:
        a,b=ed.verts; a2=bm.verts.new(a.co-Vector((0,0,skirt))); b2=bm.verts.new(b.co-Vector((0,0,skirt))); bm.faces.new((a,b,b2,a2))
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o
XC=-180.3
a1=patch('WS131_lot_E_drive_S_of_E_building_LiDAR2023_UNVERIFIEDend_x-170',-181.08,-170.0,-255.0,-251.6,22,7,0.012,asm)
a2=patch('WS131_lot_E_aisle_end_to_curb_LiDAR2023_UNVERIFIED',-181.08,XC,-251.65,-243.7,2,16,0.012,asm)
bedm=patch('WS131_E_building_W_foot_mulch_bed_tree0001_UNVERIFIED',XC+0.15,-175.4,-251.6,-243.7,8,16,-0.06,mum,skirt=0.45)
# curb along x=XC (y -251.6..-243.7) then E along y -251.6 to x -176.3, 0.15 wide, 0.14 reveal
def curb(name,pts,w=0.15,rev=0.14):
    bm=bmesh.new(); prev=None
    P=[Vector((x,y,0)) for x,y in pts]
    for i,p in enumerate(P):
        t=(P[min(i+1,len(P)-1)]-P[max(i-1,0)]).normalized(); n=Vector((-t.y,t.x,0))
        z=lz(p.x,p.y)
        q=[bm.verts.new((p+n*s).to_tuple()) for s in (0,w,w,0)]
        q[0].co.z=z-0.15; q[1].co.z=z-0.15; q[2].co.z=z+rev; q[3].co.z=z+rev
        if prev:
            for k in range(4): bm.faces.new((prev[k],prev[(k+1)%4],q[(k+1)%4],q[k]))
        else: bm.faces.new(q[::-1])
        prev=q
    bm.faces.new(prev)
    bm.normal_update(); me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(cm)
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o
cp=[(XC,y) for y in np.linspace(-243.75,-250.9,10)]
for k in range(1,6):
    a=np.pi/2*k/6; cp.append((XC+0.7-0.7*np.cos(a),-250.9-0.7*np.sin(a)))
cp+= [(x,-251.6) for x in np.linspace(XC+0.7,-176.3,6)]
cu=curb('WS131_lot_E_aisle_end_curb_and_bed_S_curb_UNVERIFIEDreveal',cp)
# ---- tree 0001 trunk into the bed
t=bpy.data.objects.get('T_RedMaple_L1_0001')
if t:
    tx,ty=t.location.x,t.location.y
    nx=min(max(tx,XC+0.9),-177.0); ny=min(max(ty,-251.0),-244.3)
    t.location.x=nx; t.location.y=ny; t.location.z=lz(nx,ny)-0.06
    print('M131 tree0001 %.2f,%.2f -> %.2f,%.2f z %.2f'%(tx,ty,nx,ny,t.location.z))
# ---- Roads_OSM / Footpaths_OSM faces under new pieces
new=[bed,band,a1,a2,bedm,cu]
T=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons if p.normal.z>0.5]) for o in new]
def ztop(x,y):
    b=None
    for tr in T:
        h=tr.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if h[0] is not None: b=h[0].z if b is None else max(b,h[0].z)
    return b
d130=[o for o in bpy.data.objects if o.name.startswith('WS130_Chapin_E_service_drive')][0]
T130=BVHTree.FromPolygons([d130.matrix_world@v.co for v in d130.data.vertices],[p.vertices for p in d130.data.polygons if p.normal.z>0.5])
def onasph(x,y):
    if ztop(x,y) is not None: return True
    return x>-192 and T130.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0] is not None
for nm in ('Roads_OSM','Footpaths_OSM','OZ_walk_joints_auto_GN_UNVERIFIED'):
    ro=bpy.data.objects.get(nm)
    if not ro or ro.type!='MESH': continue
    rb=bmesh.new(); rb.from_mesh(ro.data); rw=ro.matrix_world
    k=[f for f in rb.faces if (lambda c:-216<c.x<-169 and -256<c.y<-226 and onasph(c.x,c.y))(rw@f.calc_center_median())]
    bmesh.ops.delete(rb,geom=k,context='FACES'); rb.to_mesh(ro.data); rb.free(); ro.data.update(); print('M131 retired',nm,len(k))
# ---- ground push under new tops
nd=0
for g in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS110_ground_patch'))]:
    gw=g.matrix_world; gi=gw.inverted()
    for v in g.data.vertices:
        p=gw@v.co
        if not (-216<p.x<-169 and -256<p.y<-225): continue
        best=None
        for dx,dy in ((0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3)):
            z=ztop(p.x+dx,p.y+dy)
            if z is not None: best=z if best is None else min(best,z)
        if best is not None and p.z>best-0.10: p.z=best-0.10; v.co=gi@p; nd+=1
    g.data.update()
print('M131 ground verts pushed',nd)
px=bpy.data.objects.get('WS113_paving_tops_proxy')
if px and not px.get('ws131'):
    px['ws131']=1; pbm=bmesh.new(); pbm.from_mesh(px.data); pmi=px.matrix_world.inverted(); n0=len(pbm.faces)
    for o in new:
        for p in o.data.polygons:
            if p.normal.z>0.5: pbm.faces.new([pbm.verts.new(pmi@(o.matrix_world@o.data.vertices[i].co)) for i in p.vertices])
    pbm.to_mesh(px.data); pbm.free(); print('M131 proxy',n0,'->',len(px.data.polygons))
for o in new: print('M131',o.name,len(o.data.polygons))
if SAVE: bpy.ops.wm.save_mainfile(); print('M131 SAVED')

# ws138a: lot S of Russ (ws137p evidence) merged with the BK lot; S/W/E curbs; N-row stalls + hatch; white-curbed bed on Russ E-wing S face.
import bpy, bmesh, os, math, json, random, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE','0')=='1'
W='/workspace/nj-scenes/montclair-state/scripts/'
D=W+'ws134/'; exec(open(D+'dtm_helpers.py').read())
OSM=json.load(open(W+'ws134/osm134.json')); BK=[(a,b) for a,b in OSM['312845862'][:-1]]
ZS=np.load(W+'ws138/dtm138_s.npy').astype(float); X0,Y1,R=-185.0,-240.0,4.0
def dz(x,y):
    fi=(x-X0)*R-0.5; fj=(Y1-y)*R-0.5
    i=int(min(max(math.floor(fi),0),ZS.shape[1]-2)); j=int(min(max(math.floor(fj),0),ZS.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(ZS[j,i]*(1-tx)*(1-ty)+ZS[j,i+1]*tx*(1-ty)+ZS[j+1,i]*(1-tx)*ty+ZS[j+1,i+1]*tx*ty)
def lz(x,y): return dz(x,y)+0.05
col=bpy.data.collections.get('WS138_Russ_S_lot') or bpy.data.collections.new('WS138_Russ_S_lot')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in [o for o in bpy.data.objects if o.name.startswith('WS138a_')]: bpy.data.objects.remove(o)
# ---- 1. retire superseded ws135/ws136 pieces
for pre in ('WS136a_BK_lot_W_end_curb','WS136a_BK_lot_E_edge_curb','WS135a_BK_S_lot_asphalt','WS135a_BK_lot_S_curb'):
    for o in [o for o in bpy.data.objects if o.name.startswith(pre)]: print('REMOVED',o.name); bpy.data.objects.remove(o)
po=[o for o in bpy.data.objects if o.name.startswith('WS135a_edge_lines_and_stall_lines')]
pm=None
if po:
    o=po[0]; pm=o.data.materials[0] if o.data.materials else None
    bm=bmesh.new(); bm.from_mesh(o.data); k=[f for f in bm.faces if (o.matrix_world@f.calc_center_median()).x<-90]
    bmesh.ops.delete(bm,geom=k,context='FACES'); bm.to_mesh(o.data); bm.free(); print('old stall paint faces',len(k))
asm=bpy.data.materials['WS27_CollegeAve_asphalt_2020ortho']; cm=bpy.data.materials['WS27_curb_concrete_UNVERIFIED']
mulch=bpy.data.objects['WS131_E_building_W_foot_mulch_bed_tree0001_UNVERIFIED'].data.materials[0]
wc=bpy.data.materials.get('WS138_curb_white_concrete_UNVERIFIEDtone')
if wc is None:
    wc=bpy.data.materials.new('WS138_curb_white_concrete_UNVERIFIEDtone'); wc.use_nodes=True
    b=wc.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.62,0.61,0.57,1); b.inputs['Roughness'].default_value=0.85
# ---- 2. outline
SC=[(-163.0,-270.70),(-119.37,-281.88),(-91.0,-287.62)]
def ymin(x): return float(np.interp(x,[p[0] for p in SC],[p[1] for p in SC]))
TOPW=[(-163.0,-265.3),(-160.2,-258.3)]
def ymax(x,side):
    e=1e-6*side; x2=x+e
    if x2<-160.2: return float(np.interp(x2,[-163,-160.2],[-265.3,-258.3]))
    if x2<-146.5: return -252.6
    if x2<-129.5: return -262.3
    if x2<-125.2: return float(np.interp(x2,[-129.5,-125.2],[-262.3,-265.0]))
    if x2<-121.5: return -265.0
    return float(np.interp(x2,[-121.5,-93.5,-91.0],[-263.0,-269.4,-269.4]))
xs=sorted(set([round(v,3) for v in list(np.arange(-163.0,-90.99,1.0))+[-160.2,-146.5,-129.5,-125.2,-121.5,-119.37,-93.5]]))
xs2=[xs[0]]
for v in xs[1:]:
    if v-xs2[-1]>0.15: xs2.append(v)
xs=xs2; NR=32
bm=bmesh.new(); N=0
for i in range(len(xs)-1):
    xa,xb=xs[i],xs[i+1]
    ya0,ya1=ymin(xa),ymax(xa,1); yb0,yb1=ymin(xb),ymax(xb,-1)
    for j in range(NR):
        t0=j/NR; t1=(j+1)/NR
        ps=[(xa,ya0+(ya1-ya0)*t0),(xb,yb0+(yb1-yb0)*t0),(xb,yb0+(yb1-yb0)*t1),(xa,ya0+(ya1-ya0)*t1)]
        cx=sum(p[0] for p in ps)/4; cy=sum(p[1] for p in ps)/4
        if xa>=-121.6 and pip(BK,cx,cy): continue
        bm.faces.new([bm.verts.new((px,py,lz(px,py))) for px,py in ps]); N+=1
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.003)
for f in bm.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
# skirt on boundary
be=[e for e in bm.edges if e.is_boundary]
for e in be:
    a,b=e.verts; a2=bm.verts.new(a.co-Vector((0,0,0.25))); b2=bm.verts.new(b.co-Vector((0,0,0.25)))
    bm.faces.new((b,a,a2,b2))
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.003)
lot=bpy.data.meshes.new('WS138a_Russ_S_and_BK_lot_asphalt_one_surface_LiDAR2023_ortho2020'); bm.to_mesh(lot); bm.free(); lot.materials.append(asm)
uvl=lot.uv_layers.new(name='UVMap')
for lp in lot.loops:
    p=lot.vertices[lp.vertex_index].co; uvl.data[lp.index].uv=(p.x*0.002+0.5,p.y*0.002+0.5)
lo=bpy.data.objects.new(lot.name,lot); col.objects.link(lo); print('lot faces',N)
# ---- 3. curbs
def curbmesh(name,LS,sgn,rev,mat,w=0.18,step=1.0,centre=False):
    bm=bmesh.new(); pts=[]
    for k in range(len(LS)-1):
        a=np.array(LS[k]); b=np.array(LS[k+1]); L=np.linalg.norm(b-a); n=max(1,int(math.ceil(L/step)))
        for s in range(n): pts.append(a+(b-a)*s/n)
    pts.append(np.array(LS[-1])); rings=[]
    for k,p in enumerate(pts):
        if 0<k<len(pts)-1:
            d1=pts[k]-pts[k-1]; d2=pts[k+1]-pts[k]; d1/=np.linalg.norm(d1); d2/=np.linalg.norm(d2); d=d1+d2; d/=np.linalg.norm(d)
        else:
            q=pts[min(k+1,len(pts)-1)]-pts[max(k-1,0)]; d=q/np.linalg.norm(q)
        n=np.array([d[1],-d[0]])*sgn
        z=lz(p[0],p[1]); a=p-(n*w/2 if centre else 0); b=a+n*w
        zb=min(z-0.30,dz(*(b+n*0.4))-0.15)
        rings.append([bm.verts.new((a[0],a[1],zb)),bm.verts.new((a[0],a[1],z+rev)),bm.verts.new((b[0],b[1],z+rev)),bm.verts.new((b[0],b[1],zb))])
    for i in range(len(rings)-1):
        for j in range(3): bm.faces.new((rings[i][j],rings[i+1][j],rings[i+1][j+1],rings[i][j+1]))
        bm.faces.new((rings[i][3],rings[i+1][3],rings[i+1][0],rings[i][0]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    m=bpy.data.meshes.new(name); bm.to_mesh(m); bm.free(); m.materials.append(mat); o=bpy.data.objects.new(name,m); col.objects.link(o); return o
REV=0.17
c1=curbmesh('WS138a_lot_S_curb_two_straight_segments_LiDAR2023_UNVERIFIEDsection',[(-163.18,ymin(-163.0)+0.0),(-119.37,-281.88),(-90.82,ymin(-91.0)-0.036)],-1,REV,cm)
c2=curbmesh('WS138a_lot_W_curb_x-163_LiDAR2023_UNVERIFIEDsection',[(-163.0,-265.3),(-163.0,ymin(-163.0)-0.18)],-1,REV,cm)
c3=curbmesh('WS138a_lot_E_curb_x-91_ortho2020_UNVERIFIEDreveal',[(-91.0,-269.4),(-91.0,ymin(-91.0)-0.18)],1,REV,cm)
# ---- 4. Russ E-wing S bed: find wall per x by ray cast north
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
wally={}
for x in np.arange(-146.5,-129.49,0.5):
    z=lz(x,-262.0)+0.6; h=sc.ray_cast(dg,Vector((x,-262.0,z)),Vector((0,1,0)),distance=9.0)
    wally[round(x,2)]=(h[1].y, h[4].name) if h[0] else (None,None)
print('WALL',{k:(round(v[0],2) if v[0] else None,v[1]) for k,v in list(wally.items())[::4]})
def wy(x):
    v=wally.get(round(round(x*2)/2,2),(None,None))[0]
    return (v+0.25) if v is not None else float(np.interp(x,[-146.5,-129.5],[-257.0,-258.8]))
bm=bmesh.new(); rows=[]
BX=np.arange(-146.35,-129.64,0.5); BX=np.append(BX,-129.65)
for x in BX:
    y0=-262.15; y1=max(wy(x),y0+0.5); rows.append([bm.verts.new((x,y,lz(x,-262.2)+0.10+0.03*(y-y0)/(y1-y0))) for y in np.linspace(y0,y1,8)])
for i in range(len(rows)-1):
    for j in range(7): bm.faces.new((rows[i][j],rows[i+1][j],rows[i+1][j+1],rows[i][j+1]))
for f in bm.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
mb=bpy.data.meshes.new('WS138a_Russ_Ewing_S_bed_mulch_ortho2020_LiDARshrubs_UNVERIFIEDplanting'); bm.to_mesh(mb); bm.free(); mb.materials.append(mulch)
bo=bpy.data.objects.new(mb.name,mb); col.objects.link(bo)
c4=curbmesh('WS138a_Russ_Ewing_S_bed_white_curb_ortho2020',[(-146.5,wy(-146.5)),(-146.5,-262.3),(-129.5,-262.3),(-129.5,wy(-129.5))],1,0.15,wc,w=0.15,step=0.5,centre=True)
# shrubs: reuse campus-asset shrubs from WS125 (linked data), scaled down 15 % (ws125 self-review)
src=[o for o in bpy.data.objects if o.name.startswith(('Boxwood','Yew','Azalea')) and o.users_collection and o.users_collection[0].name.startswith('WS125')]
if not src:
    c125=bpy.data.collections.get('WS125_Chapin_W_bank_planting')
    src=[o for o in (c125.all_objects if c125 else []) if o.type in ('MESH','EMPTY') and not o.name.startswith('ShrubLeaf')][:6]
print('SHRUB SRC',[o.name for o in src[:6]])
random.seed(138); ns=0
if src:
    for x in np.arange(-145.2,-129.9,1.45):
        if x<-141.0 and random.random()<0.5: continue   # LiDAR shrub returns cluster x -140...-128
        s=random.choice(src); o=s.copy(); o.name='WS138a_bed_shrub_'+s.name.split('.')[0]
        y=(-262.15+wy(x))/2; o.location=(x+random.uniform(-0.2,0.2),y,lz(x,y)+0.10); o.rotation_euler=(0,0,random.uniform(0,6.28))
        sf=random.uniform(0.7,0.95); o.scale=(s.scale[0]*sf,s.scale[1]*sf,s.scale[2]*sf); o.parent=None
        col.objects.link(o); ns+=1
print('shrubs',ns)
# ---- 5. paint
if pm is None:
    pm=bpy.data.materials.get('WS130_lot_paint_white')
pb=bmesh.new()
def strip(a,b,w=0.10,lift=0.012):
    a=np.array(a,float); b=np.array(b,float); L=np.linalg.norm(b-a); d=(b-a)/L; n=np.array([-d[1],d[0]])*w/2; k=max(1,int(L/0.5)); prev=None
    for s in range(k+1):
        p=a+(b-a)*s/k; r=[pb.verts.new((q[0],q[1],lz(q[0],q[1])+lift)) for q in (p-n,p+n)]
        if prev: pb.faces.new((prev[0],r[0],r[1],prev[1]))
        prev=r
for (xh,xf) in ((-157.2,-158.0),(-154.6,-155.6)): strip((xh,-252.9),(xf+(xh-xf)*0.0,-258.0))
hx0,hx1,hy0,hy1=-153.5,-149.5,-259.8,-253.8
for a,b in (((hx0,hy0),(hx1,hy0)),((hx1,hy0),(hx1,hy1)),((hx1,hy1),(hx0,hy1)),((hx0,hy1),(hx0,hy0))): strip(a,b,0.10)
for c in np.arange(hx0-hy1+0.6,hx1-hy0,0.75):   # 45-degree hatch lines x - y = c clipped to the box
    p=[]
    for (x,y) in ((hx0,hx0-c),(hx1,hx1-c),(c+hy0,hy0),(c+hy1,hy1)):
        if hx0-1e-6<=x<=hx1+1e-6 and hy0-1e-6<=y<=hy1+1e-6: p.append((x,y))
    p=sorted(set(p))
    if len(p)>=2 and math.dist(p[0],p[-1])>0.3: strip(p[0],p[-1],0.10)
def srow(x,L):
    y=ymin(x); seg=0 if x<-119.37 else 1
    m=(SC[seg+1][1]-SC[seg][1])/(SC[seg+1][0]-SC[seg][0]); n=np.array([-m,1.0]); n/=np.linalg.norm(n)
    f=np.array([x,y])+n*0.5; strip(f,f+n*L)
for x in (-157.5,-154.4,-152.2): srow(x,5.4)
for x in (-121.0,-118.6,-109.3,-106.5,-103.9,-101.5): srow(x,6.5)
for f in pb.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
pmesh=bpy.data.meshes.new('WS138a_lot_paint_Nrow_stalls_hatch_Srow_visible_marks_ortho2020_UNVERIFIEDpitch'); pb.to_mesh(pmesh); pb.free()
if pm: pmesh.materials.append(pm)
col.objects.link(bpy.data.objects.new(pmesh.name,pmesh))
# ---- 6. retire drape faces under the new tops, push ground below them, add tops to the GN ground-hold proxy
new=[lo,bo]
T=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons if p.normal.z>0.5]) for o in new]
def ztop(x,y):
    b=None
    for tr in T:
        h=tr.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if h[0] is not None: b=h[0].z if b is None else max(b,h[0].z)
    return b
BOX=(-164,-90,-289,-251)
for ro in [o for o in bpy.data.objects if o.type=='MESH' and (o.name in ('Roads_OSM','Footpaths_OSM','OZ_walk_joints_auto_GN_UNVERIFIED') or o.name.startswith('UA_'))]:
    rb=bmesh.new(); rb.from_mesh(ro.data); rw=ro.matrix_world
    k=[f for f in rb.faces if (lambda c:BOX[0]<c.x<BOX[1] and BOX[2]<c.y<BOX[3] and ztop(c.x,c.y) is not None)(rw@f.calc_center_median())]
    if k: bmesh.ops.delete(rb,geom=k,context='FACES'); rb.to_mesh(ro.data); ro.data.update(); print('retired',ro.name,len(k))
    rb.free()
nd=0; mx=0
for g in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS114_terrain_fan_fill','WS110_ground_patch','WS133b_','WS134_ground','WS60_terrain_edge_apron'))]:
    gw=g.matrix_world; gi=gw.inverted(); c=0
    for v in g.data.vertices:
        p=gw@v.co
        if not (BOX[0]<p.x<BOX[1] and BOX[2]<p.y<BOX[3]): continue
        best=None
        for ddx,ddy in ((0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3)):
            z=ztop(p.x+ddx,p.y+ddy)
            if z is not None: best=z if best is None else min(best,z)
        if best is not None and p.z>best-0.10: mx=max(mx,p.z-(best-0.10)); p.z=best-0.10; v.co=gi@p; nd+=1; c+=1
    g.data.update()
    if c: print('pushed',g.name,c)
print('ground verts pushed',nd,'max',round(mx,3))
px=bpy.data.objects.get('WS113_paving_tops_proxy')
if px and not px.get('ws138'):
    px['ws138']=1; pbm=bmesh.new(); pbm.from_mesh(px.data); pmi=px.matrix_world.inverted(); n0=len(pbm.faces)
    for o in new:
        for p in o.data.polygons:
            if p.normal.z>0.5: pbm.faces.new([pbm.verts.new(pmi@(o.matrix_world@o.data.vertices[i].co)) for i in p.vertices])
    pbm.to_mesh(px.data); pbm.free(); print('proxy',n0,'->',len(px.data.polygons))
# ---- 7. probe: anything above the new lot top (poke-through) and what lies W of the Skyline walk (dark surface in the ws136 N eye view)
dg=bpy.context.evaluated_depsgraph_get(); pk={}
newn=set(o.name for o in col.objects)
for x in np.arange(-162,-92,2.0):
    for y in np.arange(ymin(x)+0.6,ymax(x,1)-0.4,2.0):
        zt=ztop(x,y)
        if zt is None: continue
        o=Vector((x,y,zt+0.5))
        for _ in range(4):
            h=sc.ray_cast(dg,o,Vector((0,0,-1)),distance=1.0)
            if not h[0]: break
            if h[4].name not in newn and h[1].z>zt-0.004: pk[h[4].name]=pk.get(h[4].name,0)+1
            if h[4].name in newn: break
            o=h[1]-Vector((0,0,0.001))
print('POKE',pk)
for (x,y) in ((-74,-215),(-76,-225),(-80,-230),(-85,-240),(-74,-205),(-71.5,-201)):
    h=sc.ray_cast(dg,Vector((x,y,140)),Vector((0,0,-1)))
    print('DOWN',x,y,(round(h[1].z,2),h[4].name) if h[0] else None)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

# ws118: replace the WS117 sawtooth terrace edge wall (8 axis boxes on a diagonal) and stepped terrace slab
# with one continuous straight wall + one continuous slab following the LiDAR 124.5 m contour xr(y).
import bpy, bmesh, numpy as np, os
R='/workspace/nj-scenes/montclair-state/'
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
ZL=124.77; XW=-209.1; YC=-196.95; CW=0.30; YN=-182.0; Y0=YC+CW
xr=lambda y: -213.3+(min(y,-184.0)+196.65)*(2.3/12.65)
def strip_edge(o):
    bm=bmesh.new(); bm.from_mesh(o.data); mw=o.matrix_world
    kill=[]
    for f in bm.faces:
        ws=[mw@v.co for v in f.verts]
        if any(w.y>Y0+0.05 for w in ws): kill.append(f)
        elif all(abs(w.y-Y0)<0.006 for w in ws) and (mw.to_3x3()@f.normal).y<-0.5: kill.append(f)
    n=len(kill); bmesh.ops.delete(bm,geom=kill,context='FACES')
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
    bm.to_mesh(o.data); bm.free(); o.data.update(); return n
def prism(o,xa,xb,za,zb):
    # continuous closed band over y samples; xa(y)<xb(y), za(y,x) bottom, zb top
    bm=bmesh.new(); bm.from_mesh(o.data); inv=o.matrix_world.inverted()
    ys=list(np.linspace(Y0,-184.0,24))+list(np.linspace(-184.0,YN,4)[1:])
    rings=[]
    for y in ys:
        x0=xa(y); x1=xb(y)
        rings.append([bm.verts.new(inv@__import__('mathutils').Vector(c)) for c in ((x0,y,za(x0,y)),(x1,y,za(x1,y)),(x1,y,zb),(x0,y,zb))])
    for r0,r1 in zip(rings[:-1],rings[1:]):
        for i in range(4):
            j=(i+1)%4; bm.faces.new((r0[i],r0[j],r1[j],r1[i]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(o.data); bm.free(); o.data.update()
wall=O('WS117_Chapin_W_entrance_cheek_and_terrace_edge_walls'); slab=O('WS117_Chapin_W_entrance_landing_terrace')
print('M118 wall faces removed',strip_edge(wall),'slab faces removed',strip_edge(slab))
prism(slab,lambda y: xr(y)-0.02,lambda y: XW,lambda x,y: ZL-1.2,ZL)
prism(wall,lambda y: xr(y)-CW,lambda y: xr(y)+0.01,lambda x,y: min(dtm(x,y),dtm(xr(y)-CW-0.5,y))-0.40,ZL+0.45)

# push the WS113 DTM fill (1 m grid) below the bed along the new wall (it poked 0.1-0.25 m through the bed within ~1 m of the wall)
# the terrace is retained by a 0.75 m wall: it must NOT be a paving edge the lawn grades up to (WS113 GN). Drop its tops from the proxy.
pv=bpy.data.objects.get('WS113_paving_tops_proxy')
if pv:
    b2=bmesh.new(); b2.from_mesh(pv.data); pmw=pv.matrix_world
    dl=[f for f in b2.faces if (lambda c:(c.y>Y0+0.05 and xr(c.y)-0.6<c.x<XW+0.3 and abs(c.z-ZL)<0.3))(pmw@f.calc_center_median())]
    bmesh.ops.delete(b2,geom=dl,context='FACES'); b2.to_mesh(pv.data); b2.free(); pv.data.update(); print('M118 proxy terrace faces dropped',len(dl))
fill=O('WS113_terrain_fan_fill'); mw=fill.matrix_world; inv=mw.inverted(); nl=0
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
BB=[]
for bo in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WS116_Chapin_W_bed')]:
    e=bo.evaluated_get(dg); me=e.to_mesh(); bw=bo.matrix_world
    BB.append(BVHTree.FromPolygons([tuple(bw@v.co) for v in me.vertices],[tuple(q.vertices) for q in me.polygons])); e.to_mesh_clear()
def bedz(x,y):
    zs=[h[0].z for h in (b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150) for b in BB) if h[0] is not None]
    return min(zs) if zs else None
for v in fill.data.vertices:
    w=mw@v.co
    if -197.2<=w.y<=-182.0 and xr(w.y)-CW-2.6<=w.x<=xr(w.y)+0.8:
        zs=[bedz(w.x+dx,w.y+dy) for dx in (-0.6,0,0.6) for dy in (-0.6,0,0.6)]
        zs=[z for z in zs if z is not None]
        if not zs: continue
        zt=min(min(zs)-0.12,dtm(w.x,w.y)-0.45)
        if w.z>zt: w.z=zt; v.co=inv@w; nl+=1
fill.data.update(); print('M118 fill verts lowered',nl)
wall.name='WS117_Chapin_W_entrance_cheek_and_terrace_edge_walls_white_UNVERIFIEDheight_ws118straight'
for o in (wall,slab):
    m=bmesh.new(); m.from_mesh(o.data); print('M118',o.name[:60],'v',len(m.verts),'f',len(m.faces)); m.free()
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M118 SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M118 SAVED',SAVE)

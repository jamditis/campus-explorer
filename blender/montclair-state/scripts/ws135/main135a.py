# ws135a: DAY 18 layer 2 roads. Skyline Way y -190..-285 as ONE asphalt ribbon (edges from the 2020 ortho bright edge lines),
# retire Roads_OSM + UA_SkylineWay_south faces under it; W walk S of -248.5; BK S lot asphalt + S curb + stall lines (ortho2020).
import bpy, bmesh, os, math, json, numpy as np
from mathutils import Vector
SAVE=os.environ.get('SAVE','0')=='1'
D='/workspace/nj-scenes/montclair-state/scripts/ws134/'
exec(open(D+'dtm_helpers.py').read())
OSM=json.load(open(D+'osm134.json')); BK=[(a,b) for a,b in OSM['312845862'][:-1]]
col=bpy.data.collections.get('WS135_Skyline_Way_and_BK_lot') or bpy.data.collections.new('WS135_Skyline_Way_and_BK_lot')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in [o for o in bpy.data.objects if o.name.startswith('WS135a_')]: bpy.data.objects.remove(o)
asm=bpy.data.materials['WS27_CollegeAve_asphalt_2020ortho']; cm=bpy.data.materials['WS27_curb_concrete_UNVERIFIED']
wm=bpy.data.materials.get('WS3_Concrete_panels_sawcut')
pm=None
for m in bpy.data.materials:
    if m.name=='WS130_lot_paint_white': pm=m
if pm is None:
    for m in bpy.data.materials:
        n=m.name.lower()
        if ('paint' in n or 'stripe' in n or 'zebra' in n) and 'white' in n: pm=m; break
print('paint mat',pm.name if pm else None)
# measured edges (x vs y) from ortho bright lines
EY=[-190,-205,-212.5,-220,-235,-250,-262,-272.5,-276.2,-280,-284]
EL=[-67.9,-67.9,-68.3,-68.1,-68.12,-68.25,-68.45,-68.38,-68.12,-67.75,-67.4]
ER=[-63.0,-62.9,-62.6,-62.6,-62.62,-62.75,-62.88,-63.0,-62.75,-62.25,-61.8]
def edge(y,E): return float(np.interp(-y,[-v for v in EY],E))
def lz(x,y): return dtm(x,y)
# ---- road ribbon
bm=bmesh.new(); rows=[]
ys=np.arange(-190.0,-284.01,-1.0)
for y in ys:
    xl,xr=edge(y,EL),edge(y,ER); r=[]
    for t in np.linspace(0,1,7):
        x=xl+(xr-xl)*t; r.append(bm.verts.new((x,y,lz(x,y)+0.05)))
    rows.append(r)
for i in range(len(rows)-1):
    for j in range(6): bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
for j in (0,6):
    sk=[bm.verts.new((r[j].co.x,r[j].co.y,r[j].co.z-0.25)) for r in rows]
    for i in range(len(rows)-1): bm.faces.new((rows[i][j],rows[i+1][j],sk[i+1],sk[i]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if f.normal.z<-0.5 and False: f.normal_flip()
me=bpy.data.meshes.new('WS135a_Skyline_Way_asphalt_y-190_-284_ortho2020_edges_LiDAR2023_UNVERIFIEDwidth'); bm.to_mesh(me); bm.free(); me.materials.append(asm)
for p in me.polygons:
    pass
ro_=bpy.data.objects.new(me.name,me); col.objects.link(ro_)
# make sure top faces point up
bm=bmesh.new(); bm.from_mesh(me)
for f in bm.faces:
    if abs(f.normal.z)>0.5 and f.normal.z<0: f.normal_flip()
bm.to_mesh(me); bm.free()
# ---- edge lines (worn white, UNVERIFIED)
pb=bmesh.new()
def strip(pts,w,off=0.0):
    r=[]
    for k,(x,y) in enumerate(pts):
        r.append((x,y))
    q=[]
    for k in range(len(r)-1):
        p0=Vector((*r[k],0)); p1=Vector((*r[k+1],0)); d=(p1-p0); d.normalize(); n=Vector((-d.y,d.x))*w/2
        if k==0: q.append([pb.verts.new((r[k][0]+n.x*s,r[k][1]+n.y*s,lz(r[k][0]+n.x*s,r[k][1]+n.y*s)+0.062)) for s in (-1,1)])
        q.append([pb.verts.new((r[k+1][0]+n.x*s,r[k+1][1]+n.y*s,lz(r[k+1][0]+n.x*s,r[k+1][1]+n.y*s)+0.062)) for s in (-1,1)])
    for i in range(len(q)-1):
        f=pb.faces.new((q[i][0],q[i+1][0],q[i+1][1],q[i][1]))
for E,sg in ((EL,1),(ER,-1)):
    pts=[(edge(y,E)+sg*0.18,y) for y in np.arange(-190.5,-283.5,-1.0)]
    strip(pts,0.10)
# ---- W walk S of -248.5 (ortho)
WC=[(-71.9,-248.5),(-71.6,-258),(-71.4,-265),(-71.0,-272),(-70.8,-278),(-70.3,-285)]
HW=1.15
bm=bmesh.new(); rows=[]
pts=[]
for k in range(len(WC)-1):
    a=np.array(WC[k]); b=np.array(WC[k+1]); L=np.linalg.norm(b-a)
    for s in np.arange(0,L,0.5): pts.append(a+(b-a)*s/L)
pts.append(np.array(WC[-1]))
for k,p in enumerate(pts):
    q=pts[min(k+1,len(pts)-1)]-pts[max(k-1,0)]; d=q/np.linalg.norm(q); n=np.array([-d[1],d[0]])
    r=[]
    for t in np.linspace(-HW,HW,5):
        u=p+n*t; r.append(bm.verts.new((u[0],u[1],lz(u[0],u[1])+0.07)))
    rows.append(r)
for i in range(len(rows)-1):
    for j in range(4): bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
for j in (0,4):
    sk=[bm.verts.new((r[j].co.x,r[j].co.y,r[j].co.z-0.2)) for r in rows]
    for i in range(len(rows)-1): bm.faces.new((rows[i][j],rows[i+1][j],sk[i+1],sk[i]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me2=bpy.data.meshes.new('WS135a_Skyline_W_walk_S_of_-248_ortho2020_2p3m_UNVERIFIEDjoints'); bm.to_mesh(me2); bm.free()
if wm: me2.materials.append(wm)
uvl=me2.uv_layers.new(name='UVMap')
for lp in me2.loops:
    p=me2.vertices[lp.vertex_index].co; uvl.data[lp.index].uv=(p.x/2.0,p.y/2.0)
bm=bmesh.new(); bm.from_mesh(me2)
for f in bm.faces:
    if abs(f.normal.z)>0.5 and f.normal.z<0: f.normal_flip()
bm.to_mesh(me2); bm.free()
col.objects.link(bpy.data.objects.new(me2.name,me2))
# ---- BK S lot
LOT=[(-121.5,-263.0),(-93.5,-269.4),(-91.0,-269.4),(-91.0,-280.9),(-103.0,-280.9),(-121.5,-277.3)]
LS=[(-91.0,-280.9),(-103.0,-280.9),(-121.5,-277.3)]   # curb line along S edge
def inbk(x,y): return pip(BK,x,y)
bm=bmesh.new(); N=0
xs=np.arange(-121.5,-90.99,1.0); 
def ymin(x): # lot S edge
    return float(np.interp(x,[-121.5,-103.0,-91.0],[-277.3,-280.9,-280.9]))
def ymax(x): return float(np.interp(x,[-121.5,-93.5,-91.0],[-263.0,-269.4,-269.4]))
cells={}
for i in range(len(xs)-1):
    xa,xb=xs[i],xs[i+1]; xm=(xa+xb)/2
    y0=max(ymin(xa),ymin(xb)); y1=min(ymax(xa),ymax(xb))
    n=max(1,int(round((y1-y0)/1.0))); yy=np.linspace(y0,y1,n+1)
    for j in range(n):
        ps=[(xa,yy[j]),(xb,yy[j]),(xb,yy[j+1]),(xa,yy[j+1])]
        if inbk((xa+xb)/2,(yy[j]+yy[j+1])/2): continue
        vs=[bm.verts.new((px,py,lz(px,py)+0.05)) for px,py in ps]; bm.faces.new(vs); N+=1
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.002)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
me3=bpy.data.meshes.new('WS135a_BK_S_lot_asphalt_ortho2020_UNVERIFIEDextent'); bm.to_mesh(me3); bm.free(); me3.materials.append(asm)
col.objects.link(bpy.data.objects.new(me3.name,me3)); print('lot faces',N)
# S curb (0.15 m reveal, 0.18 wide)
bm=bmesh.new(); pts=[]
for k in range(len(LS)-1):
    a=np.array(LS[k]); b=np.array(LS[k+1]); L=np.linalg.norm(b-a)
    for s in np.arange(0,L,1.0): pts.append(a+(b-a)*s/L)
pts.append(np.array(LS[-1])); rings=[]
for k,p in enumerate(pts):
    q=pts[min(k+1,len(pts)-1)]-pts[max(k-1,0)]; d=q/np.linalg.norm(q); n=np.array([d[1],-d[0]])  # points S (outward)
    z=lz(p[0],p[1])+0.05
    a=p; b=p-n*0.18
    ring=[bm.verts.new((a[0],a[1],z-0.2)),bm.verts.new((a[0],a[1],z+0.12)),bm.verts.new((b[0],b[1],z+0.12)),bm.verts.new((b[0],b[1],z-0.2))]
    rings.append(ring)
for i in range(len(rings)-1):
    for j in range(3): bm.faces.new((rings[i][j],rings[i+1][j],rings[i+1][j+1],rings[i][j+1]))
bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me4=bpy.data.meshes.new('WS135a_BK_lot_S_curb_ortho2020_UNVERIFIEDreveal'); bm.to_mesh(me4); bm.free(); me4.materials.append(cm)
col.objects.link(bpy.data.objects.new(me4.name,me4))
# stall lines
for xl in (-109.3,-106.5,-103.9,-101.5):
    y0=-274.0; y1=ymin(xl)+0.4
    strip([(xl,y0),(xl,y1)],0.10)
pmesh=bpy.data.meshes.new('WS135a_paint'); pb.normal_update(); pb.to_mesh(pmesh); pb.free()
if pm: pmesh.materials.append(pm)
bm=bmesh.new(); bm.from_mesh(pmesh)
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
bm.to_mesh(pmesh); bm.free()
col.objects.link(bpy.data.objects.new('WS135a_edge_lines_and_stall_lines_paint_ortho2020_UNVERIFIED',pmesh))
# ---- retire old faces
def retire(oname,box,keep=None):
    o=bpy.data.objects.get(oname)
    if not o: return 0
    mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
    dl=[f for f in bm.faces if (lambda c:box[0]<=c.x<=box[1] and box[2]<=c.y<=box[3])(mw@f.calc_center_median())]
    if dl: bmesh.ops.delete(bm,geom=dl,context='FACES'); bm.to_mesh(o.data)
    bm.free(); return len(dl)
print('RETIRED Roads_OSM',retire('Roads_OSM',(-69.2,-61.4,-285,-190.0)))
print('RETIRED UA_Skyline',retire('UA_SkylineWay_south_232846698_UNVERIFIED',(-69.5,-61.0,-285,-262.0)))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

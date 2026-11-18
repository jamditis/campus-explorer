# qw ramp (Nov 3 2026, MAIN). ALL UNVERIFIED, reversible: REVERT=1 removes QW_DTM_north_edge_ramp and restores lifted verts
# exactly from data/qw/lift_backup.npz.
# Problem: the 1 m LiDAR DTM (Terrain_LiDAR_DTM_1m) ends in a straight cut at y=247.8; north of it the coarse 3DEP skirt
# sits 0.7-2.3 m LOWER (probe data/qw/edge_probe.log), so eye-level views NW of Richardson show a grey terrain ledge/curtain.
# Fix: a 30 m smooth ramp sheet from the DTM edge height down onto the skirt (x -30..152, west 10 m taper, faded out within
# 2-7 m of Richardson's footprint so its ground storey is not buried), same skirt material/object space/attributes so the
# lawn shading continues; qs/qt/qw walks + soil strips and qs/qv grass points in the strip are lifted by the same amount.
import bpy, bmesh, os, math, numpy as np, json
from mathutils import Vector, interpolate
REV=os.environ.get('REVERT')=='1'; NAME='QW_DTM_north_edge_ramp_UNVERIFIED'; BK='data/qw/lift_backup.npz'
def restore():
    o=bpy.data.objects.get(NAME)
    if o: me=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.meshes.remove(me)
    if os.path.exists(BK):
        d=np.load(BK,allow_pickle=True); n=0
        for k in d.files:
            ob=bpy.data.objects.get(k)
            if ob and len(ob.data.vertices)*3==d[k].size: ob.data.vertices.foreach_set('co',d[k]); ob.data.update(); n+=1
        print('QW ramp restored',n)
    else: print('QW ramp nothing to restore')
if REV:
    restore()
    if os.environ.get('QWSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
if bpy.data.objects.get(NAME): restore()
dg=bpy.context.evaluated_depsgraph_get()
dtm=bpy.data.objects['Terrain_LiDAR_DTM_1m']; sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
dtme=dtm.evaluated_get(dg); ske=sk.evaluated_get(dg)
def rc(o,e,x,y):
    iw=o.matrix_world.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
    return ((o.matrix_world@r[1]).z,r[3],r[1]) if r[0] else None
YE=247.8; R=30.0; XA,XB=-30.0,152.0
rich=json.load(open('data/qp/rich_poly.json'))['outer']
def pip(x,y,poly):
    ins=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: ins=not ins
    return ins
def pdist(x,y,poly):
    if pip(x,y,poly): return 0.0
    b=1e9
    for i in range(len(poly)):
        (ax,ay),(bx,by)=poly[i],poly[(i+1)%len(poly)]; dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy or 1e-9
        t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/L2)); b=min(b,math.hypot(x-ax-t*dx,y-ay-t*dy))
    return b
def ss(t): t=min(max(t,0),1); return t*t*(3-2*t)
ez={}
for xi in range(int(XA)-1,int(XB)+2):
    h=rc(dtm,dtme,xi,YE-0.1); ez[xi]=h[0] if h else None
def edgez(x):
    a=math.floor(x); b=a+1; za,zb=ez.get(a),ez.get(b)
    if za is None or zb is None: return za if zb is None else zb
    return za+(zb-za)*(x-a)
skd=ske.data; attrs=[a for a in ('ou_edge','ow2_strip') if a in skd.attributes]
def sksample(x,y):
    h=rc(sk,ske,x,y)
    if not h: return None
    z,fi,loc=h; p=skd.polygons[fi]; vs=[skd.vertices[i].co for i in p.vertices]
    w=interpolate.poly_3d_calc(vs,loc); av={}
    for a in attrs:
        dat=skd.attributes[a].data; av[a]=sum(wi*dat[i].value for wi,i in zip(w,p.vertices))
    return z,av
def delta(x,y,skz):
    t=(y-YE)/R
    if t<0 or t>1 or x<XA or x>XB: return 0.0
    ez_=edgez(x)
    if ez_ is None: return 0.0
    if not(XA<=x<=XB): return 0.0
    d0=max(0.0,ez_-sksample_cache_edge(x))
    m=ss((pdist(x,y,rich)-2.0)/5.0)*ss((x-XA)/10.0)
    return d0*(1-ss(t))*m
_ec={}
def sksample_cache_edge(x):
    k=round(x,2)
    if k not in _ec: s=sksample(x,YE+0.05); _ec[k]=s[0] if s else 0
    return _ec[k]
# ---- ramp mesh in skirt local space
iw=sk.matrix_world.inverted(); bm=bmesh.new(); grid={}; vals={}
nx=int(XB-XA)+1; ny=int(R)+1
for i in range(nx):
    x=XA+i
    for j in range(ny):
        y=YE+j*(R/(ny-1))
        s=sksample(x,y)
        if not s: continue
        skz,av=s; d=delta(x,y,skz); t=j/(ny-1)
        z=skz+d-0.03*ss(t*3)  # sinks 3 cm under the skirt once the lift has faded
        if j==0: z=(edgez(x) if d>0 else skz-0.03)-0.008
        grid[i,j]=bm.verts.new(iw@Vector((x,y,z))); vals[i,j]=(d,av)
nf=0
for i in range(nx-1):
    for j in range(ny-1):
        q=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)]
        if not all(k in grid for k in q): continue
        if max(vals[k][0] for k in q)<0.01: continue
        bm.faces.new([grid[k] for k in q]); nf+=1
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if (sk.matrix_world.to_3x3()@f.normal).z<0: f.normal_flip()
me=bpy.data.meshes.new(NAME); bm.to_mesh(me)
# map bm vert -> attribute values
vlist=list(grid.items()); idx={v.index:k for k,v in vlist} if False else None
bm.verts.index_update(); kmap={grid[k].index:k for k in grid}
bm.free()
used=set(v for p in me.polygons for v in p.vertices)
for a in attrs:
    at=me.attributes.new(a,'FLOAT','POINT')
    for vi in range(len(me.vertices)):
        k=kmap.get(vi); at.data[vi].value=vals[k][1].get(a,0.0) if k else 0.0
uv=me.uv_layers.new(name='ortho'); mw=sk.matrix_world
for p in me.polygons:
    for li in p.loop_indices:
        w=mw@me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv=(0.00025*w.x+0.5,0.00025*w.y+0.5)
me.materials.append(sk.material_slots[0].material)
for p in me.polygons: p.use_smooth=True
ob=bpy.data.objects.new(NAME,me); ob.matrix_world=sk.matrix_world.copy()
(sk.users_collection[0]).objects.link(ob)
ob['UNVERIFIED_qw']='smooth 30 m ramp DTM edge->3DEP skirt; real ground shape north of y 247.8 unknown at 1 m (no LiDAR DTM there)'
# drop isolated verts
bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS'); bm.to_mesh(me); bm.free()
print('QW ramp faces',nf,'verts',len(me.vertices))
# ---- lift draped objects
COLS=['QS_Richardson_walks_UNVERIFIED','QT_Richardson_walk_soil_edge_UNVERIFIED','QW_Richardson_walk_ext_UNVERIFIED','QS_Richardson_lawn_grass_20261102qs','QV_Richardson_NW_lawn_grass_20261103qv']
bk={}; st={}
for cn in COLS:
    c=bpy.data.collections.get(cn)
    if not c: continue
    for o in c.all_objects:
        if o.type!='MESH': continue
        me=o.data; mw=o.matrix_world; imw=mw.inverted(); co=np.zeros(len(me.vertices)*3); me.vertices.foreach_get('co',co)
        n=0
        for v in me.vertices:
            w=mw@v.co
            if YE<=w.y<=YE+R and XA<=w.x<=XB:
                s=sksample(w.x,w.y)
                if not s: continue
                d=delta(w.x,w.y,s[0])
                if d>0.002: v.co=imw@Vector((w.x,w.y,w.z+d)); n+=1
        if n: bk[o.name]=co; me.update(); st[o.name]=n
np.savez(BK,**bk); print('QW lifted',st)
if os.environ.get('QWSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

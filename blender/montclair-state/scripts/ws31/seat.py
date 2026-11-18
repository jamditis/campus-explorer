"""ws29: Joe's top priority pass 2 — terrain poking through pavement + cliffs. In BOX: refine terrain to 1 m, pin every terrain vert
that lies under pavement to pavement-3 cm (pavement = ground truth, not moved), then feather the surrounding grass with masked
Laplacian relaxation (pinned verts fixed) and relax any remaining cliff edges; re-drape non-pavement ground cover/trees by dz."""
import bpy, bmesh, numpy as np, os, json, math, re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R='/workspace/nj-scenes/montclair-state'
X0,X1,Y0,Y1=[float(v) for v in os.environ.get('BOX').split(',')]
TAG=os.environ.get('TAG','a'); SL=float(os.environ.get('SLOPE','0.45')); IT=int(os.environ.get('ITER','400')); RAD=float(os.environ.get('RAD','5'))
sc=bpy.context.scene
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=ter.data
assert ter.matrix_world.is_identity or True
def ev_bvh(objs):
    dg=bpy.context.evaluated_depsgraph_get(); dg.update(); bm=bmesh.new()
    for o in objs:
        ev=o.evaluated_get(dg); m=ev.to_mesh()
        t=bmesh.new(); t.from_mesh(m); t.transform(o.matrix_world); tm=bpy.data.meshes.new('t'); t.to_mesh(tm); t.free(); bm.from_mesh(tm); bpy.data.meshes.remove(tm); ev.to_mesh_clear()
    T=BVHTree.FromBMesh(bm); bm.free(); return T
def inbox(o,pad=0):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    return not(max(p.x for p in bb)<X0-pad or min(p.x for p in bb)>X1+pad or max(p.y for p in bb)<Y0-pad or min(p.y for p in bb)>Y1+pad)
pavre=re.compile(r'(footpath|roads_osm|walk|paver|asphalt|slab|crosswalk|carriageway|curb|gutter|apron|sidewalk|pavement|bikepad|plaza_deck|plaza_edge|patio|turnaround|promenade)',re.I)
excl=re.compile(r'(roof|wall|window|tree|grass|bench|rack|sign|lamp|letter|frame|door|glaz|lawn|weed|tuft|pavilion|portico|rail|joint|stain|crack|decal|stripe|line)',re.I)
PAV=[o for o in sc.objects if o.type=='MESH' and not o.hide_render and o.visible_get() and pavre.search(o.name) and not excl.search(o.name) and inbox(o,2)]
PAV=[o for o in PAV if not(os.environ.get('DELROADS')=='1' and o.name=='Roads_OSM')]
print('pavement objs',[o.name[:50] for o in PAV])
OLD=ev_bvh([ter])
bm=bmesh.new(); bm.from_mesh(me)
def boxfaces(): return [f for f in bm.faces if any(X0-1<v.co.x<X1+1 and Y0-1<v.co.y<Y1+1 for v in f.verts)]
def maxedge():
    return max((e.calc_length() for f in boxfaces() for e in f.edges),default=0)
if maxedge()>1.6:
  for axis in (0,1):
    lo,hi=(X0,X1) if axis==0 else (Y0,Y1); k=math.ceil(lo)+0.5
    while k<hi:
        fs=boxfaces(); geom=list({e for f in fs for e in f.edges})+fs+list({v for f in fs for v in f.verts})
        bmesh.ops.bisect_plane(bm,geom=geom,plane_co=(k,0,0) if axis==0 else (0,k,0),plane_no=(1,0,0) if axis==0 else (0,1,0),dist=0.05)
        k+=1.0
  bmesh.ops.triangulate(bm,faces=[f for f in boxfaces() if len(f.verts)>4])
bm.to_mesh(me); bm.free(); me.update()
n=len(me.vertices); co=np.zeros(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
ne=len(me.edges); ed=np.zeros(ne*2,dtype=np.int64); me.edges.foreach_get('vertices',ed); ed=ed.reshape(-1,2)
print('terrain verts',n)
inb=(co[:,0]>X0)&(co[:,0]<X1)&(co[:,1]>Y0)&(co[:,1]<Y1)
frame=(co[:,0]<X0+2)|(co[:,0]>X1-2)|(co[:,1]<Y0+2)|(co[:,1]>Y1-2)
PB=ev_bvh(PAV)
z0=co[:,2].copy(); z=z0.copy(); pin=np.zeros(n,bool); pinned_poke=0
for i in np.nonzero(inb)[0]:
    x,y,zz=co[i]
    h=PB.ray_cast(Vector((x,y,zz+2.0)),Vector((0,0,-1)),4.0)
    if h[0] is None: continue
    pz=h[0].z
    if pz-1.7 < zz < pz+0.6:
        if zz>pz-0.03 or os.environ.get('RAISE')=='1': pinned_poke+=1; z[i]=pz-0.03
        pin[i]=True
pin&=~frame
print('pinned under pavement',int(pin.sum()),'of which lowered/raised to seat',pinned_poke)
a,b=ed[:,0],ed[:,1]; L=np.linalg.norm(co[a,:2]-co[b,:2],axis=1)+1e-6
def steepmask(zv):
    s=np.abs(zv[a]-zv[b])/L; st=(s>SL)&inb[a]&inb[b]&(L>0.05)&~(pin[a]&pin[b]); return st,s
st,s0=steepmask(z)
mid=(co[a[st],:2]+co[b[st],:2])/2
mask=np.zeros(n,bool)
if len(mid):
    kd=KDTree(len(mid))
    for i,m in enumerate(mid): kd.insert((m[0],m[1],0),i)
    kd.balance()
    for i in np.nonzero(inb)[0]:
        if kd.find((co[i,0],co[i,1],0))[2]<RAD: mask[i]=True
if os.environ.get('RAISE')=='1':
    pk=KDTree(int(pin.sum()))
    for j,i in enumerate(np.nonzero(pin)[0]): pk.insert((co[i,0],co[i,1],0),j)
    pk.balance()
    for i in np.nonzero(inb&~pin)[0]:
        if pk.find((co[i,0],co[i,1],0))[2]<float(os.environ.get('PRAD','4')): mask[i]=True
mask&=~frame&~pin
print('steep edges',int(st.sum()),'relax verts',int(mask.sum()))
W=1.0/L
for it in range(IT):
    sm=np.bincount(a,weights=z[b]*W,minlength=n)+np.bincount(b,weights=z[a]*W,minlength=n)
    ws=np.bincount(a,weights=W,minlength=n)+np.bincount(b,weights=W,minlength=n)
    z=np.where(mask,0.3*z+0.7*sm/np.maximum(ws,1e-9),z)
sel=inb[a]&inb[b]&(L>0.05)&~(pin[a]&pin[b])
s1=np.abs(z[a]-z[b])/L
print('grass-edge slope p99 %.2f -> %.2f, max %.2f -> %.2f; |dz| max %.2f'%(np.percentile(s0[sel],99),np.percentile(s1[sel],99),s0[sel].max(),s1[sel].max(),np.abs(z-z0).max()))
co[:,2]=z; me.vertices.foreach_set('co',co.ravel()); me.update()
NEW=ev_bvh([ter])
def zat(t,x,y):
    h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return h[0].z if h[0] else None
moved={}; whole=[]; pavset=set(PAV)
for o in list(sc.objects):
    if o==ter or o in pavset or o.type!='MESH' or o.library or (o.data and o.data.library) or not inbox(o): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; h=max(p.z for p in bb)-min(p.z for p in bb)
    if o.name.startswith('T_') or (h>3 and o.data.users>1):
        loc=o.matrix_world.translation
        if X0<loc.x<X1 and Y0<loc.y<Y1:
            zo,zn=zat(OLD,loc.x,loc.y),zat(NEW,loc.x,loc.y)
            if zo is not None and zn is not None and abs(zn-zo)>0.005 and abs(loc.z-zo)<1.0: o.location.z+=zn-zo; whole.append((o.name,round(zn-zo,2)))
        continue
    if o.data.users>1 or h>3 or re.search(r'(rail|step|stair|bollard|post|planter|bench|sign|Morehead|School of|CCOM_|dd_|NW 1F|Downspout|entrance|sill|pilaster|door|landing|moulding|wall)',o.name,re.I): continue
    mw=o.matrix_world; inv=mw.inverted(); cnt=0
    for v in o.data.vertices:
        p=mw@v.co
        if not(X0<p.x<X1 and Y0<p.y<Y1): continue
        zo=zat(OLD,p.x,p.y); zn=zat(NEW,p.x,p.y)
        if zo is None or zn is None or abs(zn-zo)<0.003: continue
        if -0.3<p.z-zo<0.4: v.co=inv@Vector((p.x,p.y,p.z+zn-zo)); cnt+=1
    if cnt: o.data.update(); moved[o.name]=cnt
print('draped moved',sorted(moved.items(),key=lambda k:-k[1])[:20]); print('whole',whole[:20],len(whole))
# verify poke
left=0;tot=0
for x in np.arange(X0+2,X1-2,0.5):
    for y in np.arange(Y0+2,Y1-2,0.5):
        h=PB.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),400)
        if h[0] is None: continue
        zt=zat(NEW,x,y); tot+=1
        if zt is not None and h[0].z-0.015<zt<h[0].z+0.8: left+=1
print('pavement samples',tot,'terrain within 1.5 cm or above',left)
os.makedirs(R+'/data/ws31',exist_ok=True); json.dump({'moved':moved,'whole':whole},open(R+f'/data/ws31/seat_{TAG}.json','w'))

if os.environ.get('DELROADS')=='1':
    o=bpy.data.objects['Roads_OSM']; mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data); kill=[]
    for f in bm.faces:
        ps=[mw@v.co for v in f.verts]
        if not all(X0<p.x<X1 and Y0<p.y<Y1 for p in ps): continue
        for p in ps:
            zt=zat(NEW,p.x,p.y)
            if zt is not None and p.z-zt>0.02: kill.append(f); break
    bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update(); print('Roads_OSM faces removed',len(kill))

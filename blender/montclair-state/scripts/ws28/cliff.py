"""ws28: Joe's 11:57 top priority — soften LiDAR-mesh terrain cliffs (1.5–2.5 m steps over ~1 m) on College Ave south of Kasser
(the flat pad y<-137 with cliffs on its N and E sides) by masked Laplacian relaxation of the base terrain mesh, then re-seat every
ground-draped mesh vertex (road, curbs, walks, lawn, grass points) by the same dz and move small resting objects/trees whole."""
import bpy, bmesh, numpy as np, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'
X0,X1,Y0,Y1=[float(v) for v in os.environ.get('BOX','-249,-176,-168,-112').split(',')]
SL=float(os.environ.get('SLOPE','0.45')); IT=int(os.environ.get('ITER','160'))
sc=bpy.context.scene
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=ter.data
print('terrain data users',me.users)
def tbvh():
    dg=bpy.context.evaluated_depsgraph_get(); dg.update()
    ev=ter.evaluated_get(dg); m=ev.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(ter.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); ev.to_mesh_clear(); return t
OLD=tbvh()
# 1) refine: bisect the coarse pad/cliff triangles in the box on a 1 m grid (conforming, no cracks)
bm=bmesh.new(); bm.from_mesh(me)
def boxfaces(): return [f for f in bm.faces if any(X0-1<v.co.x<X1+1 and Y0-1<v.co.y<Y1+1 for v in f.verts)]
STEP=float(os.environ.get('STEP','1.0'))
import math
for axis in (0,1):
    lo,hi=(X0,X1) if axis==0 else (Y0,Y1)
    k=math.ceil(lo)+0.5
    while k<hi:
        fs=boxfaces(); geom=list({e for f in fs for e in f.edges})+fs+list({v for f in fs for v in f.verts})
        bmesh.ops.bisect_plane(bm,geom=geom,plane_co=(k,0,0) if axis==0 else (0,k,0),plane_no=(1,0,0) if axis==0 else (0,1,0))
        k+=STEP
bmesh.ops.triangulate(bm,faces=[f for f in boxfaces() if len(f.verts)>4])
bm.to_mesh(me); bm.free(); me.update()
n=len(me.vertices); co=np.zeros(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
ne=len(me.edges); ed=np.zeros(ne*2,dtype=np.int64); me.edges.foreach_get('vertices',ed); ed=ed.reshape(-1,2)
print('terrain verts after refine',n)
inb=(co[:,0]>X0)&(co[:,0]<X1)&(co[:,1]>Y0)&(co[:,1]<Y1)
a,b=ed[:,0],ed[:,1]
L=np.linalg.norm(co[a,:2]-co[b,:2],axis=1)+1e-6
s=np.abs(co[a,2]-co[b,2])/L
steep=(s>SL)&inb[a]&inb[b]&(L>0.05)
from mathutils.kdtree import KDTree
mid=(co[a[steep],:2]+co[b[steep],:2])/2
kd=KDTree(len(mid))
for i,m in enumerate(mid): kd.insert((m[0],m[1],0),i)
kd.balance()
RAD=float(os.environ.get('RAD','5.0'))
mask=np.zeros(n,bool)
for i in np.nonzero(inb)[0]:
    if kd.find((co[i,0],co[i,1],0))[2]<RAD: mask[i]=True
frame=(co[:,0]<X0+2)|(co[:,0]>X1-2)|(co[:,1]<Y0+2)|(co[:,1]>Y1-2)
mask&=~frame
print('steep edges',int(steep.sum()),'relax verts',int(mask.sum()))
z=co[:,2].copy(); z0=z.copy()
W=1.0/L
for it in range(IT):
    sm=np.bincount(a,weights=z[b]*W,minlength=n)+np.bincount(b,weights=z[a]*W,minlength=n)
    ws=np.bincount(a,weights=W,minlength=n)+np.bincount(b,weights=W,minlength=n)
    avg=sm/np.maximum(ws,1e-9)
    z=np.where(mask,0.3*z+0.7*avg,z)
s2=np.abs(z[a]-z[b])/L
sel=inb[a]&inb[b]&(L>0.05)
print('max slope in box before %.2f after %.2f; p99 before %.2f after %.2f; |dz| max %.2f'%(s[sel].max(),s2[sel].max(),np.percentile(s[sel],99),np.percentile(s2[sel],99),np.abs(z-z0).max()))
co[:,2]=z; me.vertices.foreach_set('co',co.ravel()); me.update()
NEW=tbvh()
def zat(t,x,y):
    h=t.ray_cast(Vector((x,y,190)),Vector((0,0,-1))); return h[0].z if h[0] else None
def dzat(x,y):
    if not(X0<x<X1 and Y0<y<Y1): return 0.0
    zo=zat(OLD,x,y); zn=zat(NEW,x,y)
    return (zn-zo) if (zo is not None and zn is not None) else 0.0, zo
# 2a) refine coarse draped pavement ribbons in the box so they bend with the new grade instead of folding
for nmn in ('Footpaths_OSM','Roads_OSM'):
    o=bpy.data.objects.get(nmn)
    if not o or o.data.users>1: continue
    mw=o.matrix_world; inv=mw.inverted(); bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(mw)
    def bf(): return [f for f in bm.faces if any(X0<v.co.x<X1 and Y0<v.co.y<Y1 for v in f.verts)]
    nf0=len(bm.faces)
    for axis in (0,1):
        lo,hi=(X0,X1) if axis==0 else (Y0,Y1); k=math.ceil(lo)+0.25
        while k<hi:
            fs=bf()
            if fs:
                geom=list({e for f in fs for e in f.edges})+fs+list({v for f in fs for v in f.verts})
                bmesh.ops.bisect_plane(bm,geom=geom,plane_co=(k,0,0) if axis==0 else (0,k,0),plane_no=(1,0,0) if axis==0 else (0,1,0))
            k+=1.0
    bm.transform(inv); bm.to_mesh(o.data); bm.free(); o.data.update(); print('refined',nmn,nf0,'->',len(o.data.polygons))
moved={}; whole=[]
for o in list(sc.objects):
    if o==ter or o.type!='MESH' or o.library or (o.data and o.data.library): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(p.x for p in bb)<X0 or min(p.x for p in bb)>X1 or max(p.y for p in bb)<Y0 or min(p.y for p in bb)>Y1: continue
    h=max(p.z for p in bb)-min(p.z for p in bb)
    if o.name.startswith('T_') or (h>3 and o.data.users>1):
        loc=o.matrix_world.translation; r=dzat(loc.x,loc.y)
        d=r[0] if isinstance(r,tuple) else 0
        if abs(d)>0.005: o.location.z+=d; whole.append((o.name,round(d,2)))
        continue
    if o.data.users>1: continue
    mw=o.matrix_world; inv=mw.inverted(); cnt=0
    for v in o.data.vertices:
        p=mw@v.co
        r=dzat(p.x,p.y)
        if not isinstance(r,tuple): continue
        d,zo=r
        if zo is None or abs(d)<0.003: continue
        if -0.5< p.z-zo <0.6:
            v.co=inv@Vector((p.x,p.y,p.z+d)); cnt+=1
    if cnt: o.data.update(); moved[o.name]=cnt
print('draped verts moved',sorted(moved.items(),key=lambda k:-k[1])[:25])
print('whole objects moved',whole[:30],len(whole))
json.dump({'moved':moved,'whole':whole},open(R+'/data/ws28/cliff_moved.json','w'))
# 3) pavement seat: no terrain poking through pavement in the box (terrain kept >=3 cm under pavement tops)
PAV=[o for o in sc.objects if o.type=='MESH' and (o.name.startswith('WS27_CollegeAve') or o.name in('Footpaths_OSM','Roads_OSM'))]
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
bm=bmesh.new()
for o in PAV:
    ev=o.evaluated_get(dg); m=ev.to_mesh(); t=bmesh.new(); t.from_mesh(m); t.transform(o.matrix_world)
    tm=bpy.data.meshes.new('tmp'); t.to_mesh(tm); t.free(); bm.from_mesh(tm); bpy.data.meshes.remove(tm); ev.to_mesh_clear()
PB=BVHTree.FromBMesh(bm); bm.free()
co=np.zeros(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); low=0
for i in np.nonzero((co[:,0]>X0)&(co[:,0]<X1)&(co[:,1]>Y0)&(co[:,1]<Y1))[0]:
    x,y,zz=co[i]
    h=PB.ray_cast(Vector((x,y,zz+1.0)),Vector((0,0,-1)),3.0)
    if h[0] and h[0].z<zz+1.0 and zz>h[0].z-0.03 and zz<h[0].z+0.6:
        co[i,2]=h[0].z-0.03; low+=1
me.vertices.foreach_set('co',co.ravel()); me.update(); print('terrain verts seated under pavement',low)

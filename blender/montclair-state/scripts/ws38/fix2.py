# ws38: (1) Red Hawk statue turned to face College Ave head-on (perpendicular to the road axis at the statue)
#       (2) flatten the wavy walk/grass at the foot of the WS35 Kasser steps into one smooth plane
import bpy,bmesh,math,os
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects.get(n)
    if not o: print('W38 missing',n); return None
    e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
    t=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return t
CARR='WS27_CollegeAve_carriageway_2020ortho'
TC=bvh(CARR); TW=bvh('Footpaths_OSM'); TT0=bvh('Terrain_LiDAR_DTM_1m')
def zz(t,x,y):
    if not t: return None
    r=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return r[0].z if r[0] else None
# ---- 1. hawk facing ----
st=[o for o in bpy.data.objects if 'RedHawk' in o.name and ('statue_bronze' in o.name or 'plinth' in o.name)]
S=st[0].matrix_world.translation.copy(); print('W38 statue at',[round(v,2) for v in S],[o.name for o in st])
# road centreline from carriageway extents per y
cl=[]
for yi in range(int(S.y)-30,int(S.y)+31,2):
    xs=[x*0.5 for x in range(int((S.x-60)*2),int((S.x+60)*2)) if zz(TC,x*0.5,yi) is not None]
    if xs: cl.append(Vector(((min(xs)+max(xs))/2,yi,0)))
print('W38 centreline pts',len(cl),[(round(p.x,1),p.y) for p in cl[::5]])
best=None
for a,b in zip(cl,cl[1:]):
    ab=b-a; s=Vector((S.x,S.y,0))
    t=max(0,min(1,(s-a).dot(ab)/ab.length_squared)); q=a+ab*t; d=(q-s).length
    if best is None or d<best[0]: best=(d,q,ab.normalized())
d,q,tan=best
f=(q-Vector((S.x,S.y,0))); f.z=0; f.normalize()
# make exactly perpendicular to local road tangent, pointing at the road
perp=Vector((-tan.y,tan.x,0))
if perp.dot(f)<0: perp=-perp
yaw=math.atan2(-perp.x,perp.y)
print('W38 road dist %.1f tangent (%.3f,%.3f) facing (%.3f,%.3f) yaw %.1f deg'%(d,tan.x,tan.y,perp.x,perp.y,math.degrees(yaw)))
for o in st:
    o.matrix_world=Matrix.Translation(o.matrix_world.translation)@Matrix.Rotation(yaw,4,'Z')
    o.name=o.name.replace('_pos_UNVERIFIED','')
    if 'statue_bronze' in o.name and 'facesCollegeAve' not in o.name: o.name=o.name+'_facesCollegeAve_ws38'
# ---- 1b. swap in hawk pass-3 mesh ----
with bpy.data.libraries.load('/workspace/nj-scenes/assets/redhawk_statue_v3_ws38.blend',link=False) as (fd,td): td.meshes=['RedHawk_bronze_v3_ws38']
nm=td.meshes[0]
for o in st:
    if 'statue_bronze' in o.name:
        old=o.data; o.data=nm; o.modifiers.clear(); o.modifiers.new('wn','WEIGHTED_NORMAL'); print('W38 hawk mesh swapped',len(nm.vertices),'old',old.name)
# ---- 2. step-foot flatten (low-pass, keeps the real slope; protects the bottom tread line) ----
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=T.matrix_world; ti=tm.inverted()
X0,X1,Y0,Y1=-213.0,-202.2,-100.0,-84.0
FE=2.5
from mathutils.kdtree import KDTree
P=[tm@v.co for v in T.data.vertices]
idx=[i for i,p in enumerate(P) if X0-FE-4<p.x<X1+FE+4 and Y0-FE-4<p.y<Y1+FE+4]
kd=KDTree(len(idx))
for j,i in enumerate(idx): kd.insert(P[i],j)
kd.balance()
Z={i:P[i].z for i in idx}
for it in range(3):
    NZ={}
    for i in idx:
        p=P[i]; sw=sz_=0
        for co,j,d in kd.find_range(Vector((p.x,p.y,p.z)),6.0):
            q=P[idx[j]]; dd=math.hypot(q.x-p.x,q.y-p.y)
            if dd>3.0: continue
            ww=math.exp(-(dd*dd)/(2*1.4*1.4)); sw+=ww; sz_+=ww*Z[idx[j]]
        NZ[i]=sz_/sw
    Z=NZ
def plane(x,y): return None
def w(x,y):
    dx=max(X0-x,0,x-X1); dy=max(Y0-y,0,y-Y1); dd=math.hypot(dx,dy)
    if dd>=FE: return 0.0
    t=1-dd/FE; return t*t*(3-2*t)
SM=Z
moved=0; mx=0
for v in T.data.vertices:
    p=tm@v.co
    k=w(p.x,p.y)
    if k<=0: continue
    if zz(TC,p.x,p.y) is not None: continue          # keep ws37 road seating
    nz=p.z+(SM[v.index]-p.z)*k if v.index in SM else p.z
    nz=max(p.z-0.25,min(p.z+0.25,nz))
    if p.x>-202.6: nz=min(nz,p.z)   # never bury the bottom tread
    # never rise above an adjacent road edge (ws37 rule)
    nb=[zz(TC,p.x+dx,p.y+dy) for dx,dy in ((0.6,0),(-0.6,0),(0,0.6),(0,-0.6))]
    nb=[z for z in nb if z is not None]
    if nb: nz=min(nz,min(nb)-0.02)
    if abs(nz-p.z)>0.003: mx=max(mx,abs(nz-p.z)); v.co=ti@Vector((p.x,p.y,nz)); moved+=1
T.data.update(); print('W38 terrain verts moved',moved,'max',round(mx,3))
# reseat loose grass/lawn meshes in zone by the terrain delta
dg.update(); TT1=bvh('Terrain_LiDAR_DTM_1m'); gm=0
for o in list(bpy.data.objects):
    if o.type!='MESH' or o.library or not any(k in o.name.lower() for k in ('grass','lawn')): continue
    m=o.matrix_world; ob=[m@Vector(cc) for cc in o.bound_box]
    if max(qq.x for qq in ob)<X0-FE or min(qq.x for qq in ob)>X1+FE or max(qq.y for qq in ob)<Y0-FE or min(qq.y for qq in ob)>Y1+FE: continue
    if len(o.data.vertices)>300000: print('W38 skip big',o.name); continue
    mi=m.inverted(); cnt=0
    for vv in o.data.vertices:
        p=m@vv.co
        if w(p.x,p.y)<=0: continue
        a0=zz(TT0,p.x,p.y); a1=zz(TT1,p.x,p.y)
        if a0 is None or a1 is None or abs(a1-a0)<0.003: continue
        vv.co=mi@Vector((p.x,p.y,p.z+a1-a0)); cnt+=1
    if cnt: o.data.update(); gm+=cnt; print('W38 grass reseat',o.name,cnt)
# report walk heights after re-drape along 3 lines
dg.update(); TW1=bvh('Footpaths_OSM')
for y in (-96,-92,-88):
    r0=[zz(TW,x,y) for x in range(-212,-200)]; r1=[zz(TW1,x,y) for x in range(-212,-200)]
    print('W38 walk y',y,'before',[round(z,2) if z else None for z in r0]); print('W38 walk y',y,'after ',[round(z,2) if z else None for z in r1])
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('W38 SAVED')

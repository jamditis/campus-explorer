# ws39: (1) clean concrete landing at the foot of the WS35 Kasser steps (kills the wavy road-sliver/curb/terrain band Joe saw)
#       (2) hawk pass 4: broad-faced raised wings (asset redhawk_statue_v4_ws39.blend)
import bpy,bmesh,math,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects.get(n); e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
    t=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return t
def zz(t,x,y):
    r=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return r[0].z if r[0] else None
ST=bpy.data.objects['WS35_Kasser_terrace_steps_concrete_5risers_UNVERIFIED']
CW=bpy.data.objects['WS35_Kasser_steps_cheek_walls_UNVERIFIED']
SV=[ST.matrix_world@v.co for v in ST.data.vertices]; CV=[CW.matrix_world@v.co for v in CW.data.vertices]
XF=min(p.x for p in SV)
YS0=min(p.y for p in SV+CV); YS1=max(p.y for p in SV+CV)
print('W39 steps foot x %.2f y %.2f..%.2f'%(XF,YS0,YS1))
# landing height z(y): ground just in front of the foot, kept >=0.10 below the bottom nosing
TG=bvh('Terrain_LiDAR_DTM_1m')
foot=[p for p in SV if p.x<XF+0.06]
nos={}
for p in foot: k=round(p.y*2)/2; nos[k]=max(nos.get(k,-1e9),p.z)
bins={}
for k in sorted(nos):
    g=zz(TG,XF-0.4,k)
    if g is None: continue
    bins[k]=min(g,nos[k]-0.10)
ys=sorted(bins); print('W39 foot nosing/ground',[(y,round(nos[y],2),round(bins[y],2)) for y in ys][::3])
n=len(ys); my=sum(ys)/n; mz=sum(bins[y] for y in ys)/n
b=sum((y-my)*(bins[y]-mz) for y in ys)/max(1e-6,sum((y-my)**2 for y in ys)); a=mz-b*my
print('W39 base fit z = %.3f + %.4f*y  (residual max %.3f)'%(a,b,max(abs(bins[y]-(a+b*y)) for y in ys)))
assert 120<a+b*my<135, 'bad landing height'
PW=2.3; X0=XF-PW; X1=XF+0.08; Y0=YS0-0.5; Y1=YS1+0.5
def ptop(x,y): return a+b*y+0.004-0.012*(X1-x)/PW     # ~0.5% cross fall away from the steps
# ---- landing slab ----
bm=bmesh.new(); NY=int((Y1-Y0)/0.5)+1; NX=4
top=[[bm.verts.new((X0+(X1-X0)*i/NX, Y0+(Y1-Y0)*j/(NY-1), 0)) for i in range(NX+1)] for j in range(NY)]
for j in range(NY):
    for i in range(NX+1):
        v=top[j][i]; v.co.z=ptop(v.co.x,v.co.y)
for j in range(NY-1):
    for i in range(NX): bm.faces.new((top[j][i],top[j][i+1],top[j+1][i+1],top[j+1][i]))
ring=[top[0][i] for i in range(NX+1)]+[top[j][NX] for j in range(1,NY)]+[top[NY-1][i] for i in range(NX-1,-1,-1)]+[top[j][0] for j in range(NY-2,0,-1)]
low=[bm.verts.new((v.co.x,v.co.y,v.co.z-0.30)) for v in ring]
for k in range(len(ring)):
    k2=(k+1)%len(ring)
    try: bm.faces.new((ring[k2],ring[k],low[k],low[k2]))
    except Exception: pass
bm.normal_update()
for f in bm.faces:
    if f.normal.z<-0.5: f.normal_flip()
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me=bpy.data.meshes.new('WS39_Kasser_steps_foot_landing'); bm.to_mesh(me); bm.free()
pad=bpy.data.objects.new('WS39_Kasser_steps_foot_landing_concrete_UNVERIFIED',me)
ST.users_collection[0].objects.link(pad)
mat=bpy.data.materials.get('WS3_Concrete_panels_sawcut') or bpy.data.materials.get('WS35_concrete_steps')
me.materials.append(mat)
for p in me.polygons: p.use_smooth=False
print('W39 landing x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f mat %s'%(X0,X1,Y0,Y1,ptop(X0,Y0),ptop(X1,Y1),mat.name))
def inpad(x,y,m=0.0): return X0-m<x<X1+m and Y0-m<y<Y1+m
# ---- push everything that wobbles at the step foot under the landing ----
TT0=bvh('Terrain_LiDAR_DTM_1m'); TC=bvh('WS27_CollegeAve_carriageway_2020ortho')
for name,clear in (('WS27_CollegeAve_carriageway_2020ortho',0.07),('WS27_CollegeAve_curb_right_UNVERIFIED',0.05),('WS27_CollegeAve_curb_left_UNVERIFIED',0.05)):
    o=bpy.data.objects[name]; m=o.matrix_world; mi=m.inverted(); c=0
    for v in o.data.vertices:
        p=m@v.co
        if inpad(p.x,p.y,0.02) and p.z>ptop(p.x,p.y)-clear:
            v.co=mi@Vector((p.x,p.y,ptop(p.x,p.y)-clear)); c+=1
    o.data.update(); print('W39 tucked',name,c)
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=T.matrix_world; ti=tm.inverted(); FE=2.2; moved=0; mx=0
for v in T.data.vertices:
    p=tm@v.co
    if not (X0-FE-1<p.x<X1+1 and Y0-FE-1<p.y<Y1+FE+1): continue
    if inpad(p.x,p.y,0.05):
        nz=min(p.z,ptop(p.x,p.y)-0.10)
    else:
        if p.x>X1: continue                                  # never touch under the deck/steps side
        if zz(TC,p.x,p.y) is not None: continue              # keep road seating (ws37)
        dx=max(X0-p.x,0,p.x-X1); dy=max(Y0-p.y,0,p.y-Y1); d=math.hypot(dx,dy)
        if d>=FE: continue
        t=1-d/FE; w=t*t*(3-2*t)
        xe=min(max(p.x,X0),X1); ye=min(max(p.y,Y0),Y1); tz=ptop(xe,ye)-0.015
        nz=p.z+(tz-p.z)*w; nz=max(p.z-0.20,min(p.z+0.20,nz))
    if abs(nz-p.z)>0.003: mx=max(mx,abs(nz-p.z)); v.co=ti@Vector((p.x,p.y,nz)); moved+=1
T.data.update(); print('W39 terrain verts moved',moved,'max',round(mx,3))
dg.update(); TT1=bvh('Terrain_LiDAR_DTM_1m'); 
for o in list(bpy.data.objects):
    if o.type!='MESH' or o.library or not any(k in o.name.lower() for k in ('grass','lawn')): continue
    m=o.matrix_world; ob=[m@Vector(cc) for cc in o.bound_box]
    if max(q.x for q in ob)<X0-FE or min(q.x for q in ob)>X1 or max(q.y for q in ob)<Y0-FE or min(q.y for q in ob)>Y1+FE: continue
    if len(o.data.vertices)>300000: print('W39 skip big',o.name); continue
    mi=m.inverted(); cnt=0
    for vv in o.data.vertices:
        p=m@vv.co
        if not (X0-FE<p.x<X1 and Y0-FE<p.y<Y1+FE): continue
        a0=zz(TT0,p.x,p.y); a1=zz(TT1,p.x,p.y)
        if a0 is None or a1 is None or abs(a1-a0)<0.003: continue
        vv.co=mi@Vector((p.x,p.y,p.z+a1-a0)); cnt+=1
    if cnt: o.data.update(); print('W39 grass reseat',o.name,cnt)
# ---- hawk pass 4 ----
hp='/workspace/nj-scenes/assets/redhawk_statue_v4_ws39.blend'
if os.path.exists(hp):
    with bpy.data.libraries.load(hp,link=False) as (fd,td): td.meshes=['RedHawk_bronze_v4_ws39']
    nm=td.meshes[0]
    for o in bpy.data.objects:
        if 'RedHawk' in o.name and 'statue_bronze' in o.name:
            old=o.data.name; mats=[s.material for s in o.material_slots]
            o.data=nm; print('W39 hawk mesh v4 ->',o.name,len(nm.vertices),'old',old)
# report profile across the foot after
dg.update(); TA=bvh('Terrain_LiDAR_DTM_1m')
for y in (-96,-92,-88):
    print('W39 y',y,'terrain',[round(zz(TA,x*0.5,y),2) for x in range(-412,-400)],'pad',round(ptop(XF-1,y),2))
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('W39 SAVED')

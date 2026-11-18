# ws39b: smooth the longitudinal profile of the WS27 College Ave ribbon (carriageway + both curbs) by the Kasser terrace,
# so the road stops undulating; then keep terrain under the road (ws37 rule)
import bpy,bmesh,math,os
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
Y0,Y1=-140,-40; CAP=0.15; R=5.0; SIG=2.0
C=bpy.data.objects['WS27_CollegeAve_carriageway_2020ortho']; cm=C.matrix_world; ci=cm.inverted()
P=[cm@v.co for v in C.data.vertices]
def inpad(x,y): return -203.2<x<-200.6 and -97.8<y<-86.5   # ws39 landing: keep tucked
idx=[i for i,p in enumerate(P) if Y0-8<p.y<Y1+8 and not inpad(p.x,p.y)]
kd=KDTree(len(idx))
for j,i in enumerate(idx): kd.insert(Vector((P[i].x,P[i].y,0)),j)
kd.balance()
def smooth_at(x,y):
    sw=sz=0
    for co,j,d in kd.find_range(Vector((x,y,0)),R):
        w=math.exp(-d*d/(2*SIG*SIG)); sw+=w; sz+=w*P[idx[j]].z
    return sz/sw if sw else None
def wy(y):
    d=max(Y0-y,0,y-Y1); t=max(0,1-d/6); return t*t*(3-2*t)
# dry stats + apply to carriageway
D={}
for i in idx:
    p=P[i]; s=smooth_at(p.x,p.y); 
    if s is None: continue
    dz=max(-CAP,min(CAP,(s-p.z)))*wy(p.y); D[i]=dz
mx=max(abs(v) for v in D.values()); print('W39R carriageway verts',len(D),'max dz',round(mx,3),'>5cm',sum(1 for v in D.values() if abs(v)>0.05))
for i,dz in D.items():
    C.data.vertices[i].co=ci@(P[i]+Vector((0,0,dz)))
C.data.update()
# curbs follow the carriageway delta at their nearest carriageway point
kdc=KDTree(len(D)); keys=list(D)
for j,i in enumerate(keys): kdc.insert(Vector((P[i].x,P[i].y,0)),j)
kdc.balance()
for n in ('WS27_CollegeAve_curb_left_UNVERIFIED','WS27_CollegeAve_curb_right_UNVERIFIED'):
    o=bpy.data.objects[n]; m=o.matrix_world; mi=m.inverted(); c=0
    for v in o.data.vertices:
        p=m@v.co
        if not (Y0-8<p.y<Y1+8) or inpad(p.x,p.y): continue
        res=kdc.find_n(Vector((p.x,p.y,0)),3)
        if not res: continue
        sw=sum(1/(d+0.1) for _,_,d in res); dz=sum(D[keys[j]]/(d+0.1) for _,j,d in res)/sw
        if abs(dz)>0.002: v.co=mi@(p+Vector((0,0,dz))); c+=1
    o.data.update(); print('W39R curb',n,c)
# terrain stays >=6 cm under the road surface
dg.update()
e=C.evaluated_get(dg); me=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(me); bm.transform(cm); TC=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=T.matrix_world; ti=tm.inverted(); c=0
for v in T.data.vertices:
    p=tm@v.co
    if not (Y0-8<p.y<Y1+8 and -240<p.x<-180): continue
    r=TC.ray_cast(Vector((p.x,p.y,300)),Vector((0,0,-1)))
    if r[0] is not None and p.z>r[0].z-0.06: v.co=ti@Vector((p.x,p.y,r[0].z-0.06)); c+=1
T.data.update(); print('W39R terrain lowered under road',c)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('W39R SAVED')

# ws34: WS27 College Ave curb backs lay as wide grey wedges on the grass (Kasser front). Grade terrain behind both curbs up to
# curb top -3 cm within 0.35 m, falling 1:3 out to 1.6 m; skip verts under road/curb/walk/deck. Grass reseated.
import bpy,bmesh,os
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=map(float,os.environ.get('BOX','-236,-164,-120,-40').split(','))
dg=bpy.context.evaluated_depsgraph_get()
def bvh(name):
    o=bpy.data.objects.get(name)
    if not o: return None
    e=o.evaluated_get(dg); m=e.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(o.matrix_world)
    return BVHTree.FromBMesh(b),b
curbs=[bvh('WS27_CollegeAve_curb_right_UNVERIFIED'),bvh('WS27_CollegeAve_curb_left_UNVERIFIED')]
pts=[v.co.copy() for t,b in curbs for v in b.verts if X0-2<v.co.x<X1+2 and Y0-2<v.co.y<Y1+2]
kd=kdtree.KDTree(len(pts))
for i,p in enumerate(pts): kd.insert(Vector((p.x,p.y,0)),i)
kd.balance()
cover=[x for x in [bvh(n) for n in ('WS27_CollegeAve_carriageway_2020ortho','Roads_OSM','Footpaths_OSM','COLE_plaza_deck_bs','COLE_plaza_edge_bs','COLE_plaza_west_steps_bu')] if x]+curbs
def covered(x,y):
    for t,_ in cover:
        if t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0] is not None: return True
    return False
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=T.matrix_world; ti=tm.inverted(); n=0; mx=0
for v in T.data.vertices:
    p=tm@v.co
    if not(X0<p.x<X1 and Y0<p.y<Y1): continue
    near=kd.find_range(Vector((p.x,p.y,0)),1.6)
    if not near or covered(p.x,p.y): continue
    best=None
    for co,i,d in near:
        t=pts[i].z-0.03-max(0.0,d-0.35)/3.0
        if best is None or t>best: best=t
    if best>p.z+0.015 and best-p.z<0.6:
        v.co=ti@Vector((p.x,p.y,best)); n+=1; mx=max(mx,best-p.z)
T.data.update(); print('curb-back terrain raised',n,'max',round(mx,2))
dg.update(); te=T.evaluated_get(dg)
def tz(x,y):
    ok,hp,_,_=te.ray_cast(ti@Vector((x,y,300)),(ti.to_3x3()@Vector((0,0,-1))).normalized())
    return (tm@hp).z if ok else None
for o in [o for o in bpy.data.objects if o.type=='MESH' and ('grass' in o.name.lower() or 'lawn' in o.name.lower()) and len(o.data.polygons)==0]:
    m=o.matrix_world; mi=m.inverted(); k=0
    for v in o.data.vertices:
        p=m@v.co
        if not(X0<p.x<X1 and Y0<p.y<Y1): continue
        z=tz(p.x,p.y)
        if z is not None and 0.02<z-p.z<0.7: v.co=mi@Vector((p.x,p.y,z)); k+=1
    if k: o.data.update(); print('grass reseated',o.name,k)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)

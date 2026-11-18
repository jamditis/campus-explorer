# ws32 fix2: the apron's east edge stood ~0.9 m over the LiDAR ground (black cliff band in CCOM's shadow).
# Raise terrain east/south-east of the apron into a ~22% grassed embankment from the apron edge down to the LiDAR grade.
import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
D=Vector((0,0,-1))
def bvh(n):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(o.matrix_world); e.to_mesh_clear(); return b
ab=bvh('CCOM_dock_apron_20261014jf3'); AP=BVHTree.FromBMesh(ab)
bd=[v.co.copy() for v in ab.verts if v.is_boundary]; ab.free()
kd=KDTree(len(bd))
for i,c in enumerate(bd): kd.insert(Vector((c.x,c.y,0)),i)
kd.balance()
PAV=[]
for n in ('Footpaths_OSM','Roads_OSM'):
    b=bvh(n); PAV.append(BVHTree.FromBMesh(b)); b.free()
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tw=ter.matrix_world; ti=tw.inverted(); k=0; mx=0
for v in ter.data.vertices:
    p=tw@v.co
    if not(9<p.x<24 and -44<p.y<-22): continue
    if AP.ray_cast(Vector((p.x,p.y,p.z+5)),D,10)[0] is not None: continue
    if any(t.ray_cast(Vector((p.x,p.y,p.z+5)),D,10)[0] is not None for t in PAV): continue
    co,i,d=kd.find(Vector((p.x,p.y,0)))
    if d>6: continue
    ez=bd[i].z-0.04
    tgt=min(ez-0.20*max(0,d-0.5), p.z+1.1)
    if tgt>p.z:
        mx=max(mx,tgt-p.z); p.z=tgt; v.co=ti@p; k+=1
ter.data.update(); print('embankment terrain verts raised',k,'max',round(mx,2))
dg.update()
e=ter.evaluated_get(dg); m=e.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(tw); e.to_mesh_clear(); TB=BVHTree.FromBMesh(b); b.free()
for name in ('Lawn_grass_instanced (3g)','dS_grass_ccom_points','Lawn_worn_edge_along_walks'):
    o=bpy.data.objects.get(name)
    if not o: continue
    mw=o.matrix_world; mi=mw.inverted(); c=0
    for v in o.data.vertices:
        p=mw@v.co
        if not(9<p.x<24 and -44<p.y<-22): continue
        h=TB.ray_cast(Vector((p.x,p.y,p.z+3)),D,8)
        if h[0] is not None and abs(h[0].z-p.z)>0.005: p.z=h[0].z; v.co=mi@p; c+=1
    o.data.update(); print('grass snapped',name,c)
o=bpy.data.objects['dS_grass_ccom_points']; mw=o.matrix_world
print('dS grass in embankment',sum(1 for v in o.data.vertices if 12<(mw@v.co).x<20 and -40<(mw@v.co).y<-22))

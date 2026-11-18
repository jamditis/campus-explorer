import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(objs):
    bm=bmesh.new()
    for o in objs:
        e=o.evaluated_get(dg); m=e.to_mesh(); t=bmesh.new(); t.from_mesh(m); t.transform(o.matrix_world)
        tm=bpy.data.meshes.new('t'); t.to_mesh(tm); t.free(); bm.from_mesh(tm); bpy.data.meshes.remove(tm); e.to_mesh_clear()
    T=BVHTree.FromBMesh(bm); bm.free(); return T
RB=bvh([bpy.data.objects['Roads_OSM']])
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=ter.data
n=len(me.vertices); co=np.zeros(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
idx=np.nonzero((co[:,0]>-8)&(co[:,0]<2)&(co[:,1]>-58)&(co[:,1]<-21))[0]; low=0
for i in idx:
    x,y,z=co[i]; zs=[]
    for dx,dy in ((0,0),(.7,0),(-.7,0),(0,.7),(0,-.7)):
        h=RB.ray_cast(Vector((x+dx,y+dy,z+3)),Vector((0,0,-1)),6)
        if h[0] is not None and h[0].z-z>-0.8: zs.append(h[0].z)
    if zs:
        zn=min(zs)-0.05
        if z>zn: co[i,2]=zn; low+=1
me.vertices.foreach_set('co',co.ravel()); me.update(); print('terrain verts lowered under drive',low)
TB=bvh([ter])
for name in ('Lawn_grass_instanced (3g)','dS_grass_ccom_points','Lawn_worn_edge_along_walks'):
    o=bpy.data.objects.get(name); m=o.matrix_world; mi=m.inverted(); c=0
    for v in o.data.vertices:
        p=m@v.co
        if not(-10<p.x<8 and -60<p.y<-16): continue
        h=TB.ray_cast(Vector((p.x,p.y,p.z+3)),Vector((0,0,-1)),6)
        if h[0] is not None and 0.01<abs(p.z-h[0].z)<1.0:
            v.co=mi@Vector((p.x,p.y,h[0].z+0.005)); c+=1
    o.data.update(); print('snapped to terrain',name,c)

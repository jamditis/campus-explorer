import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
bm=bmesh.new()
for n in ('Roads_OSM','Footpaths_OSM','CCOM_dock_apron_20261014jf3','Curbs_granite_OSM'):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh(); t=bmesh.new(); t.from_mesh(m); t.transform(o.matrix_world)
    tm=bpy.data.meshes.new('t'); t.to_mesh(tm); t.free(); bm.from_mesh(tm); bpy.data.meshes.remove(tm); e.to_mesh_clear()
PB=BVHTree.FromBMesh(bm); bm.free()
for name in ('Lawn_grass_instanced (3g)','dS_grass_ccom_points'):
    o=bpy.data.objects[name]; m=o.matrix_world; b=bmesh.new(); b.from_mesh(o.data); kill=[]
    for v in b.verts:
        p=m@v.co
        if not(-10<p.x<14 and -60<p.y<-16): continue
        h=PB.ray_cast(Vector((p.x,p.y,p.z+3)),Vector((0,0,-1)),6)
        if h[0] is not None and h[0].z-p.z>-0.6: kill.append(v)
    bmesh.ops.delete(b,geom=kill,context='VERTS'); b.to_mesh(o.data); b.free(); o.data.update(); print('grass removed under paving',name,len(kill))

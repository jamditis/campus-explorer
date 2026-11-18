import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def wbvh(names):
    V=[];P=[]
    for nm in names:
        o=bpy.data.objects.get(nm)
        if not o: continue
        e=o.evaluated_get(dg); m=e.to_mesh(); MW=o.matrix_world; b=len(V)
        V+= [MW@v.co for v in m.vertices]; P+=[tuple(b+i for i in p.vertices) for p in m.polygons]; print("WB",nm,len(m.vertices),len(m.polygons)); e.to_mesh_clear()
    return BVHTree.FromPolygons(V,P)
print('MW',bpy.data.objects['Terrain_LiDAR_DTM_1m'].matrix_world.translation); TB=wbvh(['Terrain_LiDAR_DTM_1m'])
GB=wbvh([o.name for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith(('Footpaths','Roads_OSM','OZ_walk','PB2_walk','Terrain_LiDAR')))])
holes=[]
for xi in range(-220,222,2):
    for yi in range(270,300):
        if TB.ray_cast(Vector((xi+0.3,yi*0.5,400)),Vector((0,0,-1)))[0] is None: holes.append((xi,yi*0.5))
print('HOLES135',len(holes),holes[:80])
for o in bpy.data.objects:
    if (o.name.startswith('Lamp_acorn') or o.name.startswith('Bench_walk')) and not o.hide_render:
        x,y,z=o.matrix_world.translation
        if y<140: continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; zmin=min(v.z for v in bb)
        g=GB.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]; t=TB.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
        print('L',o.name,round(x,1),round(y,1),round(zmin,2),g and round(g.z,2),t and round(t.z,2))

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']
def count(label):
    dg=bpy.context.evaluated_depsgraph_get(); dg.update()
    oe=o.evaluated_get(dg); me=oe.to_mesh(); M=o.matrix_world
    T=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])
    miss=[]
    for x in range(-5,60):
        for y in range(95,130):
            for dx,dy in ((.25,.25),(.75,.75)):
                loc,n,i,d=T.ray_cast(Vector((x+dx,y+dy,200)),Vector((0,0,-1)))
                if loc is None: miss.append((x,y))
    oe.to_mesh_clear()
    print('COUNT',label,len(miss),miss[:12])
count('all')
for m in o.modifiers:
    m.show_viewport=False
    count('without '+m.name)
    m.show_viewport=True

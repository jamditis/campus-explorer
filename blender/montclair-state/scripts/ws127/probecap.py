import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def tr(o):
    oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=o.matrix_world
    t=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[p.vertices for p in me.polygons]); oe.to_mesh_clear(); return t
objs=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS127_CollegeAve_E_curbside_bed','Terrain_LiDAR','WS113_terrain_fan','WS115_E_walk','WS102_CollegeAve_S_curb_E','WS112_','WS111_CollegeAve_S_E'))]
T=[(o.name[:28],tr(o)) for o in objs]
for (x,y) in [(-237.6,-233.9),(-237.6,-234.3),(-237.6,-234.8),(-238.4,-233.7),(-236.8,-233.7),(-237.6,-235.5),(-236.5,-235.2)]:
    out=[]
    for n,t in T:
        r=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if r[0]: out.append((n,round(r[0].z,3)))
    print('P',x,y,out)

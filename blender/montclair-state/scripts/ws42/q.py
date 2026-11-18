import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=bpy.data.objects['T_PinOak_L1_0193']; print('Q oak',tuple(round(c,2) for c in o.location),tuple(round(c,1) for c in o.dimensions),o.data.name if o.data else None, [m.name for m in o.material_slots][:4])
dg=bpy.context.evaluated_depsgraph_get()
def tree(n):
    ob=bpy.data.objects[n]; bm=bmesh.new(); bm.from_mesh(ob.evaluated_get(dg).to_mesh()); bm.transform(ob.matrix_world); return BVHTree.FromBMesh(bm)
R={n:tree(n) for n in ['WS27_CollegeAve_carriageway_2020ortho','Roads_OSM','Terrain_LiDAR_DTM_1m','Footpaths_OSM','OZ_walk_joints_auto_GN_UNVERIFIED']}
def hit(x,y):
    out=[]
    for n,t in R.items():
        r=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),400)
        if r[0]: out.append((n[:14],round(r[0].z,2)))
    return out
print('Q oakbase',hit(o.location.x,o.location.y))
for x in range(-220,-203,2):
    for y in (-84,-86,-88):
        print('Q walk',x,y,hit(x,y))

import bpy, mathutils, bmesh
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects["School of Communication and Media roof (LiDAR)"]
bm=bmesh.new(); bm.from_mesh(o.evaluated_get(dg).to_mesh()); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm)
for y in range(44,-28,-2):
    row=""
    for x in range(-26,38,1):
        h=t.ray_cast(mathutils.Vector((x,y,170.0)),mathutils.Vector((0,0,-1)))
        row+= '.' if h[0] is None else ('#' if h[0].z>146 else '+')
    print("MAP %4d %s"%(y,row))

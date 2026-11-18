import bpy, mathutils
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
names=["School of Communication and Media roof (LiDAR)","School of Communication and Media walls"]
for n in names:
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh()
    bm=__import__('bmesh').new(); bm.from_mesh(m); bm.transform(o.matrix_world)
    t=BVHTree.FromBMesh(bm)
    for (x,y) in [(-10,10),(0,10),(10,10),(20,10),(24,10),(28,10),(31,10),(31,13),(22,18),(22,22),(-4,12),(16,-10),(20,-12)]:
        h=t.ray_cast(mathutils.Vector((x,y,135.0)),mathutils.Vector((0,0,1)))
        print("PROBE",n[-12:],x,y,None if h[0] is None else round(h[0].z,2))
    if 'walls' in n:
        for y in [7,10,14]:
            h=t.ray_cast(mathutils.Vector((10,y,139.0)),mathutils.Vector((1,0,0)))
            print("EASTWALL",y,None if h[0] is None else [round(h[0].x,2)])
            h=t.ray_cast(mathutils.Vector((10,y,143.5)),mathutils.Vector((1,0,0)))
            print("EASTWALL_hi",y,None if h[0] is None else [round(h[0].x,2)])

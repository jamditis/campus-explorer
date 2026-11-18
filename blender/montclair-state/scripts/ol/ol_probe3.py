import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
cap=bpy.data.objects['OL_Schmitt_walk_island_lawn_caps']; M=cap.matrix_world
tree=BVHTree.FromPolygons([M@v.co for v in cap.data.vertices],[p.vertices for p in cap.data.polygons])
for o in bpy.context.scene.objects:
    if o.type not in ('MESH','EMPTY','CURVE') or o==cap: continue
    p=o.matrix_world.translation
    h=tree.ray_cast(Vector((p.x,p.y,300)),Vector((0,0,-1)))
    if h[0] is None: continue
    if p.z < h[0].z-0.05 and p.z > h[0].z-6:
        print('INSIDE',o.name,o.type,o.instance_type,round(p.z,2),'cap',round(h[0].z,2),'parent',o.parent.name if o.parent else None, len(o.data.vertices) if o.type=='MESH' else '')

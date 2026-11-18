import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
bs=[]
for n in ('WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','WJ_south_gully_LiDAR_patch_ext_UNVERIFIED','Context_skirt_3DEP_ortho_4km'):
    o=bpy.data.objects.get(n)
    if not o: continue
    e=o.evaluated_get(dg);m=e.to_mesh();vs=[o.matrix_world@v.co for v in m.vertices];bs.append(BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in m.polygons]));e.to_mesh_clear()
def gz(x,y):
    hs=[h[0].z for h in [b.ray_cast(Vector((x,y,400)),Vector((0,0,-1))) for b in bs] if h[0] is not None]; return max(hs) if hs else None
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree_') : continue
    t=o.matrix_world.translation
    if not (160<=t.x<=275 and 300<=t.y<=340): continue
    bb=min((o.matrix_world@Vector(c)).z for c in o.bound_box)
    g=gz(t.x,t.y)
    print('TB',o.name[8:11],round(t.x,1),round(t.y,1),'orig',round(t.z,2),'bbmin',round(bb,2),'ground',round(g,2),'base-ground',round(bb-g,2),'wj' if 'wj_dz' in o else '')

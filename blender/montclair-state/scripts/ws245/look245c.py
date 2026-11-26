import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=bpy.data.objects['WS245_E_bank_grade_target_UNVERIFIED']; M=r.matrix_world
print('LK3 ring',len(r.data.vertices),len(r.data.polygons),[c.name for c in r.users_collection],r.matrix_world.translation[:],flush=True)
xs=[(M@v.co) for v in r.data.vertices]; print('LK3 bbox',min(v.x for v in xs),max(v.x for v in xs),min(v.y for v in xs),max(v.y for v in xs),min(v.z for v in xs),max(v.z for v in xs),flush=True)
t=BVHTree.FromPolygons(xs,[p.vertices[:] for p in r.data.polygons])
for p in [(-229,130.5),(-227,127.2),(-225,127.36),(-216,118),(-224,135)]:
    h=t.ray_cast(Vector((p[0],p[1],300)),Vector((0,0,-1)),400)[0]; print('LK3 hit',p,h and round(h.z,2),flush=True)
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']; m=o.modifiers['WS245_E_bank_terrain_grade']
print('LK3 mod',m.node_group.name,[n.bl_idname for n in m.node_group.nodes][:4],m.node_group.nodes['Object Info'].inputs['Object'].default_value,flush=True)
os._exit(0)

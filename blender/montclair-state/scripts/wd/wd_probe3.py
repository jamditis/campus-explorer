import bpy
from mathutils import Vector
s=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
print('MODS',[(m.name,m.type,getattr(m,'node_group',None) and m.node_group.name) for m in s.modifiers])
mw=s.matrix_world
vs=[(mw@v.co) for v in s.data.vertices]
near=[v for v in vs if 200<v.x<240 and 400<v.y<430]
print('NV',len(near), len(vs))
for v in sorted(near,key=lambda v:(v.y,v.x))[:60]: print(round(v.x,1),round(v.y,1),round(v.z,2))
for n in ['Terrain_LiDAR_DTM_1m','RZ2_SC_LiDAR_ground_patch']:
    o=bpy.data.objects.get(n)
    if o:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; print(n,[round(min(v.x for v in bb)),round(max(v.x for v in bb)),round(min(v.y for v in bb)),round(max(v.y for v in bb))])
for n in ['VV_Blanton_entrance_0_path_link_UNVERIFIED','TJ_walk_313029110_UNVERIFIED']:
    o=bpy.data.objects.get(n); print(n, o and [m.name for m in o.data.materials], o and [m.type for m in o.modifiers], o and o.users_collection[0].name)

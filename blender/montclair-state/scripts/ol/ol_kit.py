import bpy
names=[o.name for cn in ('OL_Schmitt_walk_edge_curb_20261031ol','OL_Schmitt_walk_island_lawn_caps_20261031ol') for o in bpy.data.collections[cn].objects]
ids={bpy.data.objects[n] for n in names}
bpy.data.libraries.write('/workspace/nj-scenes/assets/walk_edge_curb_kit_ol.blend',ids,fake_user=True)
print('KIT',len(ids),names)

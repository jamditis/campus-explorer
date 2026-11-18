import bpy
names=[o.name for c in bpy.data.collections if c.name.startswith(('OK_Schmitt_window','OK_Schmitt_walk')) for o in c.objects]
ids={bpy.data.objects[n] for n in names}
bpy.data.libraries.write('/workspace/nj-scenes/assets/schmitt_window_grid_sill_plinth_kit_ok.blend',ids,fake_user=True)
print('KIT',len(ids),names)

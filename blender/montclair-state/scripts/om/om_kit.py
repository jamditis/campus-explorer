import bpy
names=[o.name for o in bpy.data.collections['OM_Schmitt_curb_joints_sill_drips_20261031om'].objects]
ids={bpy.data.objects[n] for n in names}|{bpy.data.materials['OM_Schmitt_win_blind_var_UNVERIFIED'],bpy.data.materials['OM_Schmitt_small_island_lawn_tone_UNVERIFIED']}
bpy.data.libraries.write('/workspace/nj-scenes/assets/sill_drip_curb_joint_blind_var_kit_om.blend',ids,fake_user=True)
print('KIT',len(ids),names)

import bpy
S={bpy.data.objects[n] for n in ('PX_Dickson_fullheight_toprow_windows_UNVERIFIED','PX_Dickson_toprow_blinds_curtains_UNVERIFIED','PX_Dickson_wing_parapet_infill_UNVERIFIED')}
bpy.data.libraries.write('/workspace/nj-scenes/assets/dickson_parapet_fullheight_window_kit_px.blend',S,fake_user=True)
print('PX_KIT',len(S))

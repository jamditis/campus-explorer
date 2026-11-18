import bpy
ob=[bpy.data.objects[n] for n in ('PW_Dickson_window_blinds_curtains_UNVERIFIED','PW_Dickson_sill_drip_stains_UNVERIFIED')]
bpy.data.libraries.write('/workspace/nj-scenes/assets/window_blinds_curtains_drips_kit_pw.blend',set(ob),fake_user=True,compress=True)
print('KIT written')

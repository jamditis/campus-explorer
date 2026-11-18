import bpy
N=('PZ_Dickson_wing_infill_seam_bridges_UNVERIFIED','PZ_Dickson_wing_coping_joints_corners_UNVERIFIED','PZ_Dickson_wing_coping_drip_stain_UNVERIFIED','PZ_Feliciano_SW_DTM_edge_feather_UNVERIFIED')
S={bpy.data.objects[n] for n in N}
bpy.data.libraries.write('/workspace/nj-scenes/assets/dickson_coping_joints_stain_sw_feather_kit_pz.blend',S,fake_user=True)
print('PZ_KIT',len(S))

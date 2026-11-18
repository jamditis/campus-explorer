import bpy
N=('QA_Dickson_wing_parapet_south_gap_fill_UNVERIFIED','QA_Dickson_wing_scuppers_UNVERIFIED','QA_Dickson_wing_scupper_streaks_UNVERIFIED')
S={bpy.data.objects[n] for n in N}
bpy.data.libraries.write('/workspace/nj-scenes/assets/dickson_parapet_gapfill_scuppers_kit_qa.blend',S,fake_user=True)
print('QA_KIT',len(S))

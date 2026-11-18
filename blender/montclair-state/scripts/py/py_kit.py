import bpy
S={bpy.data.objects[n] for n in ('PY_Dickson_wing_parapet_raise_UNVERIFIED','PY_Dickson_wing_parapet_back_roofstrip_UNVERIFIED','PY_Dickson_wing_parapet_coping_UNVERIFIED')}
bpy.data.libraries.write('/workspace/nj-scenes/assets/dickson_wing_parapet_coping_kit_py.blend',S,fake_user=True)
print('PY_KIT',len(S))

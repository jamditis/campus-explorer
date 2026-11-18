import bpy
for n in ('TI_CAM_oblique_east_dorms_from_SW','TQ_CAM_eye_Stone_from_W','TR_CAM_eye_Blanton_infill_from_S','TR_CAM_closeup_Stone_sill_plinth'):
    o=bpy.data.objects.get(n); print('CAM',n,tuple(round(v,1) for v in o.location),tuple(round(v,3) for v in o.rotation_euler),o.data.lens)
o=bpy.data.objects['BD_farfield_3DEP_ortho']; print('FAR',o.library, o.hide_render, [s.material.name for s in o.material_slots])
for o in bpy.data.objects:
    if o.name.startswith('BD_farfield'): print('FAR2',o.name,o.library,o.hide_render,o.users_collection[0].name if o.users_collection else None,[s.material.name for s in o.material_slots])

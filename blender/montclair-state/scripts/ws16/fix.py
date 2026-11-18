import bpy
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']
cream=bpy.data.materials['TW_Cole_stucco_cream_UNVERIFIED']
print('slot0 was',o.material_slots[0].material.name)
o.material_slots[0].link='DATA'
o.data.materials[0]=cream
print('slot0 now',o.material_slots[0].material.name)
bpy.ops.wm.save_mainfile(); print('SAVED')

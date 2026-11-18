import bpy
o=bpy.data.objects.get('WS13_Boxwood_Cole_SW_bed_0_UNVERIFIED'); print('RM',o and o.name)
if o: bpy.data.objects.remove(o); bpy.ops.wm.save_mainfile(); print('SAVED')

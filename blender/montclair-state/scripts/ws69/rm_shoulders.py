import bpy
o=bpy.data.objects.get('WS69_gap_strip_grass_shoulders')
if o: bpy.data.objects.remove(o); print('R69 removed')
bpy.ops.wm.save_mainfile(); print('R69 saved')

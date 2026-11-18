import bpy,math
c=bpy.data.objects['WQ2_CAM_treeline_SW_from_Cole']; c.location=(-160,10,185); c.rotation_euler=(math.radians(83),0,math.radians(175)); c.data.lens=45
bpy.ops.wm.save_mainfile(); print('SAVED')

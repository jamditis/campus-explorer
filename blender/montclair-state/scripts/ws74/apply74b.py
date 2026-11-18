import bpy
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws74/fix74b.py').read())
if len(me.polygons)>500 and hi<10: bpy.ops.wm.save_mainfile(); print('W74b SAVED',flush=True)
else: print('W74b NOT SAVED',flush=True)

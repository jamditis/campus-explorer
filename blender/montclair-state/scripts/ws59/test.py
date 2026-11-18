import bpy,os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws59/autumn_woods.py').read())
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('A59 saved')
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws52/render52.py').read())

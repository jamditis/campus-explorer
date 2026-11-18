import bpy,os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws188/skirtoff188.py').read())
bpy.ops.wm.open_mainfile(filepath=os.environ['F'])
for s in os.environ['SCR'].split():
    exec(open(s).read())
hwm()

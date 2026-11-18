import bpy,os
R='/workspace/nj-scenes/montclair-state'
exec(open(R+'/scripts/ws33/curb.py').read())
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)

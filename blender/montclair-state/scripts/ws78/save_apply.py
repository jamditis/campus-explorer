import bpy,os
for f in os.environ['APPLYF'].split(','):
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws78/'+f).read())
if os.environ.get('NOSAVE')!='1':
    bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)

import bpy,os
for f in os.environ['APPLYF'].split(','):
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws75/'+f).read())
bpy.ops.wm.save_mainfile(compress=False) if False else bpy.ops.wm.save_mainfile()
print('SAVED',flush=True)

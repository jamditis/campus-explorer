import bpy,os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/fix166.py').read())
OUT=os.environ.get('OUT','')
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True,compress=True); print('SAVED',OUT,flush=True)

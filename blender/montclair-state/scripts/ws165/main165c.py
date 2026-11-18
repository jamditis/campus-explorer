import bpy,os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws165/fix165b.py').read())
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws165/fix165c.py').read())
OUT=os.environ.get('OUT','')
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True,compress=True); print('SAVED',OUT,flush=True)

import bpy,os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws164/fix164b.py').read())
OUT=os.environ.get('OUT','')
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED',OUT,flush=True)

import bpy,os,runpy
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/ws72/lite_load.py')
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/ws89/apply89.py')
if os.environ.get('OUT'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'])

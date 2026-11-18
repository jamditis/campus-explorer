import bpy, os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws151/test151.py').read().replace("exec(open('/workspace/nj-scenes/montclair-state/scripts/ws151/fix151.py').read())","exec(open('/workspace/nj-scenes/montclair-state/scripts/ws151/fix151.py').read()) if os.environ.get('FIX')=='1' else None").replace("bpy.ops.wm.save_as_mainfile(filepath='/tmp/test151.blend')",""))
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws151/prev151.py').read())

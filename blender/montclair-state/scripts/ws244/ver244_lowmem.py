# ws244: ver215 check in low memory (modifiers off at load, nothing saved).
import bpy, os
from bpy.app.handlers import persistent
@persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers:
            try: m.show_viewport=False
            except Exception: pass
bpy.app.handlers.load_post.append(_off)
bpy.ops.wm.open_mainfile(filepath=os.environ['F'])
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws215/ver215.py').read())

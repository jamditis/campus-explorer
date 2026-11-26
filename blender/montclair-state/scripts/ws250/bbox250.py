# ws205: dump every object's world bbox + type + hide_render (for low-memory subset renders via libraries.load)
import bpy, json, os
S='/workspace/nj-scenes/montclair-state/scripts/'
exec(open(S+'ws189/alloff189.py').read())
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/'+os.environ.get('BBF','montclair_state.blend'), load_ui=False)
from mathutils import Vector
out={}
for o in bpy.data.objects:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    out[o.name]=[o.type,o.hide_render,min(v.x for v in bb),max(v.x for v in bb),min(v.y for v in bb),max(v.y for v in bb),min(v.z for v in bb),max(v.z for v in bb),[c.name for c in o.users_collection]]
json.dump(out,open(S+'ws250/bbox250.json','w')); print('BB205',len(out),flush=True)
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('MEM',l.strip(),flush=True)

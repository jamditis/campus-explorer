import bpy, math
from mathutils import Vector
import os
os.environ['SAVE']='0'
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws108/eaves108.py').read())
# rename misnamed WS105 walkway objects (Panzer side, per ws107 OSM correction)
for o in bpy.data.objects:
    if 'Chapin_E_lower_walkway' in o.name:
        old=o.name; o.name=old.replace('Chapin_E_lower_walkway','PanzerE_side_lower_walkway'); print('REN108',old,'->',o.name)
for c in bpy.data.collections:
    if 'Chapin_E' in c.name and c.name.startswith('WS105'):
        old=c.name; c.name=old.replace('Chapin_E','PanzerE_side'); print('REN108 col',old,'->',c.name)
# trees near the WS105 eye-from-walk-N camera
cx,cy=-220.68,-154.42
for o in bpy.data.objects:
    if o.name.startswith('T_') and not o.hide_render:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        x0=min(v.x for v in bb);x1=max(v.x for v in bb);y0=min(v.y for v in bb);y1=max(v.y for v in bb)
        if x0-1<cx<x1+1 and y0-1<cy<y1+1: print('TREECAM108',o.name,round(x0,1),round(x1,1),round(y0,1),round(y1,1),round(min(v.z for v in bb),1),round(max(v.z for v in bb),1), tuple(round(v,1) for v in o.matrix_world.translation))
bpy.ops.wm.save_mainfile(); print('M108 SAVED',flush=True)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws105/cut105.py').read().replace('ws105/render_cut105','ws108/render_cut108'))

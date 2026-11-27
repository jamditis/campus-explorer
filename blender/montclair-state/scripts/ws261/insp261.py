import bpy
from mathutils import Vector
for n in bpy.data.objects.keys():
    if n.startswith(('WS129b_Chapin_S_drive','WS261_','WS128')):
        o=bpy.data.objects[n]; bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        print('I261',n[:80],o.type,'x %.1f %.1f y %.1f %.1f z %.2f %.2f'%(min(v.x for v in bb),max(v.x for v in bb),min(v.y for v in bb),max(v.y for v in bb),min(v.z for v in bb),max(v.z for v in bb)),'mods',[m.name for m in o.modifiers][:4],flush=True)

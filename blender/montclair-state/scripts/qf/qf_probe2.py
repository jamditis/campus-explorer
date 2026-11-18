import bpy
from mathutils import Vector
for o in bpy.data.objects:
    n=o.name.lower()
    if o.type=='MESH' and ('college' in n or 'tower' in n or 'dickson' in n and 'walls' in n or 'cels' in n and 'walls' in n):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; print('CH',o.name[:70],round(sum(v.x for v in bb)/8,1),round(sum(v.y for v in bb)/8,1),round(max(v.z for v in bb),1),o.hide_render)
for c in bpy.data.collections:
    if 'college' in c.name.lower() or 'hall' in c.name.lower(): print('COLL',c.name,len(c.all_objects))

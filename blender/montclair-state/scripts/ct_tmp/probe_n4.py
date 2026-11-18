import bpy
from mathutils import Vector
for o in bpy.data.objects:
  if o.library and o.type=='MESH' and ('add' in o.name.lower() or 'Susan' in o.name):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    print('BB',o.name[:60],[round(min(v[i] for v in bb),1) for i in range(3)],[round(max(v[i] for v in bb),1) for i in range(3)],flush=True)

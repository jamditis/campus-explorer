import bpy
from mathutils import Vector
for c in bpy.data.collections:
    if 'ichardson' in c.name:
        print('COLL',c.name,len(c.all_objects))
        for o in c.all_objects:
            if o.type=='MESH':
                bb=[o.matrix_world@Vector(v) for v in o.bound_box]
                print('  OBJ',o.name,len(o.data.polygons),[m.name for m in o.data.materials][:4],round(min(v.z for v in bb),2),round(max(v.z for v in bb),2), o.hide_render)
            else: print('  OBJ',o.name,o.type)

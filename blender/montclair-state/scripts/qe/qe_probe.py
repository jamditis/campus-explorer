import bpy
from mathutils import Vector
def bb(o):
    p=[o.matrix_world@Vector(c) for c in o.bound_box]
    return tuple(round(min(q[i] for q in p),2) for i in range(3)),tuple(round(max(q[i] for q in p),2) for i in range(3))
for o in bpy.data.objects:
    if 'Computing' in o.name or 'CCIS' in o.name or 'ccis' in o.name:
        print('OBJ',repr(o.name),o.type,o.hide_render,o.hide_viewport,[c.name for c in o.users_collection],bb(o),len(o.data.polygons) if o.type=='MESH' else '', [m.name for m in o.data.materials] if o.type=='MESH' else '', [m.name for m in o.modifiers])
w=bpy.data.objects['Center for Computing and Information Science walls']
print('WALLV',[tuple(round(x,2) for x in (w.matrix_world@v.co)) for v in w.data.vertices][:80])
for n in ['Dickson','Calcia']:
    for o in bpy.data.objects:
        if n in o.name and o.type=='MESH' and not o.hide_render and ('PV' in o.name or 'PR' in o.name or 'PS' in o.name or 'frame' in o.name.lower()):
            print('STY',o.name,len(o.data.polygons),[m.name for m in o.data.materials][:8])

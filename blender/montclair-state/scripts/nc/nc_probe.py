import bpy
from mathutils import Vector
O=bpy.data.objects
for nm in ['CCOM newsroom grid spots (mx, GN instances)']:
    o=O[nm]; print('SPOTS',len(o.data.vertices), [tuple(round(x,2) for x in (o.matrix_world@v.co)) for v in o.data.vertices][:4])
    for m in o.modifiers: print(' mod',m.type,m.name, getattr(m,'node_group',None) and m.node_group.name)
for o in O:
    n=o.name.lower()
    if ('newsroom' in n or 'studio' in n) and ('floor' in n or 'softbox' in n or 'window' in n or 'glass' in n or 'anchor' in n or 'camera' in n or 'grid' in n):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        print('OBJ',o.name,'|',o.hide_render,[round(min(v[i] for v in bb),2) for i in range(3)],[round(max(v[i] for v in bb),2) for i in range(3)],[s.material.name if s.material else None for s in o.material_slots][:4])

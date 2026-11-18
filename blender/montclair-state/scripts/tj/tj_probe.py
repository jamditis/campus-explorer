import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.type!='MESH': continue
    n=o.name.lower()
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; bx=[v.x for v in bb]; by=[v.y for v in bb]
    if 'grass' in n and len(o.data.polygons)==0:
        print('GRASS',o.name,len(o.data.vertices),[round(v) for v in (min(bx),max(bx),min(by),max(by))],[m.type+':'+(m.node_group.name if m.type=='NODES' and m.node_group else '') for m in o.modifiers],o.hide_render,list(o.data.attributes.keys())[:8])
    elif min(bx)<200 and max(bx)>80 and min(by)<470 and max(by)>330 and max(bx)-min(bx)<300 and not o.hide_render:
        print('OBJ',o.name,len(o.data.polygons),[round(v) for v in (min(bx),max(bx),min(by),max(by))])

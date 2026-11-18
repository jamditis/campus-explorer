import bpy
for o in bpy.data.collections['Main_grass_cx_clumps'].all_objects: print('CL',o.name,tuple(round(d,3) for d in o.dimensions),len(o.data.polygons) if o.type=='MESH' else o.type)
w=bpy.data.collections.get('Weeds + unmown tufts at walk edges (3g)') or bpy.data.objects.get('Weeds + unmown tufts at walk edges (3g)')
print('W',w, getattr(w,'type',None))
from mathutils import Vector
# which grass-like instancers are near the close-up view (within 25 m of cam)
cam=Vector((140,285,0))
for o in bpy.data.objects:
    if o.type!='MESH' or not any(m.type=='NODES' for m in o.modifiers): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if min(b.x for b in bb)<150 and max(b.x for b in bb)>125 and min(b.y for b in bb)<300 and max(b.y for b in bb)>270:
        print('GN',o.name,len(o.data.vertices),[m.node_group.name for m in o.modifiers if m.type=='NODES'],o.hide_render)

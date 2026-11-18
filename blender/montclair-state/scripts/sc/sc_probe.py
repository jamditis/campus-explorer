import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type=='MESH' and any(s.material and s.material.name.startswith('SC_') for s in o.material_slots): print('SCMAT',o.name,o.hide_render,len(o.data.polygons))
for x,y in [(-113.1,212.14),(-112.8,207),(-113.5,220)]:
    r=bpy.context.scene.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
    print('HIT',x,y,r[4].name if r[0] else None, round(r[1].z,3) if r[0] else None, r[4].material_slots[r[4].data.polygons[r[3]].material_index].material.name if r[0] and r[4].type=='MESH' and r[3]<len(r[4].data.polygons) and r[4].material_slots else '')

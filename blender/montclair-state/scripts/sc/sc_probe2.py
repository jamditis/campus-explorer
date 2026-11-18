import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
for x,y in [(-118,302),(-110,306),(-104,309),(-112,296)]:
    r=bpy.context.scene.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
    o=r[4] if r[0] else None
    mn=''
    if o is not None and o.type=='MESH' and o.material_slots:
        try: mn=o.material_slots[o.data.polygons[r[3]].material_index].material.name
        except Exception as e: mn='?'
    print('HIT2',x,y,o.name if o else None,mn)

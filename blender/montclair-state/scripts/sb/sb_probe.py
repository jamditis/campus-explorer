import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for x,y in ((-122,243),(-125,246),(-135,250),(-140,262),(-150,275),(-120,262),(-112,276),(-118,283)):
    r=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
    o=r[4]; mn=''
    if o and o.material_slots:
        e=o.evaluated_get(dg); 
        try: mn=o.material_slots[e.data.polygons[r[3]].material_index].name
        except Exception: mn='?'
    print('PROBE',x,y,round(r[1].z,2) if r[0] else None,o.name if o else None,mn)

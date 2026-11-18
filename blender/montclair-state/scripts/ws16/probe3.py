import bpy, collections
from mathutils import Vector
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; mw=o.matrix_world
c=collections.Counter()
for p in o.data.polygons:
    z=(mw@p.center).z
    if z>142.6: c[(o.material_slots[p.material_index].material.name, round(z,1))]+=1
print('TOPFACES',sorted(c.items()))
pt=Vector((-90,-74,143.8))
for ob in bpy.data.objects:
    if ob.type!='MESH' or ob.hide_render: continue
    bb=[ob.matrix_world@Vector(v) for v in ob.bound_box]
    mn=Vector((min(v.x for v in bb),min(v.y for v in bb),min(v.z for v in bb))); mx=Vector((max(v.x for v in bb),max(v.y for v in bb),max(v.z for v in bb)))
    if all(mn[i]-3<pt[i]<mx[i]+3 for i in range(3)):
        print('NEAR',ob.name,len(ob.data.polygons),[round(v,1) for v in mn],[round(v,1) for v in mx],[s.material.name for s in ob.material_slots if s.material][:3])

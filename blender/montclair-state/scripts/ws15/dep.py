import bpy
from mathutils import Vector
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; me=o.data
slots=[s.material.name for s in o.material_slots]
n=Vector((0.975,-0.22,0)).normalized(); W=Vector((-n.y,n.x,0))
c0=Vector((-95.86,-74.33,0))
for p in me.polygons:
    c=p.center
    if (c.to_2d()-c0.to_2d()).length<1.2 and 134.5<c.z<138.5:
        print('P',p.index,slots[p.material_index][7:14],'d=%.3f u=%.2f z=%.2f nd=%.2f area=%.2f'%((c-c0).dot(n),(c-c0).dot(W),c.z,p.normal.dot(n),p.area))

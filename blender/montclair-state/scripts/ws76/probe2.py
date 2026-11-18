import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if not o.name.startswith('T_'): continue
    l=o.matrix_world.translation
    if -262<l.x<-215 and -95<l.y<-60:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        print('P76t',o.name,o.type,tuple(round(c,1) for c in l),tuple(round(c,2) for c in o.rotation_euler),'bbz',round(min(p.z for p in bb),1),round(max(p.z for p in bb),1),'bbx',round(min(p.x for p in bb),1),round(max(p.x for p in bb),1),'bby',round(min(p.y for p in bb),1),round(max(p.y for p in bb),1),o.get('src',''),flush=True)

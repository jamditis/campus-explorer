import bpy
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
for nm in ['CCOM entrance spandrel (outer)','CCOM entrance pier -1','CCOM entrance pier +1','CCOM entrance arch ring (inner tier)','CCOM entrance cornice']:
    o=bpy.data.objects[nm]; mw=o.matrix_world
    vs=[mw@v.co for v in o.data.vertices]
    print('G',nm,'w',round(min(v.dot(n) for v in vs),3),round(max(v.dot(n) for v in vs),3),'u',round(min(v.dot(t) for v in vs),3),round(max(v.dot(t) for v in vs),3),'z',round(min(v.z for v in vs),3),round(max(v.z for v in vs),3))
for nm in ['CCOM tower 4a hip roof tiles','CCOM tower 4a hip eave fascia + soffit']:
    o=bpy.data.objects[nm]; print('M',nm,[m.name for m in o.data.materials], o.data.uv_layers.keys(), list(o.data.attributes.keys())[:12])
print('MATS',[m for m in ['Wall_SCM_precast','SCM_tower_precast','Cast_stone_tan','Eave_fascia_dark_wood'] if m in bpy.data.materials])

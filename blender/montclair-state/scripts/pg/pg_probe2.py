import bpy
from mathutils import Vector
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']; mw=r.matrix_world
import collections
bins=collections.Counter()
low=[]
for p in r.data.polygons:
    c=mw@p.center; n=(mw.to_3x3()@p.normal).normalized()
    if c.z<157:
        low.append((round(c.x,1),round(c.y,1),round(c.z,1),round(n.z,2),round(p.area,1),p.material_index))
print('NLOW',len(low))
for l in sorted(low,key=lambda t:t[2])[:400:4]: print('LOW',l)
w=bpy.data.objects['Feliciano School of Business walls']
for p in w.data.polygons:
    c=w.matrix_world@p.center; n=p.normal
    print('WALL',p.index,round(c.x,1),round(c.y,1),round(c.z,1),[round(x,2) for x in n],round(p.area,1),p.material_index)
m=bpy.data.materials['Wall_stucco_mission']
for nd in m.node_tree.nodes: print('NODE',nd.type,nd.name,nd.label,[ (i.name, i.default_value if hasattr(i,'default_value') and not hasattr(i.default_value,'__len__') else '') for i in nd.inputs if not i.is_linked][:6])
print('UV',[u.name for u in w.data.uv_layers],[a.name for a in w.data.attributes])

# export RED HAWK letter faces (all faces) in wall-plane 2D coords for shapely analysis (read-only)
import bpy, json
from mathutils import Vector
o=[x for x in bpy.data.objects if x.name.startswith('MI Annex RED HAWK COUNTRY 3D letters')][0]
me=o.data; mw=o.matrix_world
t=Vector((0.07,1.0,0)).normalized()  # along-wall axis (approx from normals)
F=[]
for p in me.polygons:
    vs=[mw@me.vertices[i].co for i in p.vertices]
    n=(mw.to_3x3()@p.normal).normalized()
    F.append(dict(i=p.index,m=p.material_index,n=[round(n.x,3),round(n.y,3),round(n.z,3)],uv=[[v.dot(t),v.z] for v in vs],d=[v.x for v in vs]))
json.dump(dict(name=o.name,faces=F),open('data/sd/letters.json','w'))
print('EXPORTED',len(F))

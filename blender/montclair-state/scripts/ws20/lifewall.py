import bpy, bmesh
from mathutils import Vector
from collections import Counter
o=bpy.data.objects['Life Hall walls']; M=o.matrix_world
print('LW', len(o.data.vertices), len(o.data.polygons), [m.type for m in o.modifiers], o.data.materials[:] and [m.name for m in o.data.materials])
bm=bmesh.new(); bm.from_mesh(o.data)
bd=[e for e in bm.edges if e.is_boundary]
print('boundary edges',len(bd))
tops=[]
for e in bd:
    a=M@e.verts[0].co; b=M@e.verts[1].co
    if abs(a.z-b.z)<0.05 and a.z>140:
        tops.append((round((a.z+b.z)/2,2),round(a.x,1),round(a.y,1),round(b.x,1),round(b.y,1)))
zs=Counter(t[0] for t in tops); print('TOPZ',zs.most_common(15))
for t in sorted(tops,key=lambda t:-t[2])[:40]: print('T',t)
s=bpy.data.objects['Life Hall eave soffit + fascia + rafter tails']
print('SOFF mats',[m.name for m in s.data.materials])

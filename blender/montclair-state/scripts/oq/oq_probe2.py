import bpy
from mathutils import Vector
from collections import Counter
for n in ['Center for Computing and Information Science walls','Calcia Hall walls','Speech Building walls']:
    w=bpy.data.objects[n]; bb=[w.matrix_world@Vector(c) for c in w.bound_box]
    x0=min(v.x for v in bb);x1=max(v.x for v in bb);y0=min(v.y for v in bb);y1=max(v.y for v in bb)
    print('BB',n,round(x0),round(x1),round(y0),round(y1),round(min(v.z for v in bb),1),round(max(v.z for v in bb),1))
    c=Counter()
    for o in bpy.data.objects:
        if o.type not in('MESH','EMPTY'): continue
        p=o.matrix_world.translation
        if x0-2<p.x<x1+2 and y0-2<p.y<y1+2: c[(o.users_collection[0].name if o.users_collection else '-')[:50]]+=1
    print('  cols',c.most_common(8))
print('MATS',[m.name for m in bpy.data.materials if any(k in m.name.lower() for k in ('glass','frame','window','sill'))][:60])

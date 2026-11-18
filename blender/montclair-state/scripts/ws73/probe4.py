import bpy
from mathutils import Vector
from collections import defaultdict
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for o in sc.objects:
    if 'cogen' in o.name.lower() or 'plant' in o.name.lower():
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; print('P4 obj',o.name,[round(min(p.x for p in bb)),round(max(p.x for p in bb)),round(min(p.y for p in bb)),round(max(p.y for p in bb))])
hits=defaultdict(list)
for i in range(0,61):
    for j in range(0,61):
        x=-345+i*1.75; y=-160+j*2.0
        r=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
        if r[0]:
            o=r[4]; mi=o.data.polygons[r[3]].material_index if o.type=='MESH' and r[3]<len(o.data.polygons) else -1
            mn=o.material_slots[mi].material.name if 0<=mi<len(o.material_slots) and o.material_slots[mi].material else '?'
            hits[(o.name[:60],mn[:40])].append((round(x),round(y),round(r[1].z,1)))
for k,v in sorted(hits.items(),key=lambda kv:-len(kv[1])):
    xs=[p[0] for p in v]; ys=[p[1] for p in v]
    print('P4',k,len(v),'x',min(xs),max(xs),'y',min(ys),max(ys))

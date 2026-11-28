# ws273 probe D (NO SAVE): evaluated Terrain faces over the lot-pocket hole (x -250..-235, y -114..-100): materials, normals, z; modifier list.
import bpy, os, collections
from mathutils import Vector
TAG='P273D'; BX=(-250.0,-235.0,-114.0,-100.0)
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']
print(TAG,'mods',[(m.name,m.type,m.node_group.name if m.type=='NODES' and m.node_group else None) for m in o.modifiers],flush=True)
for m in o.modifiers: m.show_viewport=True
dg=bpy.context.evaluated_depsgraph_get(); oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=o.matrix_world
C=collections.Counter(); R=collections.defaultdict(list)
for p in me.polygons:
    c=mw@p.center
    if BX[0]<c.x<BX[1] and BX[2]<c.y<BX[3]:
        mn=me.materials[p.material_index].name if p.material_index<len(me.materials) and me.materials[p.material_index] else None
        C[mn]+=1; R[mn].append((round(c.x,1),round(c.y,1),round(c.z,2),round(p.normal.z,3),round(p.area,2)))
print(TAG,'mats',dict(C),flush=True)
for k,v in R.items():
    xs=[a[0] for a in v]; ys=[a[1] for a in v]
    print(TAG,k,'x',min(xs),max(xs),'y',min(ys),max(ys),'sample',v[:6],flush=True)
print(TAG,'attrs',[a.name for a in me.attributes],flush=True)
oe.to_mesh_clear(); os._exit(0)

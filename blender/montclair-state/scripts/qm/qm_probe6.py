import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; e=T.evaluated_get(dg); me=e.data
mw=T.matrix_world
print('terrain mods',[m.name for m in T.modifiers])
bad=[]
for p in me.polygons:
    c=mw@p.center
    if 138<c.x<156 and 162<c.y<184:
        n=(mw.to_3x3()@p.normal).normalized()
        if n.z<0.3: bad.append((round(c.x,1),round(c.y,1),round(c.z,2),round(n.z,2),round(p.area,2),p.material_index))
print('steep/flipped faces in box',len(bad)); [print(b) for b in bad[:40]]
bt=BVHTree.FromObject(T,dg)
for y in range(164,184,2):
    row=[]
    for x in range(138,158,2):
        h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        row.append('%6.1f'%h[0].z if h[0] is not None else '  MISS')
    print(y,' '.join(row))

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
for o in bpy.data.objects:
    if o.name.startswith('WS70'):
        bb=[o.matrix_world@Vector(b) for b in o.bound_box]
        print('P220 WS70obj',o.name,len(o.data.vertices) if o.type=='MESH' else '', [round(min(v[i] for v in bb),2) for i in range(3)],[round(max(v[i] for v in bb),2) for i in range(3)],[s.material.name if s.material else None for s in o.material_slots],[m.type for m in o.modifiers])
X0,X1,Y0,Y1=-262,-238,-64,-44
cand=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or not o.data.polygons: continue
    bb=[o.matrix_world@Vector(b) for b in o.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    if max(v.x for v in bb)-min(v.x for v in bb)>400: continue
    cand.append(o)
print('P220 cand',len(cand))
T={}
for o in cand:
    M=o.matrix_world
    T[o.name]=(BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons]),o)
import collections
for y in range(Y1,Y0-1,-2):
    row=[]
    for x in range(X0,X1+1,2):
        hits=[]
        for n,(t,o) in T.items():
            h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
            if h[0]: hits.append((h[0].z,n))
        hits.sort(reverse=True)
        row.append('%d,%d:'%(x,y)+('|'.join('%s@%.2f'%(n[:22],z) for z,n in hits[:3])))
    for r in row: print('P220G',r)

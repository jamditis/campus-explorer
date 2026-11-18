import bpy
from mathutils import Vector
X0,X1,Y0,Y1=-226,-210,-166,-150
for o in bpy.data.objects:
    if o.type!='MESH': continue
    mw=o.matrix_world; n=0; zs=[]
    if len(o.data.vertices)>400000: continue
    for p in o.data.polygons:
        c=mw@p.center
        if X0<=c.x<=X1 and Y0<=c.y<=Y1: n+=1; zs.append(c.z)
    if n: print('P121',o.name,n,round(min(zs),2),round(max(zs),2),[m.name for m in o.data.materials][:3], [md.type for md in o.modifiers])

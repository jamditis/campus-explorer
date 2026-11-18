import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
from collections import Counter
for z in (139.5,141.5,142.5,143.5,144.2):
    row=[]
    for x in range(26,60,2):
        h,loc,n,i,ob,_=sc.ray_cast(dg,Vector((x,125,z)),Vector((0,-1,0)),distance=60)
        row.append((x,round(loc.y,1) if h else None,(ob.name[:28] if h else '-')))
    print('Z',z); [print('   ',r) for r in row]

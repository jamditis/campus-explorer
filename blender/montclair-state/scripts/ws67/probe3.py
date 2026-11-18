import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for y in (-62,-58,-55,-52):
    row=[]
    for x in range(-272,-238,2):
        r=sc.ray_cast(dg,Vector((x,y,170)),Vector((0,0,-1)))
        if r[0]: row.append('%d:%s@%.2f'%(x,r[4].name[:10],r[1].z))
        else: row.append('%d:-'%x)
    print('P3 y',y,' '.join(row))

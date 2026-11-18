import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get(); out=[]
for y in (80,95,106,115,130,142):
    row=[]
    for x in range(-262,-219,2):
        r=sc.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
        row.append('%.1f%s'%(r[1].z,r[4].name[0:2]) if r[0] else 'NA')
    out.append('y%d: '%y+' '.join(row))
open('data/pz/probe_step2.txt','w').write('\n'.join(out)); print('\n'.join(out))

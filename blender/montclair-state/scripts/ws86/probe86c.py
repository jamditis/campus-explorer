import bpy
from mathutils import Vector
sc=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
for x,y in[(-245,-145),(-240,-140),(-238,-135),(-244,-132),(-236,-150),(-246,-152),(-228,-145),(-215,-145),(-260,-140),(-255,-150)]:
    o=Vector((x,y,400));hits=[]
    for i in range(4):
        r=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not r[0]:break
        hits.append('%s@%.2f'%(r[4].name[:40],r[1].z));o=r[1]+Vector((0,0,-0.01))
    print('P86 hit',x,y,hits)

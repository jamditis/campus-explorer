import bpy, mathutils
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for (x,y) in [(-83.5,257),(-75,250),(-95,262),(-83,240),(-70,265)]:
    hits=[]; o=mathutils.Vector((x,y,300)); 
    for i in range(6):
        r=sc.ray_cast(dg,o,mathutils.Vector((0,0,-1)))
        if not r[0]: break
        hits.append((r[4].name[:70], round(r[1].z,2), r[4].hide_render))
        o=r[1]+mathutils.Vector((0,0,-0.01))
    print('PROBE',x,y,hits)

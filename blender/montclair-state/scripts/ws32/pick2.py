import bpy
from mathutils import Vector
sc=bpy.context.scene; c=bpy.data.objects['WS32_CAM_closeup_walk_apron_seam']
sc.render.resolution_x=1280; sc.render.resolution_y=720
dg=bpy.context.evaluated_depsgraph_get()
fr=[c.matrix_world@v for v in c.data.view_frame(scene=sc)]
o=c.matrix_world.translation
for u,v,lab in [(.677,.59,'wedge'),(.70,.57,'wedge2'),(.612,.5625,'blotch_mid'),(.43,.49,'blotch_left'),(.30,.465,'blotch_far'),(.55,.66,'walk_clean')]:
    p=fr[3].lerp(fr[0],u).lerp(fr[2].lerp(fr[1],u),v); d=(p-o).normalized(); s=o.copy(); out=[]
    for k in range(3):
        r=sc.ray_cast(dg,s,d)
        if not r[0]: break
        out.append((r[4].name[:28],tuple(round(x,2) for x in r[1]))); s=r[1]+d*0.002
    print('PICK',lab,out)

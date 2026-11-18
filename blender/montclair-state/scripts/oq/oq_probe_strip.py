import bpy
from mathutils import Vector
scn=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['OP_CAM_eye_redraped_road_E_campus_edge']
fr=cam.data.view_frame(scene=scn); mw=cam.matrix_world
tl,tr,br,bl=[mw@v for v in fr]  # view_frame order: tr, br, bl, tl actually
f=[mw@v for v in fr]
o=mw.translation
for yy in [i/40 for i in range(14,30)]:
    for xx in (0.3,0.7):
        # interpolate in frame: f[0]=tr f[1]=br f[2]=bl f[3]=tl
        top=f[3]+(f[0]-f[3])*xx; bot=f[2]+(f[1]-f[2])*xx; p=top+(bot-top)*yy
        h=scn.ray_cast(dg,o,(p-o).normalized())
        print('R',round(yy,3),xx,h[4].name if h[0] else None, tuple(round(c,2) for c in h[1]) if h[0] else '', h[4].material_slots[h[3] if False else 0].material.name if h[0] and h[4].material_slots else '')

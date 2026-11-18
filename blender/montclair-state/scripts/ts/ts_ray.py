import bpy
from mathutils import Vector
sc=bpy.context.scene; cam=bpy.data.objects['TI_CAM_oblique_east_dorms_from_SW']
sc.render.resolution_x=1024; sc.render.resolution_y=576
fr=cam.data.view_frame(scene=sc)  # tr,br,bl,tl
M=cam.matrix_world; o=M.translation
dg=bpy.context.evaluated_depsgraph_get()
for (u,v) in [(0.1,0.3),(0.2,0.35),(0.4,0.25),(0.75,0.4),(0.6,0.2),(0.9,0.5),(0.1,0.6),(0.5,0.15)]:
    tr,br,bl,tl=fr
    p=tl+(tr-tl)*u+(bl-tl)*v
    d=(M.to_3x3()@p).normalized()
    hit,loc,n,i,ob,mx=sc.ray_cast(dg,o,d)
    print('RAY',u,v,hit,ob.name if ob else None,tuple(round(c) for c in loc), ob.active_material.name if ob and ob.active_material else None)

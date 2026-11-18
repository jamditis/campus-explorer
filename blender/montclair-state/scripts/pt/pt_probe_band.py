import bpy
from mathutils import Vector
sc=bpy.context.scene; cam=bpy.data.objects['PE_CAM_oblique_calcia_from_SE']; sc.camera=cam
sc.render.resolution_x=1024; sc.render.resolution_y=576
for ob in bpy.data.objects:
    if not ob.hide_render: ob.hide_viewport=False; ob.hide_set(False)
dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world; o=mw.translation
def ray(px,py):
    x=px/1024; y=1-py/576
    tr,br,bl,tl=[mw@v for v in fr]
    p=bl+(br-bl)*x+(tl-bl)*y; d=(p-o).normalized()
    h,loc,n,fi,ob,_=sc.ray_cast(dg,o,d)
    if h:
        me=ob.evaluated_get(dg).data; f=me.polygons[fi] if fi<len(me.polygons) else None
        print('PX',px,py,ob.name[:60],'fi',fi,'n',tuple(round(c,3) for c in n),'loc',tuple(round(c,2) for c in loc))
for px in (200,300,400):
    for py in (378,386,394,402,410):
        ray(px,py)

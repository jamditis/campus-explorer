import bpy, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
c=bpy.data.objects['NY_CAM_closeup_N_classroom_shell_chairs_clock_whiteboard']
fr=[c.matrix_world@v for v in c.data.view_frame(scene=sc)]  # tr, br, bl, tl
tr,br,bl,tl=fr; o=c.matrix_world.translation
for px,py in ((360,10),(450,20),(550,30),(500,5),(420,40),(200,5)):
    u=px/1024; v=py/576
    p=tl+(tr-tl)*u+(bl-tl)*v; d=(p-o).normalized()
    r=sc.ray_cast(dg,o,d)
    print('P4',px,py,r[0] and [round(x,2) for x in r[1]],r[0] and [round(x,2) for x in r[2]], r[4].name if r[0] else None, r[4].hide_render if r[0] else None)

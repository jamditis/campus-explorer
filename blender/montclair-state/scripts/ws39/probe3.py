import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['WS35_CAM_eye_RedHawk_statue_match4_from_W']
sc.render.resolution_x=1280; sc.render.resolution_y=720
tr,br,bl,tl=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]; o0=cam.matrix_world.translation
cx0,cx1,cy0,cy1=-250,-150,-150,-60
for ob in sc.objects:
    if ob.type in ('CAMERA','LIGHT') or ob.hide_render or ob.name.startswith('Terrain_LiDAR'): continue
    bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]; xs=[q.x for q in bb]; ys=[q.y for q in bb]
    if max(xs)<cx0 or min(xs)>cx1 or max(ys)<cy0 or min(ys)>cy1: ob.hide_render=True
print('P39c cam',[round(c,2) for c in o0])
for px in (780,820,860,900,940):
  for py in range(236,262,3):
    u=px/960; v=py/540; p=(tl+(tr-tl)*u)+((bl+(br-bl)*u)-(tl+(tr-tl)*u))*v; d=(p-o0).normalized(); o=o0.copy()
    for k in range(12):
        hit,loc,n,i,ob,m=sc.ray_cast(dg,o,d)
        if not hit: print('P39c',px,py,None); break
        if ob.hide_render or ob.name.startswith('T_'): o=loc+d*0.01; continue
        print('P39c',px,py,ob.name,[round(c,2) for c in loc]); break

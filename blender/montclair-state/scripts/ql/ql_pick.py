import bpy, collections
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=bpy.data.objects['QK_CAM_eye_ccis_east_bay']; sc.camera=cam
sc.render.resolution_x=1024; sc.render.resolution_y=576; sc.render.resolution_percentage=100
dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc); M=cam.matrix_world; o=M.translation
tl,tr,br,bl=[M@v for v in (fr[0],fr[1],fr[2],fr[3])]  # view_frame order: tr,br,bl,tl
tr,br,bl,tl=[M@v for v in fr]
def ray(px,py):
    u=px/1024; v=py/576
    top=tl.lerp(tr,u); bot=bl.lerp(br,u); p=top.lerp(bot,v)
    return sc.ray_cast(dg,o,(p-o).normalized())
for (x0,x1,y0,y1,lab) in [(55,135,250,395,'wedge'),(190,215,90,160,'vstrip_top'),(190,215,200,250,'vstrip_mid'),(960,985,120,370,'right_strip'),(20,60,40,400,'left_pilaster'),(130,500,378,395,'ledge_left')]:
    c=collections.Counter(); pts={}
    for x in range(x0,x1,5):
        for y in range(y0,y1,6):
            h,loc,nr,fi,ob,_=ray(x,y)
            if h: k=ob.name; c[k]+=1; pts.setdefault(k,(tuple(round(a,2) for a in loc),tuple(round(a,2) for a in nr)))
    print('PICK',lab,c.most_common(6)); [print('  ',k,pts[k]) for k,_ in c.most_common(6)]

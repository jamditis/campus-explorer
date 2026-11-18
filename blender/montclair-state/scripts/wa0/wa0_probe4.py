import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cd=bpy.data.cameras.new('tmp'); cam=bpy.data.objects.new('TMP_CAM',cd); sc.collection.objects.link(cam)
P=Vector((116.5,279.6,138.6)); T=Vector((112.6,281.2,137.75))
cam.location=P; cam.rotation_euler=(T-P).to_track_quat('-Z','Y').to_euler(); cd.lens=35
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
def ray(px,py,rx=768,ry=432):
    nx=(px+.5)/rx; ny=1-(py+.5)/ry
    tr,br,bl,tl=cd.view_frame(scene=sc); p=bl.lerp(br,nx).lerp(tl.lerp(tr,nx),ny)
    o=cam.matrix_world.translation.copy(); return o,((cam.matrix_world@p)-o).normalized()
for px,py in [(366,300),(364,330),(368,270),(372,320),(395,175),(400,230),(400,370),(380,390)]:
    o,d=ray(px,py); hits=[]; oo=o.copy()
    for i in range(5):
        r=sc.ray_cast(dg,oo,d,distance=60)
        if not r[0]: hits.append('MISS'); break
        hits.append((r[4].name[:40],tuple(round(c,3) for c in r[1]),'bf' if d.dot(r[2])>0 else 'ff'))
        oo=r[1]+d*0.002
    print('PX',px,py,hits)

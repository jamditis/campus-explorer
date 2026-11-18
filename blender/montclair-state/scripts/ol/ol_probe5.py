import bpy, mathutils
cap=bpy.data.objects['OL_Schmitt_walk_island_lawn_caps']; me=cap.data; ul=me.uv_layers['ortho']
img=bpy.data.images['ortho2020.png']; print('PATH',bpy.path.abspath(img.filepath))
for lab,(cx,cy) in (('small',(21.6,136.5)),('big',(47.8,150.2))):
    best=min(me.polygons,key=lambda p:(p.center.x-cx)**2+(p.center.y-cy)**2)
    uv=sum((ul.data[li].uv for li in best.loop_indices),mathutils.Vector((0,0)))/3
    print('UVPIX',lab,int(uv.x*2048),int((1-uv.y)*2048))

import bpy, mathutils
sk=bpy.data.objects['OO_skirt_Center for Environmental and Life Sciences walls']; me=sk.data; M=sk.matrix_world
print('SK mods',[m.name for m in sk.modifiers], 'mats',[m.name for m in me.materials], sk.get('oo_src'), list(sk.keys()))
for p in me.polygons:
    vs=[M@me.vertices[i].co for i in p.vertices]; c=sum(vs,mathutils.Vector())/len(vs)
    if (abs(c.x-127.5)<3 and abs(c.y-196)<4) or (abs(c.x-129.8)<2 and abs(c.y-204.5)<3):
        print('F',p.index,[tuple(round(a,2) for a in v) for v in vs], tuple(round(a,2) for a in p.normal))
# also a camera-grid scan for see-through pixels
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['OR_CAM_eye_CELS_skirt_windows_base_course']; sc.camera=cam
fr=cam.data.view_frame(scene=sc); Mc=cam.matrix_world; tr,br,bl,tl=[Mc@p for p in fr]; o=Mc.translation
for py in range(60,400,20):
    row=''
    for px in range(0,1024,16):
        u=px/1024; v=py/576; p=tl.lerp(tr,u).lerp(bl.lerp(br,u),v); d=(p-o).normalized()
        h,l,n,i,ob,_=sc.ray_cast(dg,o,d)
        row+= ' ' if not h else ('#' if (l-o).length>40 else '.')
    print('R%03d'%py,row)

import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def probe(cn,pts):
    cam=bpy.data.objects[cn]; fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
    tr,br,bl,tl=[mw@v for v in fr]
    for px,py in pts:
        u=px/1024; v=py/576; p=tl+(tr-tl)*u+(bl-tl)*v; o=mw.translation.copy(); d=(p-o).normalized()
        r=sc.ray_cast(dg,o,d)
        if not r[0]: print('PX',cn[:20],px,py,None); continue
        ob=r[4]; mi=ob.material_slots[ob.data.polygons[r[3]].material_index].name if ob.type=='MESH' and ob.material_slots and r[3]<len(ob.data.polygons) else '-'
        print('PX',cn[:22],px,py,ob.name,r[3],mi,[round(x,2) for x in r[1]],[round(x,2) for x in r[2]])
probe('PK_CAM_oblique_feliciano_from_NW',[(225,150),(235,170),(250,185),(265,190),(240,215),(255,140),(300,175),(350,200),(370,230),(330,160)])
probe('PK_CAM_eye_feliciano_NW',[(415,20),(420,40),(428,60),(435,90),(450,10),(400,30),(460,5),(520,30)])

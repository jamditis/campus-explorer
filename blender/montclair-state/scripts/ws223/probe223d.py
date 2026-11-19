import bpy
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; M=L.matrix_world
S=set(range(260,269))|{150,160,140,142,132,152,170}
for p in L.data.polygons:
    if S & set(p.vertices):
        print('P223 f%d n=(%.2f,%.2f,%.2f) area %.3f %s'%(p.index,*p.normal,p.area,list(p.vertices)))

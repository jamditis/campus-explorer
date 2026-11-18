import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
cam=bpy.data.objects['QM_CAM_closeup_ccis_podium_edge_east']; sc.camera=cam
sc.render.resolution_x=1024; sc.render.resolution_y=576
fr=cam.data.view_frame(scene=sc); M=cam.matrix_world
tr,br,bl,tl=[M@v for v in fr]; o=M.translation
for (px,py) in ((830,445),(870,440),(900,438),(940,440),(860,446),(700,440)):
    u=px/1024; v=py/576
    p=tl+(tr-tl)*u+(bl-tl)*v
    ok,loc,n,i,ob,m=sc.ray_cast(dg,o,(p-o).normalized())
    ms=''
    if ok and ob.type=='MESH':
        e=ob.evaluated_get(dg); me=e.data
        if i<len(me.polygons): ms=me.materials[me.polygons[i].material_index].name if me.materials else ''
    print('HIT',(px,py),ok and [round(c,2) for c in loc],ob.name if ok else None,ok and [round(c,2) for c in n],i,ms)

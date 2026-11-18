import bpy
from mathutils import Vector
sc=bpy.context.scene; cam=bpy.data.objects['PV_CAM_closeup_dickson_north_toprow']; dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
W,H=768,432
for (px,py) in [(190,80),(230,95),(345,155),(420,170),(490,135),(530,150),(150,70)]:
    u=px/W; v=1-py/H
    p=fr[3]+(fr[0]-fr[3])*u  # fr: tr,br,bl,tl
    tl,tr,br,bl=fr[3],fr[0],fr[1],fr[2]
    pt=tl+(tr-tl)*u+(bl-tl)*(1-v)
    d=(mw@pt-mw.translation).normalized()
    hit,loc,nor,idx,ob,_=sc.ray_cast(dg,mw.translation,d)
    if hit:
        me=ob.data; mi=me.polygons[idx].material_index if ob.type=='MESH' and idx<len(me.polygons) else -1
        print('RAY',px,py,ob.name,tuple(round(x,2) for x in loc),tuple(round(x,2) for x in nor),ob.material_slots[mi].name if mi>=0 and ob.material_slots else '')
    else: print('RAY',px,py,'miss')

import bpy, os
from mathutils import Vector
sc=bpy.context.scene; cam=bpy.data.objects[os.environ['CAM']]; dg=bpy.context.evaluated_depsgraph_get()
W,H=640,360; sc.render.resolution_x=1920; sc.render.resolution_y=1080
tr,br,bl,tl=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]
for s in os.environ['PX'].split(';'):
    px,py=map(float,s.split(','))
    p=tl+(tr-tl)*(px/W); q=bl+(br-bl)*(px/W); p=p+(q-p)*(py/H)
    o0=cam.matrix_world.translation; d=(p-o0).normalized()
    for k in range(3):
        hit,loc,nor,idx,ob,_=sc.ray_cast(dg,o0,d)
        if not hit: print('RAY',s,'miss'); break
        mi=ob.data.polygons[idx].material_index if ob.type=='MESH' and idx<len(ob.data.polygons) else -1
        mn=ob.material_slots[mi].material.name if 0<=mi<len(ob.material_slots) and ob.material_slots[mi].material else None
        print('RAY',s,k,ob.name[:55],idx,mn,tuple(round(x,2) for x in loc),tuple(round(x,2) for x in nor))
        o0=loc+d*0.02

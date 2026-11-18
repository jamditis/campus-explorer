import bpy, os
from mathutils import Vector
sc=bpy.context.scene; cam=bpy.data.objects['QA_CAM_eye_feliciano_sw_slope']; dg=bpy.context.evaluated_depsgraph_get()
fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]; o=cam.matrix_world.translation
print('CAM',tuple(round(x,2) for x in o))
for (px,py) in [(20,470),(100,500),(200,550),(60,560),(260,570),(300,560),(150,480),(5,460)]:
    x=px/1024; y=py/576; top=fr[3]+(fr[0]-fr[3])*x; bot=fr[2]+(fr[1]-fr[2])*x; p=top+(bot-top)*y
    hit,loc,nor,idx,ob,mx=sc.ray_cast(dg,o,(p-o).normalized())
    # what is directly below/above at that xy
    zs=[]
    q=Vector((loc.x,loc.y,300)); 
    for k in range(6):
        h2=sc.ray_cast(dg,q,Vector((0,0,-1)))
        if not h2[0]: break
        zs.append((h2[4].name[:40],round(h2[1].z,2))); q=h2[1]-Vector((0,0,0.002))
    print('SK',px,py,ob and ob.name,tuple(round(v,2) for v in loc),'dist %.1f'%(loc-o).length,zs)

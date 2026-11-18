import bpy
from mathutils import Vector
sc=bpy.context.scene; sc.render.resolution_x=1024; sc.render.resolution_y=576
cam=bpy.data.objects['PK_CAM_oblique_feliciano_from_NW']; dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
def ray(px,py):
    u=px/1024; v=1-py/576
    tl,bl=fr[1],fr[2]; tr,br=fr[0],fr[3]  # view_frame order: TR,BR,BL,TL
    tr,br,bl,tl=fr
    p=bl+(br-bl)*u+(tl-bl)*v; d=(mw.to_3x3()@p).normalized()
    r=sc.ray_cast(dg,mw.translation,d)
    return r
out=[]
for (x,y) in [(740,250),(800,235),(850,220),(900,210),(950,200),(1000,192),(800,260),(800,215),(900,230),(900,190),(120,440),(130,470)]:
    r=ray(x,y); out.append('%d,%d hit=%s obj=%s loc=%s'%(x,y,r[0],r[4].name if r[0] else None,tuple(round(c,2) for c in r[1]) if r[0] else None))
open('data/pz/probe_step.txt','w').write('\n'.join(out)); print('\n'.join(out))

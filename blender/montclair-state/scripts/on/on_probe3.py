import bpy
from mathutils import Vector
sc=bpy.context.scene
w=bpy.data.objects['Schmitt Hall walls']; me=w.data; M=w.matrix_world
C=Vector((-15.67,117.09)); A=Vector((0.396,0.918)); N=Vector((-0.918,0.396))
win=bpy.data.objects['SCH_win_104_r2']
print('WIN', tuple(round(v,2) for v in win.matrix_world.translation), [ (o.name, tuple(round(d,2) for d in o.dimensions)) for o in win.instance_collection.all_objects][:6])
for f in me.polygons:
    vs=[M@me.vertices[i].co for i in f.vertices]
    cc=sum(vs,Vector())/len(vs)
    p=Vector((cc.x,cc.y))-C
    if abs(p.dot(A))<1.3 and -1.0<p.dot(N)<0.6 and 145.5<cc.z<149.5:
        print('F',f.index,len(vs),tuple(round(n,2) for n in f.normal),round(f.area,3),[ (round((Vector((v.x,v.y))-C).dot(A),2),round((Vector((v.x,v.y))-C).dot(N),2),round(v.z,2)) for v in vs])
# rays for dark void from test cam 2
cam_o=Vector((-13.6,105.5,143.0)); tgt=Vector((-15.7,117.1,146.8))
dg=bpy.context.evaluated_depsgraph_get()
import math
d0=(tgt-cam_o).normalized()
q=d0.to_track_quat('-Z','Y'); R=q.to_matrix()
fw=36/35/2  # half sensor/lens
for px,py in [(140,150),(120,170),(160,120),(130,110)]:
    u=(px/640-0.5)*2*fw; v=-(py/360-0.5)*2*fw*360/640
    d=(R@Vector((u,v,-1))).normalized()
    hit,loc,nor,idx,ob,mx=sc.ray_cast(dg,cam_o,d)
    print('R',px,py,hit,ob.name if ob else None,tuple(round(c,2) for c in loc),tuple(round(c,2) for c in nor))

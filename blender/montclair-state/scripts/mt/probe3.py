import bpy
from mathutils import Vector
n=Vector((-0.970,0.242,0)).normalized()
sh=bpy.data.objects['CCOM tower 4a shaft (one volume, OSM+LiDAR)']
mw=sh.matrix_world
for p in sh.data.polygons:
    nw=(mw.to_3x3()@p.normal).normalized()
    if nw.dot(n)>0.9 and p.area>1:
        vs=[mw@sh.data.vertices[i].co for i in p.vertices]
        print('FACE area',round(p.area,2),'n',tuple(round(x,3) for x in nw),'verts',[tuple(round(c,3) for c in v) for v in vs])
tr=bpy.data.objects['CCOM tower 4a trim (belfry band, arch surrounds)']
mw=tr.matrix_world
zs=sorted(set(round((mw@v.co).z,2) for v in tr.data.vertices if 146<(mw@v.co).z<151.5 and (mw@v.co).x<-18.5))
print('TRIMZ',zs)
for nm in ['CCOM tower 4a lettering COLLEGE OF','CCOM tower 4a lettering COMMUNICATION AND MEDIA']:
    o=bpy.data.objects[nm]; print('LET',nm,tuple(o.location))

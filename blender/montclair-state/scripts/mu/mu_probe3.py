import bpy
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
for nm in ['Downspouts (3f)','Gutters half-round (3f, Life/CCOM UNVERIFIED)']:
    o=bpy.data.objects[nm]; mw=o.matrix_world
    vs=[mw@v.co for v in o.data.vertices]
    near=[v for v in vs if 1.0<v.dot(t)<13.5 and 21.5<v.dot(n)<24 and 140<v.z<148]
    if near: print(nm,len(near),'u',round(min(v.dot(t) for v in near),3),round(max(v.dot(t) for v in near),3),'w',round(min(v.dot(n) for v in near),3),round(max(v.dot(n) for v in near),3),'z',round(min(v.z for v in near),3),round(max(v.z for v in near),3))
    # clusters by u
    us=sorted(set(round(v.dot(t),1) for v in near)); print(' us',us[:60])

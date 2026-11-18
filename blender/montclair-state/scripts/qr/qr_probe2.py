import bpy
from mathutils import Vector
o=bpy.data.objects['QP_Richardson_white_corner_towers_UNVERIFIED']; me=o.data; MW=o.matrix_world; CTR=Vector((84,264,0))
print('MW',MW.translation)
for f in me.polygons:
    cs=[MW@me.vertices[i].co for i in f.vertices]; zs=[c.z for c in cs]
    if abs(f.normal.z)>0.1 or max(zs)>157.05: continue
    m=sum(cs,Vector())/len(cs); m.z=0; n=MW.to_3x3()@f.normal
    print(len(cs),round(min(zs),2),round(max(zs),2),[round(c,2) for c in m.xy],[round(c,2) for c in n],round(n.dot((m-CTR).normalized()),2))

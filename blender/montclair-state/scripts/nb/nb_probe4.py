import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
loc=Vector((-6.74,-0.10,143.56)); tgt=Vector((-8.44,3.66,142.76)); f=18; W,H=768,432
fw=(tgt-loc).normalized(); r=fw.cross(Vector((0,0,1))).normalized(); up=r.cross(fw)
for px,py in ((150,100),(250,120),(60,150),(250,200),(30,60)):
    x=(px/W-0.5)*36; y=(0.5-py/H)*36*H/W
    dr=(fw*f+r*x+up*y).normalized(); o=loc.copy()
    for k in range(3):
        h=sc.ray_cast(dg,o,dr)
        if not h[0]: print('HIT',px,py,k,None); break
        m=h[4].material_slots[h[4].data.polygons[h[3]].material_index].material.name if h[4].type=='MESH' and h[4].material_slots else None
        print('HIT',px,py,k,h[4].name,m,[round(c,2) for c in h[1]]); o=h[1]+dr*0.002

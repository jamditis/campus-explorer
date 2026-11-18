# Session iy probe (read-only): which bowl faces are the dark wedges in the close-up? ray-cast pixels of the closeup camera.
import bpy, mathutils, math, numpy as np
LOC=mathutils.Vector((-165.3,7.2,134.5)); TGT=mathutils.Vector((-167.8,18,137.0)); LENS=32; W,H=768,432; SW=36
d=(TGT-LOC).normalized(); rot=d.to_track_quat('-Z','Y').to_matrix()
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data; names=[s.material.name for s in ob.material_slots]
fl=me.attributes.get('iy_wedge')
for px,py in [(317,340),(312,345),(322,335),(342,305),(355,282),(367,263),(270,340),(290,330)]:
    x=(px+0.5-W/2)/W*SW; y=-(py+0.5-H/2)/W*SW
    ray=(rot@mathutils.Vector((x,y,-LENS))).normalized()
    hit,loc,nrm,fi,o,_=sc.ray_cast(dg,LOC,ray)
    if hit and o.name==ob.name:
        p=me.polygons[fi]; zs=[(me.vertices[v].co.z-132.45)/((141.3-132.45)/19) for v in p.vertices]
        print('IYP',px,py,'face',fi,names[p.material_index],'n',[round(c,2) for c in p.normal],'tilt',round(math.degrees(math.acos(max(-1,min(1,p.normal.z)))),1),'lv',[round(z,2) for z in zs],'area',round(p.area,4),'wedge',fl.data[fi].value if fl else None)
    else: print('IYP',px,py,'hit',hit,o.name if o else None)

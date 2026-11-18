import bpy
from mathutils import Vector
c=Vector((-105.7,199.06))
for n in ('PR_Calcia_slot_surrounds_UNVERIFIED','PS_Calcia_slot_reveals_glass_UNVERIFIED','PE_Calcia_slot_surrounds_UNVERIFIED'):
    o=bpy.data.objects.get(n)
    if not o: print('4A',n,'absent'); continue
    k=sum(1 for p in o.data.polygons if ((o.matrix_world@p.center).xy-c).length<0.9)
    print('4A',n,'polys within 0.9 m of the new bay',k)
q=bpy.data.objects['QC_Calcia_cornerbay_frames_reveals_glass_UNVERIFIED']; w=bpy.data.objects['Calcia Hall walls']
# coplanar test: any QC face whose plane+extent coincides with a wall face (distance<2mm along normal, same normal)
import mathutils
wp=[(w.matrix_world@p.center,(w.matrix_world.to_3x3()@p.normal).normalized()) for p in w.data.polygons]
cop=0
for p in q.data.polygons:
    pc=q.matrix_world@p.center; pn=p.normal
    for (c2,n2) in wp:
        if abs(abs(pn.dot(n2))-1)<1e-3 and abs((pc-c2).dot(n2))<0.0015 and (pc-c2).length<1.0: cop+=1
print('4A coplanar QC-vs-wall faces',cop)

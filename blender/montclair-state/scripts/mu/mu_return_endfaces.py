# Session mu: end faces (+/-u) of the eave-return tile caps -> dark-wood end board (tile texture read as stripes on the end grain).
import bpy
from mathutils import Vector
t=Vector((0.232,0.972,0)).normalized()
for o in bpy.data.collections['MS_CCOM_gable_eave_returns_20261029mu'].objects:
    if 'tile cap' not in o.name: continue
    if 'Eave_fascia_dark_wood' not in [m.name for m in o.data.materials]: o.data.materials.append(bpy.data.materials['Eave_fascia_dark_wood'])
    k=0
    for p in o.data.polygons:
        nw=(o.matrix_world.to_3x3()@p.normal).normalized()
        if abs(nw.dot(t))>0.9: p.material_index=1; k+=1
    print('ENDF',o.name,k)
print('COUNT',len(bpy.data.objects)); bpy.ops.wm.save_mainfile(); print('SAVED')

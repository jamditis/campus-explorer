import bpy
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; me=o.data
fm=bpy.data.materials['Eave_fascia_dark_wood']
if fm.name not in [m.name for m in me.materials if m]: me.materials.append(fm)
idx=[i for i,m in enumerate(me.materials) if m and m.name==fm.name][0]
for f in (6,14):
    p=me.polygons[f]; assert p.material_index==1 and abs(p.normal.z)<0.01, (f,p.material_index)
    p.material_index=idx
me.update(); print('FASCIA slot',idx); bpy.ops.wm.save_mainfile(); print('SAVED')

import bpy
S=bpy.data.materials['WS25_Partridge_soffit_stucco_JoePhoto']
S.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.15,0.03,0.028,1)
S.name='WS25_Partridge_soffit_burgundy_JoePhoto'
f=bpy.data.objects['WS25_Partridge_eave_fascia_burgundy_UNVERIFIED']; print('FASCIA',[s.material.name for s in f.material_slots], f.data.polygons[0].normal)
bpy.ops.wm.save_mainfile(); print('SAVED')

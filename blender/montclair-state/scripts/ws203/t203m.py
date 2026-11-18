import bpy
o=[x for x in bpy.data.objects if x.name.startswith('WS163_Lot3_aisle_S_drive')][0]
m=bpy.data.materials.new('T203grey'); m.use_nodes=True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.18,0.18,0.18,1)
o.material_slots[0].material=m
mt=o.data.materials
print('F203m mat swapped',flush=True)

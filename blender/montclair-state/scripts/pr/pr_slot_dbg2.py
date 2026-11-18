import bpy
m=bpy.data.materials['PE_Calcia_brick_slot_windows_UNVERIFIED']; a=m.node_tree.nodes['Attribute']; print('ATTR',a.attribute_type,a.attribute_name)
w=bpy.data.objects['Calcia Hall walls']; print('OBJPROPS',{k:w[k] for k in w.keys() if not k.startswith('_')}, [a.name+':'+a.domain for a in w.data.attributes])
for s in w.material_slots: print('SLOT',s.link,s.material.name if s.material else None)
print('MODS',[(md.name,md.type) for md in w.modifiers])

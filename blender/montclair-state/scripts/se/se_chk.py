import bpy
m=bpy.data.materials['SE_SC_membrane_seams_dirt_UNVERIFIED']; b=m.node_tree.nodes['Principled BSDF']
print('SE_CHK users',m.users,'basecolor from',b.inputs['Base Color'].links[0].from_node.name if b.inputs['Base Color'].is_linked else None)
for ob in bpy.data.objects:
    if ob.name.startswith('StudentCenter L'): print('SE_CHK',ob.name[:20],[s.material.name for s in ob.material_slots])

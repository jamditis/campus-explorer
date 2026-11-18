import bpy
m=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']
print('TJSIG',len(bpy.data.objects),len(bpy.data.materials),len(bpy.data.meshes),len(m.node_tree.nodes),m.node_tree.nodes['QV_gm'].inputs[0].links[0].from_node.name,
 sorted((o.name,o.data.materials[0].name) for o in bpy.data.objects if o.name.startswith('TI_') and o.type=='MESH'),bpy.data.materials['TI_dorm_wall_windows_UNVERIFIED'].use_fake_user)

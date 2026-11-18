import bpy
m=bpy.data.materials['North_StudentCenter_membrane_UNVERIFIED']
for n in m.node_tree.nodes:
    if n.type=='TEX_IMAGE': print('SE_IMG',n.image and n.image.name, n.image and n.image.filepath, n.image and n.image.packed_file is not None, n.image and n.image.users)
for mm in bpy.data.materials:
    if mm.use_nodes and any(n.type=='TEX_IMAGE' and n.image==[x for x in m.node_tree.nodes if x.type=='TEX_IMAGE'][0].image for n in mm.node_tree.nodes): print('SE_USER',mm.name,mm.users)

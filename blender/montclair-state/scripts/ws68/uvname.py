import bpy
for n in bpy.data.materials['Ground_ortho_grass'].node_tree.nodes:
    if n.type=='UVMAP': print('UVN',n.name,n.uv_map)

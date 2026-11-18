import bpy
N=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED'].node_tree.nodes
print('TJCHK max1 in0',N['TJ_max1'].inputs[0].links[0].from_node.name if 'TJ_max1' in N else None)

import bpy,os
m=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']; N=m.node_tree.nodes; L=m.node_tree.links
nn=os.environ['DBG']; src=N[nn]; out=src.outputs[0]
b=N['Principled BSDF']; L.new(out,b.inputs['Base Color']); print('DBG',nn)
for k in ('Math','Math.001'): print('OP',k,N[k].operation)

exec(open('scripts/ts/ts_main.py').read())
import bpy
m=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']; N=m.node_tree.nodes; L=m.node_tree.links
d=N.new('ShaderNodeBsdfDiffuse'); d.inputs['Color'].default_value=(0.03,0.04,0.025,1)
L.new(d.outputs[0],N['Material Output'].inputs['Surface']); print('DBG4 diffuse dark')

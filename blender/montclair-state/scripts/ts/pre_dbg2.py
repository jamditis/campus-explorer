exec(open('scripts/ts/ts_main.py').read())
import bpy
m=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']; N=m.node_tree.nodes; L=m.node_tree.links
e=N.new('ShaderNodeEmission'); e.inputs['Color'].default_value=(0,0,0,1)
L.new(e.outputs[0],N['Material Output'].inputs['Surface']); print('DBG2 black emission')

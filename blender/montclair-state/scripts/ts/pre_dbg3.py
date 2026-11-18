exec(open('scripts/ts/ts_main.py').read())
import bpy
m=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']; N=m.node_tree.nodes; L=m.node_tree.links
b=N['Principled BSDF']
for l in list(b.inputs['Normal'].links): L.remove(l)
print('DBG3 no normal')

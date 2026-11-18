import bpy
# quatrefoil reads near-white against the field in aerial A (shadowed band ~1.6x the field) -> brighten so it keeps contrast on the lighter field
m=bpy.data.materials['WS5_Quatrefoil_inlay_light_stone']
for n in m.node_tree.nodes:
  if n.type=='VALTORGB': n.color_ramp.elements[0].color=(0.70,0.69,0.66,1); n.color_ramp.elements[1].color=(0.84,0.83,0.80,1)
# a touch more paver-to-paver tone variation on the field
p=bpy.data.materials['WS8_Grey_pavers_plaza_sunlit_sampled']
for n in p.node_tree.nodes:
  if n.type=='VALTORGB': n.color_ramp.elements[0].color=(0.245,0.241,0.236,1); n.color_ramp.elements[1].color=(0.375,0.370,0.362,1)
bpy.ops.wm.save_mainfile(); print('SAVED2')

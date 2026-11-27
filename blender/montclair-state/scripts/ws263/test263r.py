# ws263 debug (subset CHAIN, render to renders/test): paint the W263 layers pure red/blue to see where the mask lands
import bpy
m=bpy.data.materials.get('WS68_Ground_ortho_grass_north2020'); N=m.node_tree.nodes
N['W263_soil_mix'].inputs['B'].default_value=(1,0,0,1); N['W263_fac_thatch'].inputs[1].default_value=1.0
N['W263_litter_mix'].inputs['B'].default_value=(0,0,1,1); N['W263_fac_humus'].inputs[1].default_value=1.0
im=bpy.data.images['W263_police_grass_density263']; f=open('/workspace/nj-scenes/montclair-state/scripts/ws263/test263r.out','w'); print('T263R img',im.size[:],im.has_data,im.packed_file is not None,max(list(im.pixels)[0::4]),file=f,flush=True)
print('T263R litter mix fac link',[ (l.from_node.name) for l in N['WR_litter_mix'].inputs['Fac'].links],file=f,flush=True)

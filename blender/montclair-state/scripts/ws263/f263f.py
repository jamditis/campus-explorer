# ws263 (merge208 CHAIN, after f263e): close-up on ws263e still read grey between blades (the ortho under the slope is very pale),
# so strengthen the W263 layer: thatch mix 0.35 -> 0.70 of the mask, olive multiply (0.46,0.56,0.30) -> (0.40,0.50,0.24),
# litter humus mix 0.40 -> 0.65.
import bpy
TAG='F263F'
for mn in ('WS68_Ground_ortho_grass_north2020','North_ground_ortho2020.001'):
    N=bpy.data.materials[mn].node_tree.nodes
    N['W263_fac_thatch'].inputs[1].default_value=0.70; N['W263_olive_mul'].inputs['B'].default_value=(0.40,0.50,0.24,1)
    print(TAG,'strengthened',mn,flush=True)
bpy.data.materials['WS68_Ground_ortho_grass_north2020'].node_tree.nodes['W263_fac_humus'].inputs[1].default_value=0.65

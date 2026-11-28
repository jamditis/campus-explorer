# ws273 f273c (merge208 CHAIN on ws273b): extend the #4b lawn box N to y -100 so the pocket's N tip under the lot's diagonal S edge
# (Terrain regrid faces above the lot fill there, still showing the 2020 roof in the ortho) also gets the grandstand lawn.
import bpy
ng=bpy.data.node_groups['WS273_lot_pocket_S_terrain_lawn_material']; n=0
for nd in ng.nodes:
    if nd.bl_idname=='FunctionNodeCompare' and abs(nd.inputs[1].default_value-(-105.5))<1e-3:
        nd.inputs[1].default_value=-100.0; n+=1
print('F273C ymax changed',n,flush=True)
assert n==1

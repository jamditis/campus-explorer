import bpy,runpy
runpy.run_path('scripts/wn/wn_fix.py')
m=bpy.data.materials['TR_Stone_brick_detail_UNVERIFIED']; N=m.node_tree.nodes; L=m.node_tree.links
mix=N['WN_mix']
for l in list(mix.inputs['Factor'].links): L.remove(l)
L.new(N[__import__('os').environ['DBGN']].outputs[0],mix.inputs['Factor']); mix.inputs[7].default_value=(1,0,0,1)
P=[n for n in N if n.type=='BSDF_PRINCIPLED'][0]
print('BC from',[l.from_node.name for l in P.inputs['Base Color'].links], 'emission',P.inputs['Emission Strength'].default_value,flush=True)
# which object does the camera centre hit?
import mathutils
runpy.run_path('scripts/wl/wl_render.py')

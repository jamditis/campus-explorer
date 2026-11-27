# ws267 (merge208 CHAIN, on ws267b): the ws267a lawn blades in the police S terrace bed stand on ge_bed_soil, a pale grey-brown
# soil that reads as bald patches between blades in the close-up. Real lawn shows dark olive thatch between blades (same design
# call as ws263's W263 layer on the police lawn). Only if ge_bed_soil is used by the terrace bed alone: tint its base colour
# toward the W263 olive and make it matte (roughness 1, specular 0.1). Tone UNVERIFIED (no close photo).
import bpy
TAG='F267C'
M=bpy.data.materials['ge_bed_soil']
users=[o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material==M for s in o.material_slots)]
print(TAG,'users',users,flush=True)
if users!=['ge_police_terrace_bed']: raise SystemExit('F267C ge_bed_soil shared, not changed')
if M.get('ws267c'): raise SystemExit('F267C already applied')
if not M.use_nodes: M.use_nodes=True
nt=M.node_tree; bs=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED']
print(TAG,'nodes',[(n.name,n.type) for n in nt.nodes],flush=True)
b=bs[0]; bc=b.inputs['Base Color']; OL=(0.055,0.065,0.025,1.0)
if bc.is_linked:
    src=bc.links[0].from_socket; mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MIX'; mx.name='W267_olive'
    mx.inputs['Factor'].default_value=0.8; mx.inputs[7].default_value=OL
    nt.links.new(src,mx.inputs[6]); nt.links.new(mx.outputs[2],bc); print(TAG,'linked base -> mixed 0.8 olive',flush=True)
else:
    old=tuple(bc.default_value); bc.default_value=tuple(0.2*o+0.8*n for o,n in zip(old,OL)); print(TAG,'base',old,'->',tuple(bc.default_value),flush=True)
b.inputs['Roughness'].default_value=1.0
for k in ('Specular IOR Level','Specular'):
    if k in b.inputs: b.inputs[k].default_value=0.1
for l in list(nt.links):
    if l.to_node==b and l.to_socket.name in ('Roughness',): nt.links.remove(l)
M['ws267c']=1; print(TAG,'done',flush=True)

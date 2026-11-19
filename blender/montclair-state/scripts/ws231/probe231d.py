import bpy,os,sys
M='/workspace/nj-scenes/montclair-state/'
with bpy.data.libraries.load(M+'montclair_state_ws231a.blend',link=False) as (src,dst): dst.node_groups=['QK_NE_end_drape_GN']
ng=dst.node_groups[0]
for l in ng.links: print('P231D',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.identifier,flush=True)
for n in ng.nodes:
    if n.bl_idname=='GeometryNodeRaycast': print('P231D RC',n.name,[ (i.identifier,tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if not i.is_linked and hasattr(i,'default_value')],flush=True)
sys.stdout.flush(); os._exit(0)

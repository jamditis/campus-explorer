# ws263 (NO SAVE): materials on the ground under the police-lawn grass (pale soil tone between blades) + grass GN material
import bpy
TAG='P263C'
for on in ('WS68_RHD_ground_northDTM','M3b_north_LiDAR_DTM_1m_west_rail_corridor','gd_grass_police_lawn_points'):
    o=next((x for x in bpy.data.objects if x.name.startswith(on)),None)
    if not o: print(TAG,'missing',on); continue
    print(TAG,'OBJ',on,'mats',[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else None,'users_mat',[ (m.name,m.users) for m in o.data.materials if m],'mods',[(m.type,m.name,getattr(m,'node_group',None) and m.node_group.name) for m in o.modifiers],flush=True)
    for m in o.data.materials:
        if not m or not m.use_nodes: continue
        for n in m.node_tree.nodes:
            ex=''
            if n.type=='TEX_IMAGE' and n.image: ex=n.image.name+' '+n.image.filepath+' '+n.image.colorspace_settings.name
            print(TAG,' N',m.name,n.name,n.type,ex,flush=True)
        for l in m.node_tree.links: print(TAG,' L',m.name,l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name,flush=True)
import os; os._exit(0)

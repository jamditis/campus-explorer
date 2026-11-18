import bpy
for n in ('SF_asphalt_worn_UNVERIFIED','SG_oil_stain_UNVERIFIED','SG_curb_concrete_UNVERIFIED'):
    m=bpy.data.materials.get(n); print('MAT',n,m and m.users)
    if not m: continue
    for nd in m.node_tree.nodes:
        ins={i.name:(tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in nd.inputs if hasattr(i,'default_value') and not i.is_linked and i.name in('Base Color','Roughness','Specular IOR Level','Fac','Color1','Color2','Scale','Alpha','Strength','Detail','Distortion','Value','From Min','From Max','To Min','To Max')}
        print('  N',nd.name,nd.bl_idname,getattr(nd,'blend_type',''),ins)
    for l in m.node_tree.links: print('  L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
for o in bpy.data.objects:
    if o.type=='MESH' and o.data.materials and any(mm and mm.name=='SF_asphalt_worn_UNVERIFIED' for mm in o.data.materials): print('USER',o.name,o.hide_render)

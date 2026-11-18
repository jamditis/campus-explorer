import bpy
sc=bpy.context.scene; vs=sc.view_settings
print('VIEW',vs.view_transform,vs.look,vs.exposure,vs.gamma, sc.render.engine)
w=sc.world; print('WORLD',w.name)
for nd in w.node_tree.nodes:
    ins={i.name:(round(i.default_value,3) if isinstance(i.default_value,float) else '') for i in nd.inputs if not i.is_linked and hasattr(i,'default_value')}
    print(' ',nd.name,nd.type,{k:v for k,v in ins.items() if v!=''})
for l in w.node_tree.links: print('  L',l.from_node.name,'->',l.to_node.name,l.to_socket.name)
for o in bpy.data.objects:
    if o.type=='LIGHT': print('LIGHT',o.name,o.data.type,round(o.data.energy,2),tuple(round(c,2) for c in o.data.color),o.hide_render)
c=bpy.data.objects.get('TI_CAM_oblique_east_dorms_from_SW'); print('CAM',c.location if c else None)
print('fog?',[o.name for o in bpy.data.objects if 'haze' in o.name.lower() or 'fog' in o.name.lower() or 'mist' in o.name.lower()][:10])

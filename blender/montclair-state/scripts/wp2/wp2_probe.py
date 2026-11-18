import bpy, math
sc=bpy.context.scene
for o in bpy.data.objects:
    if o.type=='LIGHT' and o.data.type=='SUN':
        print('SUN',o.name,o.data.name,o.data.energy,tuple(o.data.color),o.data.angle,[round(math.degrees(a),1) for a in o.rotation_euler],o.hide_render,[c.name for c in o.users_collection], o.data.users)
w=sc.world
for n in w.node_tree.nodes:
    ins={i.name:(i.default_value if not hasattr(i.default_value,'__len__') else tuple(i.default_value)) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked}
    print('N',n.name,n.type,ins)
    if n.type=='TEX_SKY':
        print(' sky',n.sky_type,n.sun_disc,n.sun_size,n.sun_intensity,n.sun_elevation,n.sun_rotation,n.altitude,n.air_density,n.dust_density,n.ozone_density)
    if n.type=='MAPPING': print(' map rot',tuple(n.inputs['Rotation'].default_value))
for l in w.node_tree.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
print('VIEW',sc.view_settings.view_transform,sc.view_settings.look,sc.view_settings.exposure)
print('texts',[t.name for t in bpy.data.texts])
print('worlds',[x.name for x in bpy.data.worlds])

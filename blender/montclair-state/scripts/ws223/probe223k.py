import bpy
for o in bpy.data.objects:
    for m in o.modifiers:
        if m.type=='NODES' and m.node_group and m.node_group.name=='WS72_KasserSW_walk_cut': print('P223 user',o.name,m.name)
        if m.type=='NODES' and m.node_group:
            for n in m.node_group.nodes:
                if n.bl_idname=='GeometryNodeObjectInfo' and n.inputs[0].default_value and n.inputs[0].default_value.name=='WS72_cut_helper_hidden': print('P223 helperuser',o.name,m.name,m.node_group.name)
h=bpy.data.objects['WS72_cut_helper_hidden']; M=h.matrix_world
print('P223 helper nv',len(h.data.vertices),'np',len(h.data.polygons),'hide_render',h.hide_render, 'users', h.data.users)
for v in h.data.vertices:
    w=M@v.co
    if -250.5<=w.x<=-248 and -55.5<=w.y<=-53.8: print('P223 hv (%.3f,%.3f,%.3f)'%tuple(w))

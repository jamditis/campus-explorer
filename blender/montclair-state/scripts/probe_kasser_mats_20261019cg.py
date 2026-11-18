import bpy
for on in ['Alexander Kasser Theater walls','Alexander Kasser Theater roof (LiDAR)','Alexander Kasser Theater eave soffit + fascia + rafter tails','Alexander Kasser Theater barrel tile eave course']:
    o=bpy.data.objects[on]; print('CGM OBJ',on,[ (m.name, m.users) for m in o.data.materials if m])
seen=set()
for on in ['Alexander Kasser Theater roof (LiDAR)','Alexander Kasser Theater eave soffit + fascia + rafter tails','Alexander Kasser Theater barrel tile eave course','Alexander Kasser Theater walls']:
    for m in bpy.data.objects[on].data.materials:
        if not m or m.name in seen: continue
        seen.add(m.name)
        for nd in m.node_tree.nodes:
            ins={i.name:(tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in nd.inputs if hasattr(i,'default_value') and not i.is_linked and i.name in('Base Color','Color','Color1','Color2','A','B','Fac','Scale','Hue','Saturation','Value','Roughness')}
            extra=''
            if nd.type=='VALTORGB': extra=[(round(e.position,2),tuple(round(c,3) for c in e.color)) for e in nd.color_ramp.elements]
            if nd.type=='RGB': extra=tuple(round(c,3) for c in nd.outputs[0].default_value)
            print('CGM',m.name,'|',nd.name,nd.type,ins,extra)
        for l in m.node_tree.links: print('CGM L',m.name,l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)

"""vy: deep dump TR_Stone_brick_detail + TQ_Stone_buff_brick + who uses them."""
import bpy

def dump_mat(name):
    m = bpy.data.materials.get(name)
    if not m:
        print('MISSING', name); return
    print('====', name, 'users', m.users, '====')
    # objects using it
    for o in bpy.data.objects:
        if o.type!='MESH': continue
        for s in o.material_slots:
            if s.material == m:
                print('  used_by', o.name)
    nt = m.node_tree
    for nd in nt.nodes:
        print(f'NODE {nd.name} type={nd.type} loc=({nd.location.x:.0f},{nd.location.y:.0f})')
        if nd.type == 'VALTORGB':
            for i,e in enumerate(nd.color_ramp.elements):
                print(f'  ramp[{i}] pos={e.position:.4f} color={tuple(round(c,4) for c in e.color)}')
        if nd.type == 'RGB':
            print('  rgb', tuple(round(c,4) for c in nd.outputs[0].default_value))
        if nd.type == 'TEX_BRICK':
            for inp in ('Color1','Color2','Mortar','Scale','Mortar Size','Brick Width','Row Height'):
                try:
                    sock=nd.inputs[inp]
                    v=sock.default_value
                    if hasattr(v,'__len__'):
                        print(f'  {inp}={tuple(round(x,4) for x in v)}')
                    else:
                        print(f'  {inp}={v}')
                except Exception as e:
                    print(f'  {inp} ERR {e}')
        if nd.type == 'MAPPING':
            try:
                print('  scale', tuple(round(x,3) for x in nd.inputs['Scale'].default_value))
                print('  loc', tuple(round(x,3) for x in nd.inputs['Location'].default_value))
            except Exception: pass
        if nd.type == 'TEX_NOISE':
            try:
                print('  scale', nd.inputs['Scale'].default_value, 'detail', nd.inputs['Detail'].default_value)
            except Exception: pass
        if nd.type == 'BUMP':
            try:
                print('  strength', nd.inputs['Strength'].default_value, 'distance', nd.inputs['Distance'].default_value)
            except Exception: pass
        if nd.type == 'BSDF_PRINCIPLED':
            for inp in ('Base Color','Roughness','Specular IOR Level','Coat Weight','Alpha','Metallic'):
                try:
                    sock=nd.inputs[inp]
                    if sock.is_linked:
                        ln=sock.links[0]
                        print(f'  {inp} <- {ln.from_node.name}.{ln.from_socket.name}')
                    else:
                        v=sock.default_value
                        if hasattr(v,'__len__'):
                            print(f'  {inp}={tuple(round(x,4) for x in v)}')
                        else:
                            print(f'  {inp}={round(v,4)}')
                except KeyError:
                    pass
    print('LINKS:')
    for L in nt.links:
        print(f'  {L.from_node.name}.{L.from_socket.name} -> {L.to_node.name}.{L.to_socket.name}')

for n in ('TR_Stone_brick_detail_UNVERIFIED','TQ_Stone_buff_brick_UNVERIFIED','TQ_Stone_fascia_paint_UNVERIFIED','TR_Stone_sill_UNVERIFIED'):
    dump_mat(n)

# also dump VB brick briefly for pattern numbers we already have
print('=== North_Dickson_brick_buff_plain brick params (campus buff ref) ===')
m=bpy.data.materials.get('North_Dickson_brick_buff_plain')
if m:
    for nd in m.node_tree.nodes:
        if nd.type=='TEX_BRICK':
            print('color1', tuple(round(x,3) for x in nd.inputs['Color1'].default_value))
            print('color2', tuple(round(x,3) for x in nd.inputs['Color2'].default_value))
            print('mortar', tuple(round(x,3) for x in nd.inputs['Mortar'].default_value))
            print('scale', nd.inputs['Scale'].default_value, 'mortar_size', nd.inputs['Mortar Size'].default_value)

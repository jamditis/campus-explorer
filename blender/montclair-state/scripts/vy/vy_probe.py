"""vy: probe Stone Hall meshes/materials + Stone cams + Freeman VB cream brick pattern (read-only)."""
import bpy
print('=== STONE / TI / TQ objects ===')
for o in sorted(bpy.data.objects, key=lambda x: x.name):
    n = o.name
    if any(k in n for k in ('Stone', 'stone', 'TI_', 'TQ_')) and o.type in ('MESH','CAMERA','EMPTY'):
        if o.type == 'CAMERA':
            print('CAM', n)
            continue
        if o.type != 'MESH':
            continue
        if not any(k in n for k in ('Stone','stone','TI_Stone','TQ_Stone','TI_','TQ_')):
            continue
        # filter to stone-ish
        if not any(k in n.lower() for k in ('stone','ti_','tq_')):
            continue
        mats=[s.material.name if s.material else None for s in o.material_slots]
        # only print if Stone in name or stone-related mats
        if 'Stone' in n or 'stone' in n or any(m and ('Stone' in m or 'stone' in m or 'TI_' in m or 'TQ_' in m) for m in mats):
            print('OBJ', n, 'hideR' if o.hide_render else 'vis', 'dim', tuple(round(x,2) for x in o.dimensions), 'mats', mats)

print('=== STONE-RELATED MATERIALS ===')
seen=set()
for m in bpy.data.materials:
    if m.name in seen: continue
    if any(k in m.name for k in ('Stone','stone','TI_','TQ_','buff','Buff','cream','Cream','brick','Brick')):
        # skip unrelated campus bricks somewhat
        if not any(k in m.name for k in ('Stone','stone','TI_','TQ_','VB_','Freeman')) and 'brick' in m.name.lower():
            if 'Bohn' in m.name or 'Blanton' in m.name or 'Webster' in m.name:
                continue
        seen.add(m.name)
        if not m.use_nodes:
            print('MAT', m.name, 'NO_NODES', 'users', m.users); continue
        b=m.node_tree.nodes.get('Principled BSDF')
        if not b:
            print('MAT', m.name, 'no BSDF', 'users', m.users); continue
        bc=b.inputs['Base Color']
        linked = bc.is_linked
        src = None
        if linked:
            src = bc.links[0].from_node.name + '/' + bc.links[0].from_socket.name
        print('MAT', m.name, 'BC', tuple(round(x,3) for x in bc.default_value), 'linked' if linked else 'flat', 'src', src,
              'rough', round(b.inputs['Roughness'].default_value,3), 'users', m.users)
        # list interesting nodes
        interesting=[]
        for nd in m.node_tree.nodes:
            if nd.type in ('TEX_BRICK','TEX_NOISE','TEX_IMAGE','TEX_CHECKER','BUMP','MAPPING','TEX_COORD','MIX','VALTORGB','RGB'):
                interesting.append(f'{nd.name}({nd.type})')
        if interesting:
            print('  nodes:', ', '.join(interesting[:20]))

print('=== STONE CAMS (preferred list) ===')
wanted=[
 'TQ_CAM_eye_Stone_from_W','TQ_CAM_eye_Stone_from_NW','TQ_CAM_closeup_Stone_brick_fascia',
 'TI_CAM_eye_Stone_from_N','TI_CAM_oblique_east_dorms_from_SW','TR_CAM_closeup_Stone_sill_plinth',
]
for n in wanted:
    o=bpy.data.objects.get(n)
    print('  ', n, 'OK' if o else 'MISSING')

print('=== any CAM with Stone ===')
for o in bpy.data.objects:
    if o.type=='CAMERA' and 'Stone' in o.name:
        print('  ', o.name)

print('=== Freeman VB cream brick (pattern ref, DO NOT COPY) ===')
for m in bpy.data.materials:
    if 'VB' in m.name and ('cream' in m.name.lower() or 'brick' in m.name.lower() or 'Freeman' in m.name):
        print('VB_MAT', m.name, 'users', m.users)
        if m.use_nodes:
            for nd in m.node_tree.nodes:
                if nd.type in ('TEX_BRICK','TEX_NOISE','BUMP','MAPPING','MIX','VALTORGB','RGB'):
                    extra=''
                    if nd.type=='TEX_BRICK':
                        try:
                            extra=f' color1={tuple(round(x,3) for x in nd.inputs["Color1"].default_value)} color2={tuple(round(x,3) for x in nd.inputs["Color2"].default_value)} mortar={tuple(round(x,3) for x in nd.inputs["Mortar"].default_value)} scale={nd.inputs["Scale"].default_value:.2f} mortar_size={nd.inputs["Mortar Size"].default_value:.4f}'
                        except Exception as e:
                            extra=str(e)
                    if nd.type=='RGB':
                        extra=f' {tuple(round(x,3) for x in nd.outputs[0].default_value)}'
                    if nd.type=='VALTORGB':
                        try:
                            els=[tuple(round(c,3) for c in e.color) for e in nd.color_ramp.elements]
                            extra=f' ramp={els}'
                        except Exception: pass
                    print(f'   {nd.name}({nd.type}){extra}')
print('OBJS', len(bpy.data.objects))

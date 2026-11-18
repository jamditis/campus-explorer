import bpy, re, collections
w=bpy.context.scene.world
print('WORLD', w.name if w else None)
if w and w.use_nodes:
    for n in w.node_tree.nodes: print('  WN', n.type, n.name, getattr(n,'sky_type',''), getattr(n,'sun_elevation',''))
for m in bpy.data.materials:
    if 'Freeman' in m.name and ('glass' in m.name.lower() or 'sky' in m.name.lower()):
        b=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
        users=m.users
        if b:
            g=lambda k: (round(b.inputs[k].default_value,3) if k in b.inputs and not hasattr(b.inputs[k].default_value,'__len__') else None)
            print('GM', m.name, 'u',users, 'A',g('Alpha'),'T',g('Transmission Weight'),'R',g('Roughness'),'M',g('Metallic'),'Spec',g('Specular IOR Level'),'IOR',g('IOR'),'Coat',g('Coat Weight'),'base',tuple(round(x,3) for x in b.inputs['Base Color'].default_value), 'blend', getattr(m,'blend_method',None), getattr(m,'surface_render_method',None))
cnt=collections.Counter(); vis=collections.Counter()
for o in bpy.data.objects:
    mm=re.match(r'(V[A-Z])_Freeman_W_interbay',o.name)
    if mm:
        cnt[mm.group(1)]+=1
        if not o.hide_render: vis[mm.group(1)]+=1
print('IBAY', dict(cnt), 'visible', dict(vis))
# objects using W glass
wg=bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
print('WGLASS objs', [o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material==wg for s in o.material_slots)][:10])
print('NOBJ', len(bpy.data.objects))

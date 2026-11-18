import bpy
o=bpy.data.objects['TI_Stone_Hall_313028565_lower_UNVERIFIED']
print('MATS',[ (s.material.name if s.material else None) for s in o.material_slots])
for s in o.material_slots:
    m=s.material
    if not m: continue
    users=[ob.name for ob in bpy.data.objects if any(ss.material==m for ss in getattr(ob,'material_slots',[]))]
    print('MAT',m.name,'users',len(users),users[:8])
    out=[n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL']
    print(' nodes',len(m.node_tree.nodes),[ (n.name,n.type) for n in m.node_tree.nodes][:40])
    for n in out:
        l=n.inputs['Surface'].links
        print(' out<-',[x.from_node.name for x in l])
for n in ['WM_Stone_foundation_reveal_UNVERIFIED','TR_Stone_window_sills_UNVERIFIED']:
    ob=bpy.data.objects.get(n); print(n, ob and [s.material.name for s in ob.material_slots if s.material])
print('HIGH', [ob.name for ob in bpy.data.objects if 'Stone_Hall' in ob.name])

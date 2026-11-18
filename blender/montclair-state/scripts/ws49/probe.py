import bpy
p=bpy.data.objects['MID_street_tree_proto_20261015ag']; m=p.data.materials[0] if p.data.materials else None
print('P49 mat',m and m.name, m and m.use_nodes)
if m and m.use_nodes:
    for n in m.node_tree.nodes:
        if n.type=='BSDF_PRINCIPLED': print('P49 bsdf',tuple(round(v,3) for v in n.inputs['Base Color'].default_value), 'linked',n.inputs['Base Color'].is_linked, 'rough',n.inputs['Roughness'].default_value)
        else: print('P49 node',n.type,n.name)
print('P49 cams',[o.name for o in bpy.data.objects if o.type=='CAMERA' and 'cole' in o.name.lower()][:30])

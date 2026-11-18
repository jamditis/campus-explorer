import bpy
for o in bpy.data.objects:
    if o.get('tx_obj') and o.type=='MESH':
        print('CHK',o.name[:40],[ (m.name, tuple(round(v,3) for v in m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:3])) for m in o.data.materials])
for m in bpy.data.materials:
    if m.name.startswith('TX_'): print('MAT',m.name,m.users)

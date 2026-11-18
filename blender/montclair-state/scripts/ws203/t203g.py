import bpy
m=bpy.data.materials.new('T203grey'); m.use_nodes=True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.18,0.18,0.18,1)
n=0
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith(('WS75_','WS80_','WS94_','WS81_','WS76_','WS199_','WS82')):
        for s in o.material_slots:
            if s.material and 'paint' not in s.material.name.lower() and 'line' not in s.material.name.lower(): s.material=m; n+=1
print('F203g swapped',n,flush=True)

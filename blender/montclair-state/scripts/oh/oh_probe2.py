import bpy
m=bpy.data.materials['Roof_tile_or_membrane']
for l in m.node_tree.links:
    if l.from_node.name in('Attribute','EM_ringforce') or l.to_node.name in ('Math.038','EM_gate37'): print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
print('ops', m.node_tree.nodes['Math.037'].operation, m.node_tree.nodes['EM_inv'].operation, m.node_tree.nodes['EM_gate37'].operation, m.node_tree.nodes['EM_ringforce'].attribute_type)
ws=[ob for ob in bpy.data.objects if ob.name.startswith('SCH_win_')]
w=ws[0]; print(w.name,w.type,w.instance_type,w.instance_collection, w.instance_collection.library if w.instance_collection else None)
ic=w.instance_collection
for ob in ic.all_objects: print(' IC',ob.name,ob.type,[s.material.name for s in ob.material_slots if s.material])
print('instancers', sum(1 for ob in bpy.data.objects if ob.instance_collection==ic))

import bpy
for n in ['Footpaths_OSM','Roads_OSM']:
    o=bpy.data.objects.get(n); print(n, o and [s.material.name for s in o.material_slots if s.material], o and [m.name for m in o.modifiers])
m=bpy.data.materials['OV_Paving_concrete_walk_tone_UNVERIFIED']; print('OVusers',[o.name for o in bpy.data.objects if any(s.material==m for s in o.material_slots)][:10])
for o in bpy.data.objects:
    if o.type=='MESH' and o.material_slots and any(s.material and 'Paving' in s.material.name for s in o.material_slots) and not o.name.startswith(('QS_','QT_')):
        pass
cam=bpy.data.objects['QT_CAM_closeup_richardson_walk_joints']; print('cam',tuple(cam.location))
m=bpy.data.materials[[s.material.name for s in bpy.data.objects['Footpaths_OSM'].material_slots][0]]
print([(n.type,n.name) for n in m.node_tree.nodes])
P=[n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0]; print('BC link', P.inputs['Base Color'].links[0].from_node.name if P.inputs['Base Color'].links else P.inputs['Base Color'].default_value[:])

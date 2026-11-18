import bpy
for o in bpy.data.objects:
    n=o.name
    if 'MID' in n or 'canopy' in n.lower() or 'wood' in n.lower() or 'FAR' in n:
        mods=[(m.name,m.type,getattr(m,'node_group',None) and m.node_group.name) for m in o.modifiers]
        print('OBJ',n,o.type,o.data.name if o.data else None,len(o.data.vertices) if o.type=='MESH' else '',o.hide_render,mods,[s.material.name for s in o.material_slots if s.material][:4])
mat=bpy.data.materials['MID_canopy_carpet_leaf_ai']
for nd in mat.node_tree.nodes: print('NODE',nd.name,nd.type,nd.label)
for ng in bpy.data.node_groups:
    if 'canopy' in ng.name.lower() or 'MID' in ng.name or 'wood' in ng.name.lower():
        print('NG',ng.name,[ (n.name,n.type) for n in ng.nodes][:60])

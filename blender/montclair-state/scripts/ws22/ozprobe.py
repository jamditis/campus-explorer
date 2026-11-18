import bpy
o=bpy.data.objects['OZ_walk_joints_auto_GN_UNVERIFIED']
print('OZ',o.type,len(o.data.vertices) if o.type=='MESH' else '',[ (m.name,m.type,getattr(m,'node_group',None) and m.node_group.name) for m in o.modifiers],[s.material.name for s in o.material_slots if s.material], o.parent and o.parent.name, [c.name for c in o.users_collection])
for m in o.modifiers:
    if m.type=='NODES':
        for k in m.keys(): print('  IN',k,m[k] if not hasattr(m[k],'name') else m[k].name)
        for n in m.node_group.nodes: print('  N',n.name,n.bl_idname, n.inputs['Object'].default_value.name if n.bl_idname=='GeometryNodeObjectInfo' and n.inputs['Object'].default_value else '')
print('CUSTOM',{k:str(o[k])[:200] for k in o.keys()})

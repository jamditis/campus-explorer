import bpy
ng=bpy.data.objects['OZ_walk_joints_auto_GN_UNVERIFIED'].modifiers[0].node_group
print('NG',ng.name)
for n in ng.nodes: print('N',n.type,n.name,getattr(n,'data_type',''),getattr(n,'domain',''), [ (i.name, round(i.default_value,3) if isinstance(getattr(i,'default_value',None),float) else '') for i in n.inputs if not i.is_linked and hasattr(i,'default_value')][:5])

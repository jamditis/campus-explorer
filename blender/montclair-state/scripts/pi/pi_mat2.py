import bpy
nt=bpy.data.materials['Roof_tile_or_membrane'].node_tree
for nm in ('Math.037','Math.039','Math.003','Map Range'):
    n=nt.nodes[nm]; print('V',nm,[(i.name,i.is_linked,getattr(i,'default_value',None) if not hasattr(getattr(i,'default_value',None),'__len__') else tuple(round(x,3) for x in i.default_value)) for i in n.inputs])
n=nt.nodes['Mix.009']; print('M9',n.data_type,[ (i.name,i.is_linked, tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if i.enabled])
print('USERS',bpy.data.materials['Roof_tile_or_membrane'].users)

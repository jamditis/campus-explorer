import bpy
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=['Terrain_LiDAR_DTM_1m']
o=to.objects[0]; m=o.modifiers['QI_east_edge_LiDAR_patch']; ng=m.node_group
print('QD group',ng.name)
for k in m.keys(): print('QD input',k,m[k] if not hasattr(m[k],'name') else m[k].name)
for n in ng.nodes:
    vals=[]
    for i in n.inputs:
        if not i.is_linked and hasattr(i,'default_value'):
            v=i.default_value
            try: v=tuple(round(a,3) for a in v)
            except TypeError: v=round(v,3) if isinstance(v,float) else v
            vals.append(f'{i.name}={v}')
    extra=getattr(n,'operation',None) or getattr(n,'data_type',None) or ''
    print('QD',n.name,n.bl_idname,extra,getattr(n,'image',None) and n.image.name,'|',' '.join(vals)[:200])
for l in ng.links: print('QL',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)

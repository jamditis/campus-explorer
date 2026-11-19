import bpy
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F) as (a,b): b.objects=['Context_skirt_3DEP_ortho_4km']
o=b.objects[0]
print('P237E stack',[m.name for m in o.modifiers])
for mn in ('QD_skirt_under_pzpk','WS235_skirt_under_M3b_corridor'):
    ng=o.modifiers[mn].node_group
    print('P237E ===',mn)
    for n in ng.nodes:
        vals=[]
        for i in n.inputs:
            if not i.is_linked and hasattr(i,'default_value') and i.enabled:
                v=i.default_value
                try: v=tuple(round(x,3) for x in v)
                except TypeError:
                    try: v=round(v,3)
                    except TypeError: v=getattr(v,'name',v)
                vals.append((i.name,v))
        ex=getattr(n,'operation','') or getattr(n,'data_type','')
        print('P237E N',n.name,n.type,ex,getattr(n,'domain',''),vals)
    for l in ng.links: print('P237E L',l.from_node.name,l.from_socket.identifier,'->',l.to_node.name,l.to_socket.identifier)

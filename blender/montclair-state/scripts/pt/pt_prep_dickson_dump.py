# pt prep (read-only): dump Dickson wall objects, UV layers, attributes and the facade shader node trees for the next
# session's Dickson slot extraction (shader slots use different per-object maths than Calcia). No scene change, no save.
import bpy, json
out=[]
for o in bpy.data.objects:
    if o.type=='MESH' and 'Dickson' in o.name:
        me=o.data; d=dict(name=o.name,verts=len(me.vertices),faces=len(me.polygons),hide_render=o.hide_render,
            uv=[u.name for u in me.uv_layers],attrs=[(a.name,a.domain,a.data_type) for a in me.attributes if not a.name.startswith('.')],
            props={k:(o[k] if isinstance(o[k],(int,float,str)) else str(o[k])) for k in o.keys()},mats=[])
        for m in me.materials:
            if not m or not m.use_nodes: continue
            nodes=[]
            for n in m.node_tree.nodes:
                ins={i.name:(list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked}
                nodes.append(dict(name=n.name,type=n.bl_idname,op=getattr(n,'operation',None),attr=getattr(n,'attribute_name',None),uv=getattr(n,'uv_map',None),ins={k:(v if isinstance(v,(int,float)) else [round(x,4) for x in v]) for k,v in ins.items() if isinstance(v,(int,float,list))}))
            links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]
            d['mats'].append(dict(name=m.name,nodes=nodes,links=links))
        out.append(d)
json.dump(out,open('data/pt/prep_dickson_shader_dump.json','w'),indent=1,default=str); print('DICKSON_DUMP',len(out),[d['name'] for d in out])

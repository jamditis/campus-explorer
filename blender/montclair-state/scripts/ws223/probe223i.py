import bpy
o=bpy.data.objects['WS70_gap_strip_grass_berms']
for m in o.modifiers:
    print('P223 mod',m.name,m.node_group.name if m.node_group else None,{k:(m[k] if not hasattr(m[k],'name') else m[k].name) for k in m.keys()})
    if m.node_group:
        for n in m.node_group.nodes:
            vals=[]
            for s in n.inputs:
                if hasattr(s,'default_value') and not s.is_linked:
                    try: vals.append((s.name,round(float(s.default_value),4)))
                    except Exception: pass
            print('P223   node',n.bl_idname,n.name,getattr(n,'operation',''),getattr(n,'data_type',''),vals[:6])

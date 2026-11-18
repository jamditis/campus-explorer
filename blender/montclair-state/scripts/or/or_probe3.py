import bpy
m=bpy.data.materials['Wall_stucco_mission']; nt=m.node_tree
for n in nt.nodes:
    if n.type=='ATTRIBUTE': print('ATTR',n.name,n.attribute_name,n.attribute_type,[ (l.to_node.name) for o in n.outputs for l in o.links])
w=bpy.data.objects['Center for Computing and Information Science walls']
for a in w.data.attributes: print('MESHATTR',a.name,a.domain,a.data_type)
# dump math chain compactly
def desc(n):
    s=n.name+'['+(n.operation if n.type=='MATH' else n.type)+']'
    ins=[]
    for i in n.inputs:
        if not i.enabled: continue
        if i.is_linked: ins.append(i.links[0].from_node.name+'.'+i.links[0].from_socket.name)
        elif hasattr(i,'default_value'):
            try: ins.append(str(round(float(i.default_value),4)))
            except: pass
    return s+' <- '+', '.join(ins)
for n in nt.nodes:
    if n.type in('MATH','SEPXYZ','COMBXYZ','MIX','MIX_SHADER','TEX_WHITE_NOISE'): print(desc(n))

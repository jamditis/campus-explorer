import bpy
w=bpy.data.objects['Feliciano School of Business walls']
print('PROPS',{k:(w[k] if not hasattr(w[k],'to_dict') else '..') for k in w.keys()})
print('ATTRS',[(a.name,a.domain,a.data_type) for a in w.data.attributes])
m=bpy.data.materials['Wall_stucco_mission']
for n in m.node_tree.nodes:
    s=n.bl_idname+' '+n.name+' '+n.label
    if n.bl_idname in('ShaderNodeAttribute',): s+=' attr='+n.attribute_name
    if n.bl_idname=='ShaderNodeMath': s+=' op='+n.operation+' in='+str([round(i.default_value,3) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked])
    if n.bl_idname=='ShaderNodeValue': s+=' v='+str(round(n.outputs[0].default_value,3))
    if n.bl_idname=='ShaderNodeGroup': s+=' grp='+n.node_tree.name
    print('N',s)

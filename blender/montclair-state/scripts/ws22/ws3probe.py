import bpy
mt=bpy.data.materials['WS3_Concrete_panels_sawcut']; nt=mt.node_tree
for n in nt.nodes:
    if n.bl_idname in ('ShaderNodeTexCoord','ShaderNodeNewGeometry','ShaderNodeAttribute','ShaderNodeUVMap','ShaderNodeMapping'):
        print('N',n.name,n.bl_idname,getattr(n,'attribute_name',''), [l.to_node.name for o in n.outputs for l in o.links][:4], [ (o.name) for o in n.outputs if o.is_linked])
users=[o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material==mt for s in o.material_slots)]
print('USERS',users[:10])
o=bpy.data.objects[users[0]]; print('UVS',[u.name for u in o.data.uv_layers], 'scale',o.scale[:], 'attrs',[a.name for a in o.data.attributes][:15])
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; print('TUV',[u.name for u in t.data.uv_layers])

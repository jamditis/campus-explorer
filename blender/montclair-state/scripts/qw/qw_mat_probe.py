import bpy
m=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']
for n in m.node_tree.nodes:
    if n.type in ('ATTRIBUTE','UVMAP','TEX_COORD','VERTEX_COLOR','GEOMETRY','TEX_IMAGE'):
        print('NODE',n.type,n.name,getattr(n,'attribute_name',''),getattr(n,'uv_map',''),getattr(n,'image',None) and n.image.name, [o.name for o in n.outputs if o.is_linked])
o=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; e=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
print('EVAL attrs',[(a.name,a.domain,a.data_type) for a in e.data.attributes if not a.name.startswith('.')])

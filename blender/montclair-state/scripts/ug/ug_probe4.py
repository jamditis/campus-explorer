import bpy
for n in ('Terrain_LiDAR_DTM_1m','SA_ground_lower_patch_UNVERIFIED'):
    o=bpy.data.objects[n]
    print('UGM',n,[s.material.name for s in o.material_slots],list(o.data.uv_layers.keys()),[m.type for m in o.modifiers], list(o.data.attributes.keys())[:12])
    for s in o.material_slots:
        print('UGM  nodes',s.material.name,sorted({nd.type for nd in s.material.node_tree.nodes}))
        for nd in s.material.node_tree.nodes:
            if nd.type in('TEX_COORD','UVMAP','ATTRIBUTE','TEX_IMAGE','MAPPING'):
                print('UGM   ',nd.type,nd.name,[l.to_node.name for out in nd.outputs for l in out.links][:4], getattr(nd,'uv_map',''),getattr(nd,'attribute_name',''), nd.image.name if nd.type=='TEX_IMAGE' and nd.image else '')

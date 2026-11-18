import bpy
for n in ['TZ_Cole_add_glass_UNVERIFIED','TZ_Cole_add_mullion_UNVERIFIED','WS6_Glass_dark_reflective_UNVERIFIED','TW_Cole_win_glass_UNVERIFIED','TZ_Cole_sill_drip_UNVERIFIED']:
    m=bpy.data.materials.get(n); print('MAT',n,m.users if m else None)
    if m and m.use_nodes:
        for nd in m.node_tree.nodes:
            if nd.type=='BSDF_PRINCIPLED':
                print('  ',{k:(tuple(round(x,3) for x in nd.inputs[k].default_value) if hasattr(nd.inputs[k].default_value,'__len__') else round(nd.inputs[k].default_value,3)) for k in ['Base Color','Roughness','Metallic','IOR','Transmission Weight','Coat Weight']}, 'linked', [i.name for i in nd.inputs if i.is_linked])
            else: print('   node',nd.type)

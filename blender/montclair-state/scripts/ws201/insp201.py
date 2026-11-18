import bpy, numpy as np
for n in ('WS75_sprague','WS80_sprague','WS81_lot_seam','WS94_lot','WS96_lot'):
    o=[o for o in bpy.data.objects if o.name.startswith(n)][0]; me=o.data
    sm=np.array([p.use_smooth for p in me.polygons])
    print('I201',o.name[:40],'v',len(me.vertices),'f',len(me.polygons),'smooth%',round(sm.mean(),2),'mats',[m.name if m else None for m in me.materials],'mods',[(m.name,m.type,m.show_render) for m in o.modifiers],'loc',tuple(round(a,2) for a in o.location),flush=True)
    for m in me.materials:
        if m and m.use_nodes:
            for nd in m.node_tree.nodes:
                if nd.type=='BSDF_PRINCIPLED': print('I201  ',m.name,'base',tuple(round(a,3) for a in nd.inputs['Base Color'].default_value),'linked',nd.inputs['Base Color'].is_linked,'rough',round(nd.inputs['Roughness'].default_value,2),flush=True)
                if nd.type=='TEX_IMAGE': print('I201   img',nd.image.name if nd.image else None,flush=True)

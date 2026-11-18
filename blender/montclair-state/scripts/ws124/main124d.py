import bpy, os
g=bpy.data.materials['WS108_Chapin_window_glass_dark']; b=g.node_tree.nodes['Principled BSDF']
print('M124d before',[(k,round(b.inputs[k].default_value,3) if not hasattr(b.inputs[k].default_value,'__len__') else tuple(round(x,3) for x in b.inputs[k].default_value)) for k in ('Base Color','Roughness','Metallic','Transmission Weight','Alpha')])
print('M124d users',[o.name[:40] for o in bpy.data.objects if o.type=='MESH' and g.name in [m.name for m in o.data.materials if m]])
if os.environ.get('APPLY')=='1':
    b.inputs['Transmission Weight'].default_value=0.0; b.inputs['Alpha'].default_value=1.0
    b.inputs['Base Color'].default_value=(0.02,0.025,0.03,1); b.inputs['Roughness'].default_value=0.06; b.inputs['Specular IOR Level'].default_value=0.8
    g.blend_method='OPAQUE' if hasattr(g,'blend_method') else None
    bpy.ops.wm.save_mainfile(); print('M124d SAVED')

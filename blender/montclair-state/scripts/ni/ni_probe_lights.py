import bpy
for o in bpy.data.objects:
    if o.type=='LIGHT' and not o.hide_render:
        p=o.matrix_world.translation
        if -25<p.x<40 and -30<p.y<45 and 130<p.z<160: print('LT|%s|%s|%.1f|%.1f,%.1f,%.1f'%(o.name,o.data.type,o.data.energy,p.x,p.y,p.z))
for m in bpy.data.materials:
    if m.name.startswith(('NG_led','NG_sign')) and m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type=='BSDF_PRINCIPLED': print('MAT|',m.name,n.inputs['Emission Strength'].default_value,m.users)
sc=bpy.context.scene; print('VIEW',sc.view_settings.view_transform,sc.view_settings.look,sc.view_settings.exposure)

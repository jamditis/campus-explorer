import bpy
o=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
print('SK vis',o.visible_camera,o.visible_diffuse,o.visible_glossy,o.visible_shadow,o.is_shadow_catcher,o.is_holdout, o.light_linking.receiver_collection, o.light_linking.blocker_collection)
for l in bpy.data.objects:
    if l.type=='LIGHT' and not l.hide_render:
        ll=l.light_linking
        print('L',l.name,l.data.type,round(l.data.energy,2),ll.receiver_collection.name if ll.receiver_collection else None)
w=bpy.context.scene.world
for n in w.node_tree.nodes:
    if n.type=='BACKGROUND': print('BG',n.name,n.inputs['Strength'].default_value)
    if n.type=='TEX_SKY': print('SKY',n.sky_type,getattr(n,'sun_intensity',None),getattr(n,'air_density',None),getattr(n,'dust_density',None),getattr(n,'sun_elevation',None))
v=bpy.context.scene.view_settings; print('VIEW',v.view_transform,v.look,v.exposure)

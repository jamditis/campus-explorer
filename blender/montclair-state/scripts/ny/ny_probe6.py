import bpy, mathutils
for o in bpy.data.objects:
    p=o.matrix_world.translation
    if -1<p.x<7 and 13.5<p.y<18.5 and 139<p.z<141.5 and o.type in ('LIGHT','MESH') and 'N classroom' not in o.name:
        print('P6',o.type,o.name,[round(x,2) for x in p],o.hide_render, o.visible_camera, o.visible_shadow, o.data.type if o.type=='LIGHT' else '')
for o in bpy.data.objects:
    if o.type=='LIGHT':
        p=o.matrix_world.translation
        if -1<p.x<7 and 13.5<p.y<18.5: print('L6',o.name,[round(x,2) for x in p],o.data.type,round(o.data.energy,1),o.hide_render)

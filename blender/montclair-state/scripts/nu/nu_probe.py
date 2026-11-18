import bpy
c=bpy.data.objects['NT_CAM_eye_atrium_looking_west_to_doors']; print('CAM',tuple(round(x,2) for x in c.matrix_world.translation), c.data.lens)
for o in bpy.data.objects:
    if o.type=='LIGHT' and not o.hide_render:
        p=o.matrix_world.translation
        if -24<p.x<-5 and -2<p.y<20 and 136<p.z<150:
            d=o.data; print('L|',o.name,d.type,round(d.energy,1),tuple(round(x,2) for x in p),getattr(d,'size',None),getattr(d,'spot_size',None),tuple(round(x,2) for x in o.rotation_euler))
for o in bpy.data.objects:
    if o.type=='MESH' and not o.hide_render and ('pilaster' in o.name.lower() or 'column' in o.name.lower()):
        p=o.matrix_world.translation; 
        if -26<p.x<0: print('M|',o.name,tuple(round(x,2) for x in p),o.dimensions[:])

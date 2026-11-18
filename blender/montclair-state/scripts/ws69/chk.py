import bpy
for o in bpy.data.objects:
    if o.name.startswith(('WS67_','WS68_','WS60','ey_rhd','WS27_CollegeAve')):
        print('C69',o.name[:60],o.type,'hide_render',o.hide_render,'vis_cam',o.visible_camera,'hide_vp',o.hide_viewport,'mats',[m.name[:30] for m in o.data.materials] if o.type=='MESH' else '', len(o.data.polygons) if o.type=='MESH' else '')

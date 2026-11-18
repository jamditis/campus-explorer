import bpy
for o in bpy.data.objects:
    n=o.name
    if o.type=='MESH' and any(n.startswith(p) for p in ('WS89','WS87','WS77','WS74','WS75','WS76','WS80','WS83','WS73','WS72','WS71','WS69','WS35','COLE_plaza','Footpath','WS27')):
        bb=[o.matrix_world@__import__('mathutils').Vector(v) for v in o.bound_box]
        print('P91',n,len(o.data.vertices),len(o.data.polygons),'mods',len(o.modifiers),'hide',o.hide_render,'x %.1f %.1f y %.1f %.1f z %.2f %.2f'%(min(v.x for v in bb),max(v.x for v in bb),min(v.y for v in bb),max(v.y for v in bb),min(v.z for v in bb),max(v.z for v in bb)))

import bpy, mathutils
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    if not (min(v.x for v in bb)<-4 and max(v.x for v in bb)>-9 and min(v.y for v in bb)<16.7 and max(v.y for v in bb)>12.5 and max(v.z for v in bb)>140.5 and min(v.z for v in bb)<142.5): continue
    print('G',o.name[:60],[(s.link,s.material.name if s.material else None) for s in o.material_slots],[round(min(v.x for v in bb),2),round(max(v.x for v in bb),2),round(min(v.y for v in bb),2),round(max(v.y for v in bb),2)])

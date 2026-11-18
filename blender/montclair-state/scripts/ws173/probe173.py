import bpy, mathutils
X0,X1,Y0,Y1=-352,-268,-300,-252
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE'): continue
    bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    if (max(xs)-min(xs))>400: continue
    m=o.active_material.name if o.active_material else '-'
    print('OBJ',o.name,'|',round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),round(min(zs),2),round(max(zs),2),'|',len(o.data.vertices) if o.type=='MESH' else 'c','|',m,'|hide',o.hide_render,flush=True)

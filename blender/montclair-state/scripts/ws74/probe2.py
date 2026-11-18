import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.type not in('MESH','CURVE','EMPTY'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]; zs=[p.z for p in bb]
    if min(xs)<-280 and max(xs)>-345 and min(ys)<-60 and max(ys)>-135 and max(xs)-min(xs)<150:
        print('P2',o.name[:60],o.type,'hideR',o.hide_render,'v',len(o.data.vertices) if o.type=='MESH' else '-', 'x %.0f..%.0f y %.0f..%.0f z %.1f..%.1f'%(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)),[m.material.name[:25] for m in o.material_slots if m.material][:2])

import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]
    if not(min(xs)<-235 and max(xs)>-280 and min(ys)<-95 and max(ys)>-140): continue
    if o.name.startswith('T_') : continue
    mw=o.matrix_world; n=0; zs=[]
    me=o.data
    for p in me.polygons:
        c=mw@p.center
        if -280<c.x<-235 and -140<c.y<-95: n+=1; zs.append(c.z)
    if n: print('P6',o.name[:50],n,'z %.1f..%.1f'%(min(zs),max(zs)),[s.material.name[:20] if s.material else None for s in o.material_slots][:3],[m.name[:20] for m in o.modifiers][:4],flush=True)

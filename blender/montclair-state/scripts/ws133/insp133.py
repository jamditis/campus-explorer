import bpy, math
from mathutils import Vector
X0,X1,Y0,Y1=-130,-108,-272,-205
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if any(math.isnan(q) for q in xs+ys): print('NAN',o.name); continue
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    area=(max(xs)-min(xs))*(max(ys)-min(ys))
    me=o.data
    # count faces with centre in window
    n=0; zc=[]
    mw=o.matrix_world
    if len(me.polygons)<400000:
        for p in me.polygons:
            c=mw@p.center
            if X0<c.x<X1 and Y0<c.y<Y1: n+=1; zc.append(c.z)
    print('OBJ %-70s vis=%d col=%s faces_in=%d z=%.1f..%.1f bb x%.0f..%.0f y%.0f..%.0f mats=%s'%(o.name,not o.hide_render,o.users_collection[0].name if o.users_collection else '-',n,min(zc) if zc else 0,max(zc) if zc else 0,min(xs),max(xs),min(ys),max(ys),[m.name for m in me.materials][:3]))

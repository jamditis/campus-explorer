import bpy, mathutils
# list renderable objects whose world bbox intersects the CCOM west entrance zone
X0,X1,Y0,Y1,Z0,Z1=-25,-17,4,19,136.5,150
res=[]
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE','FONT') or o.hide_render: continue
    bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1 or max(zs)<Z0 or min(zs)>Z1: continue
    if (max(xs)-min(xs))>60 or (max(ys)-min(ys))>60: continue
    mats=','.join(m.name for m in o.data.materials if m)[:60] if hasattr(o.data,'materials') else ''
    res.append((o.name[:70],round(min(xs),2),round(max(xs),2),round(min(ys),2),round(max(ys),2),round(min(zs),2),round(max(zs),2),o.users_collection[0].name[:40],mats, o.library is not None or (o.data and o.data.library is not None)))
res.sort(key=lambda r:r[1])
for r in res: print('P',r)
print('N',len(res))

import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
pts=[(x,y) for x in (122,124,126,128,131,134) for y in (164,168,172,176,180)]
cands=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<120 or min(xs)>136 or max(ys)<162 or min(ys)>182: continue
    cands.append(o)
print('PROBE cands',len(cands),[o.name for o in cands][:40])
for (x,y) in pts:
    hits=[]
    for o in cands:
        e=o.evaluated_get(dg); mi=o.matrix_world.inverted()
        try: ok,loc,n,i=e.ray_cast(mi@Vector((x,y,400)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
        except Exception as ex: continue
        if ok: hits.append(((o.matrix_world@loc).z,o.name,i))
    hits.sort(reverse=True)
    print('PROBE',x,y,[(round(z,2),n,i) for z,n,i in hits[:4]])

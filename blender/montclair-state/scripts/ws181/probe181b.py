# ws181 read-only fine probe of the y -229..-238 seam W of Lot 3 (hole check); loads every ground-ish object
import bpy, re
from mathutils import Vector
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
R=re.compile(r'^(WS16|WS17|Context_ground_beyond)',re.I)
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if R.search(n) and 'CAM' not in n and 'hidden' not in n]
objs=[o for o in b.objects if o and o.type=='MESH']
print('LOADED',len(objs),flush=True)
X0,X1,Y0,Y1=-352,-306,-240,-226
cand=[]
for o in objs:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    if len(o.data.polygons)==0: continue
    cand.append(o)
for o in cand: bpy.context.scene.collection.objects.link(o)
bpy.context.evaluated_depsgraph_get()
print('CAND',[o.name for o in cand],flush=True)
holes=[]
y=-226.0
while y>=-240:
    x=-350.0
    while x<=-306:
        best=None
        for o in cand:
            mw=o.matrix_world; inv=mw.inverted()
            ok,loc,n,i=o.ray_cast(inv@Vector((x,y,200)),(inv.to_3x3()@Vector((0,0,-1))).normalized())
            if ok:
                z=(mw@loc).z
                if best is None or z>best[0]: best=(z,o.name,o.hide_render)
        if best is None or best[2]: holes.append((x,y,best[1] if best else None))
        x+=1.0
    y-=0.5
print('HOLES',len(holes),flush=True)
for h in holes: print('HOLE',h,flush=True)

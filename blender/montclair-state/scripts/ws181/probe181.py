# ws181 read-only probe: what in main currently covers Lot 36 (x -350..-312, y -248..-205)? subset load by prefix, raycast grid
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PRE=tuple(os.environ.get('PRE','WS16,WS17,WS13,WS110,WS113,WS86,WS179,UTIL,GROUND,Ground,ground,TER,Terrain,terrain,NORTH,North,north').split(','))
with bpy.data.libraries.load(p) as (a,b):
    names=[n for n in a.objects]
    b.objects=[n for n in names if n.startswith(PRE) and 'CAM' not in n and 'hidden' not in n]
print('ALL',len(names),'LOADED',len(b.objects),flush=True)
X0,X1,Y0,Y1=-350,-312,-248,-205
dg=None
hits={}
objs=[o for o in b.objects if o and o.type=='MESH']
sc=bpy.context.scene
for o in objs:
    sc.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
cand=[]
for o in objs:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    cand.append(o); print('BBOX',o.name,'x %.1f..%.1f y %.1f..%.1f z %.2f..%.2f'%(min(xs),max(xs),min(ys),max(ys),min(v.z for v in bb),max(v.z for v in bb)),flush=True)
print('CAND',len(cand),flush=True)
for y in range(-208,-247,-4):
    row=[]
    for x in range(-348,-311,4):
        best=None
        for o in cand:
            mw=o.matrix_world; inv=mw.inverted()
            org=inv@Vector((x,y,200)); d=(inv.to_3x3()@Vector((0,0,-1))).normalized()
            ok,loc,nrm,idx=o.ray_cast(org,d)
            if ok:
                z=(mw@loc).z
                if best is None or z>best[0]:
                    mat=o.material_slots[o.data.polygons[idx].material_index].material.name if o.material_slots and o.material_slots[o.data.polygons[idx].material_index].material else '-'
                    best=(z,o.name,mat)
        row.append(best)
    for x,bst in zip(range(-348,-311,4),row):
        print('RAY',x,y,'%.2f %s | %s'%bst if bst else 'none',flush=True)

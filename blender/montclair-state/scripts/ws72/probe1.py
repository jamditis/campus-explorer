import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=-260,-236,-62,-40
cand=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]; zs=[p.z for p in bb]
    if min(xs)<X1 and max(xs)>X0 and min(ys)<Y1 and max(ys)>Y0 and max(xs)-min(xs)<3000:
        cand.append(o); print('OBJ',o.name,[round(v,1) for v in (min(xs),max(xs),min(ys),max(ys),min(zs),max(zs))],[m.name for m in o.modifiers][-3:],o.active_material.name if o.active_material else None)
T0=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for m in T0.modifiers:
    if m.name.startswith(tuple(os.environ.get('MODOFF','WS64').split(','))): m.show_viewport=False; m.show_render=False
KEEP=tuple(os.environ.get('KEEP','Terrain_LiDAR_DTM_1m,WS,LH_,LF_,ey_,cf_,KY_').split(','))
for o in list(bpy.data.objects):
    if not o.name.startswith(KEEP) or (o.name[-4:-3]=='.' and o.name[-3:].isdigit()): bpy.data.objects.remove(o)
cand=[o for o in bpy.data.objects]
print('LR evaluating',len(cand),flush=True)
dg=bpy.context.evaluated_depsgraph_get()
GROUND=os.environ.get('GROUND','Terrain_LiDAR_DTM_1m,Footpaths_OSM,Roads_OSM,WS,cf_,LH_,LF_,KY_,fn_,ey_,Kasser_apron,KX').split(',')
import os
B={}
for o in cand:
    if (o.name[-4:-3]=='.' and o.name[-3:].isdigit()) or 'DTM_target' in o.name or o.hide_render: continue
    if not any(o.name.startswith(p) for p in GROUND): continue
    oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); B[o.name]=BVHTree.FromBMesh(bm); print('LR bvh',o.name,len(bm.verts),flush=True); bm.free(); oe.to_mesh_clear()
ab={}
for y in range(-40,-61,-1):
    row=[]
    for x in range(-259,-236,1):
        best=None
        for n,t in B.items():
            h=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
            if h and (best is None or h.z>best[1]): best=(n,h.z)
        if best:
            a=ab.setdefault(best[0],chr(65+len(ab)) if len(ab)<26 else chr(97+len(ab)-26)); row.append(f"{a}{best[1]-120:5.2f}")
        else: row.append('  -   ')
    print('R',y,' '.join(row))
for k,v in ab.items(): print('KEY',v,k)

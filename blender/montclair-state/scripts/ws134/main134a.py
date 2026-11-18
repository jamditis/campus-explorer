# ws134a: UNIFY #42 part 1 — lift WS133 Russ E walk tops to >= evaluated ground + 3 cm (bed +1 cm) using cropped
# BVHs of the evaluated ground objects (replaces main133d's per-vertex scene.ray_cast). Also prints the day-18 region inventory.
import bpy, os, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE','0')=='1'
w=bpy.data.objects['WS133_Russ_E_walk_concrete_LiDAR2023int_UNVERIFIEDjoints']; b=bpy.data.objects['WS133_Russ_E_wall_foot_bed_mulch_LiDAR2023lowint_UNVERIFIED']
GROUND=('Terrain_LiDAR','WS113_terrain','WS114_terrain','WS133b_','WS60_terrain','Context_skirt','WS110_ground')
pts=[w.matrix_world@v.co for v in w.data.vertices]+[b.matrix_world@v.co for v in b.data.vertices]
X0=min(p.x for p in pts)-1;X1=max(p.x for p in pts)+1;Y0=min(p.y for p in pts)-1;Y1=max(p.y for p in pts)+1
print('BBOX %.1f %.1f %.1f %.1f'%(X0,X1,Y0,Y1))
dg=bpy.context.evaluated_depsgraph_get(); trees=[]
for o in bpy.data.objects:
    if o.type!='MESH' or not o.name.startswith(GROUND) or o.hide_render: continue
    e=o.evaluated_get(dg); m=e.to_mesh(); mw=o.matrix_world
    V=[mw@v.co for v in m.vertices]; F=[]
    for p in m.polygons:
        vs=p.vertices
        if any(X0<=V[i].x<=X1 and Y0<=V[i].y<=Y1 for i in vs): F.append(tuple(vs))
    if F:
        used=sorted({i for f in F for i in f}); rm={i:k for k,i in enumerate(used)}
        trees.append((o.name,BVHTree.FromPolygons([tuple(V[i]) for i in used],[tuple(rm[i] for i in f) for f in F])))
        print('GROUND',o.name,len(F))
    e.to_mesh_clear()
def ground(x,y):
    best=None
    for n,T in trees:
        h=T.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        if h[0] is not None and (best is None or h[0].z>best): best=h[0].z
    return best
for o,off in ((w,0.03),(b,0.01)):
    me=o.data; mw=o.matrix_world; n=0; mx=0; byxy={}
    for v in me.vertices: byxy.setdefault((round(v.co.x,3),round(v.co.y,3)),[]).append(v)
    for key,vs in byxy.items():
        top=max(vs,key=lambda v:v.co.z); p=mw@top.co; g=ground(p.x,p.y)
        if g is None: continue
        d=g+off-p.z
        if d>0:
            for v in vs: v.co.z+=d
            n+=1; mx=max(mx,d)
    me.update(); print('LIFT',o.name[:40],n,'of',len(byxy),'max %.3f'%mx)
# proxy: keep WS113 paving tops proxy in sync if the walk is part of it (report only)
for o in bpy.data.objects:
    if 'paving_tops_proxy' in o.name: print('PROXY',o.name,len(o.data.vertices))
# region inventory for day 18
RX0,RX1,RY0,RY1=-125,-30,-300,-190
for o in bpy.data.objects:
    if o.type not in('MESH','CURVE') : continue
    try: bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    except Exception: continue
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if any(math.isnan(q) for q in xs+ys) or max(xs)<RX0 or min(xs)>RX1 or max(ys)<RY0 or min(ys)>RY1: continue
    if (max(xs)-min(xs))>400: continue
    print('INV %-70s x%.0f..%.0f y%.0f..%.0f z%.1f..%.1f hide%d %s'%(o.name[:70],min(xs),max(xs),min(ys),max(ys),min(zs),max(zs),o.hide_render,o.users_collection[0].name[:30] if o.users_collection else ''))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

# ws22: close small gaps (<=24-edge boundary loops) in QG_north_strip_LiDAR_terrain_patch where nothing is overhead
# (they showed the ws21 backing skin 6 cm below as dark cracks in the court north of Life Hall).
import bpy,bmesh,os
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['QG_north_strip_LiDAR_terrain_patch']; M=o.matrix_world; Mi=M.inverted()
bm=bmesh.new(); bm.from_mesh(o.data)
be=[e for e in bm.edges if e.is_boundary]
seen=set(); loops=[]
for e in be:
    if e in seen: continue
    stack=[e]; grp=[]
    while stack:
        x=stack.pop()
        if x in seen: continue
        seen.add(x); grp.append(x)
        for v in x.verts:
            for y in v.link_edges:
                if y.is_boundary and y not in seen: stack.append(y)
    loops.append(grp)
fill=[]; skip=0
for g in loops:
    if len(g)>24: continue
    vs={v for e in g for v in e.verts}
    c=M@(sum((v.co for v in vs),Vector())/len(vs))
    hit,loc,n,i,ob,m=sc.ray_cast(dg,c+Vector((0,0,0.5)),Vector((0,0,1)),distance=25)
    if hit: skip+=1; print('SKIP overhead',ob.name,[round(x,1) for x in c]); continue
    fill.extend(g)
nf0=len(bm.faces)
r=bmesh.ops.holes_fill(bm,edges=fill,sides=0)
newf=r['faces']
bmesh.ops.triangulate(bm,faces=newf)
for f in bm.faces:
    if f.index<0 or not f.smooth: pass
for f in bm.faces: f.smooth=True
bm.to_mesh(o.data); o.data.update()
print('LOOPS small',sum(1 for g in loops if len(g)<=24),'filled edges',len(fill),'skipped',skip,'faces',nf0,'->',len(o.data.polygons))
o.data['ws22']='small gap loops filled (holes_fill), nothing overhead'
dg.update()
from mathutils.bvhtree import BVHTree
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; te=t.evaluated_get(dg); me=te.to_mesh(); TM=t.matrix_world
T=BVHTree.FromPolygons([TM@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])
# count points where the top surface within the court box is the low skin (patch missing): ray from above hits z lower than patch neighbours
P=BVHTree.FromObject(o,dg)
miss=0
for x in range(-5,60):
    for y in range(100,130):
        for dx in (0.25,0.75):
            for dy in (0.25,0.75):
                loc,n,i,d=P.ray_cast(Mi@Vector((x+dx,y+dy,400)),Vector((0,0,-1)))
                if loc is None: miss+=1
print('COURT patch misses (0.5 m grid)',miss)
te.to_mesh_clear()
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED')

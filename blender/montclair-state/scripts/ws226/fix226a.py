# W53 fix: over the east of the scene the base Terrain_LiDAR_DTM_1m mesh (fan-regrid) lies 3-23 m above the 1 m LiDAR
# DTM (dtm_1m.npy; independently confirmed by the USGS 3DEP 10 m DEM, data/skirt_dem_10m.npy, within ~1 m). The QG patch
# only offsets base vertices -6 cm where it hits (relative, so a base 10 m high stays 10 m high), and QI/QH deletes miss
# many base faces, so the wrong upper sheet wins. 
# REVISED after probe226e/f: the upper sheet is ONE giant interpolated base face (21,272 m2 quad, centre (163,50)) plus a few
# smaller ones, fan-triangulated by PB_terrain_fan_regrid; their vertices sit outside the patches so no patch delete/drop
# catches them. Fix: delete base faces in the east (centre x>60, area>100 m2) that are 100% covered by the QG/QH/QI
# patches (2 m sample grid, probe226f.json); the LiDAR patch becomes the surface there. No vertex moved.
# Then trees (mesh Tree_*) and loose props whose base followed the old upper sheet are re-seated onto the new surface.
# Trees are re-seated only where the new ground agrees with dtm_1m within 0.6 m. DRY=1: no tree moved (faces still deleted in memory).
import bpy, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
DRY=os.environ.get('DRY','0')=='1'
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
P=[bpy.data.objects[n] for n in ('QG_north_strip_LiDAR_terrain_patch','QH_east_fan_LiDAR_terrain_patch','QI_east_edge_LiDAR_terrain_patch')]
def terrain_bvh():
    sv=[m.show_viewport for m in t.modifiers]
    for m in t.modifiers: m.show_viewport=m.show_render
    dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); me=e.to_mesh(); M=t.matrix_world
    B=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); nv=len(me.vertices); e.to_mesh_clear()
    for m,s in zip(t.modifiers,sv): m.show_viewport=s
    return B,nv
def top(B,x,y):
    h=B.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return h[0].z if h[0] else None
B0,nv0=terrain_bvh()
import bmesh
DEL=[o[0] for o in json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws226/probe226f.json')) if o[3]>60 and o[1]>100 and o[5]>0 and o[5]==o[6]]
me=t.data; ok=[i for i in DEL if i<len(me.polygons) and me.polygons[i].area>100 and me.polygons[i].center.x>60]
print('F226A delete base faces (east, >100 m2, 100% under QG/QH/QI LiDAR patches):',[(i,round(me.polygons[i].area),tuple(round(c) for c in me.polygons[i].center[:2])) for i in ok],flush=True)
assert len(ok)==len(DEL), 'face indices changed'
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.faces[i] for i in ok],context='FACES_ONLY'); bm.to_mesh(me); bm.free(); me.update()
B1,nv1=terrain_bvh()
print('F226A terrain verts',nv0,nv1,flush=True)
# grid change summary
ch=0; big=0
for x in range(-245,250,5):
    for y in range(-245,250,5):
        a=top(B0,x,y); b=top(B1,x,y)
        if a is not None and b is not None and abs(a-b)>0.1:
            ch+=1; big+= abs(a-b)>2
            if b>a+0.05: print('F226A RAISED?',x,y,a,b,flush=True)
print('F226A grid5 changed cells',ch,'>2m',big,flush=True)
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
moved=[]; flag=[]; skip=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o.parent is not None or o.name.startswith(('Terrain_','QG_','QH_','QI_','Context_')): continue
    M=o.matrix_world
    bb=[M@Vector(c) for c in o.bound_box]; cx=sum(v.x for v in bb)/8; cy=sum(v.y for v in bb)/8
    if cx<60: continue
    a=top(B0,cx,cy); b=top(B1,cx,cy)
    if a is None or b is None or a-b<0.1: continue
    if o.data.name.startswith('Tree_'):
        ws=sorted((M@v.co for v in o.data.vertices),key=lambda w:w.z)[:20]
        ax=sum((w for w in ws),Vector())/len(ws); zb=ws[0].z
        a=top(B0,ax.x,ax.y); b=top(B1,ax.x,ax.y)
        if b is None: continue
        d=float(A[min(499,max(0,int(ax.y+250))),min(499,max(0,int(ax.x+250)))])
        if abs(zb-b)>0.3 and abs(b-d)>0.6: skip.append((o.name,round(ax.x,1),round(ax.y,1),round(zb,2),round(b,2),round(d,2)))
        if abs(zb-b)>0.3 and abs(b-d)<=0.6:
            dz=(b-0.05)-zb; moved.append((o.name,round(ax.x,1),round(ax.y,1),round(zb,2),round(b,2),round(dz,2)))
            if not DRY: o.location.z+=dz
    else:
        zmin=min(v.z for v in bb)
        flag.append((o.name,round(cx,1),round(cy,1),round(zmin,2),round(a,2),round(b,2)))
print('F226A trees reseated',len(moved),'(dry)' if DRY else '',flush=True)
for r in moved: print('F226A T',r,flush=True)
print('F226A trees NOT reseated (new ground != DTM, e.g. planter/structure or residual terrain):',len(skip),flush=True)
for r in skip: print('F226A S',r,flush=True)
fl=[r for r in flag if abs(r[3]-r[4])<1.0 and r[4]-r[5]>0.5]
print('F226A non-tree objects that sat on the old upper sheet (now floating):',len(fl),'of',len(flag),flush=True)
for r in fl: print('F226A O',r,flush=True)
json.dump({'skip':skip,'trees':moved,'objs':flag},open('/workspace/nj-scenes/montclair-state/scripts/ws226/fix226a_report.json','w'))

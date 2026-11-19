# ws228 re-run of fix227b after fix228a (W53d east edge). W53c follow-up: inside the re-gridded SE triangle (fix227a), re-seat trees (trunk-base ring, local z~0, as fix226b)
# both ways to the evaluated terrain - 0.05 where that terrain agrees with dtm_1m within 0.7 m, and re-seat the
# MID_lod1 context houses so their base sits 0.15 m under the lowest evaluated terrain at their footprint corners/centre.
import bpy, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_point_tri_2d
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
R=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws227/fix227a_report.json')); TR=[Vector(p[:2]) for p in R['tri']]
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
sv=[m.show_viewport for m in t.modifiers]
for m in t.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); me=e.to_mesh(); M=t.matrix_world
B=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear()
for m,s in zip(t.modifiers,sv): m.show_viewport=s
def tz(x,y):
    h=B.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return None if h[0] is None else h[0].z
inside=lambda x,y: bool(intersect_point_tri_2d(Vector((x,y)),*TR)) or (x>95 and y<-30)  # ws227e: plus the fix227x fan regions (SE box)
tr=[]; hs=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o.parent is not None: continue
    if o.data.name.startswith('Tree_') and not o.name.startswith('Tree_'):
        ring=[o.matrix_world@v.co for v in o.data.vertices if abs(v.co.z)<0.03]
        if len(ring)<3: continue
        x=sum(p.x for p in ring)/len(ring); y=sum(p.y for p in ring)/len(ring); z=min(p.z for p in ring)
        if not (-249<x<249 and -249<y<249) or not inside(x,y): continue
        g=tz(x,y)
        if g is None or abs(g-float(A[int(y+250),int(x+250)]))>0.7: continue
        dz=(g-0.05)-z
        if abs(dz)>0.05: o.location.z+=dz; tr.append((o.name,round(x,1),round(y,1),round(dz,2)))
    elif o.name.startswith('MID_lod1_'):
        bb=[o.matrix_world@Vector(b) for b in o.bound_box]
        xs=[b.x for b in bb]; ys=[b.y for b in bb]; cx=sum(xs)/8; cy=sum(ys)/8
        if not inside(cx,cy): continue
        S=[tz(x,y) for x,y in [(min(xs),min(ys)),(min(xs),max(ys)),(max(xs),min(ys)),(max(xs),max(ys)),(cx,cy)]]
        S=[s for s in S if s is not None]
        if not S: continue
        dz=(min(S)-0.15)-min(b.z for b in bb)
        if abs(dz)>0.05: o.location.z+=dz; hs.append((o.name,round(cx,1),round(cy,1),round(dz,2)))
print('F228B trees re-seated',len(tr),'down',sum(1 for r in tr if r[3]<0),'max |dz|',max([abs(r[3]) for r in tr] or [0]),flush=True)
print('F228B houses',hs,flush=True)
json.dump({'trees':tr,'houses':hs},open('/workspace/nj-scenes/montclair-state/scripts/ws228/fix228b_report.json','w'))

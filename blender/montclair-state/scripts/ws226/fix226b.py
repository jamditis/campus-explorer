# W53/W52 tree re-seat, corrected metric (probe226i): tree meshes have their trunk-base ring at local z=0 (PinOak/Spruce
# branch tips droop to -2.8/-3.5 m, WhitePine has no ground ring), so the trunk base is that ring, not the lowest
# vertex (probe225d/fix226a used the lowest 20 vertices). Trunk base = world position of the local z~0 vertex ring
# (meshes without one, e.g. WhitePine, are left alone). Rules, using the evaluated terrain (modifiers on):
#  (a) scene-wide: a tree whose origin is > 0.3 m BELOW the top terrain, where that terrain agrees with dtm_1m within 0.7 m,
#      is raised to terrain - 0.05 (raise only; never lowers a tree into paving or a planter).
#  (b) the 30 trees fix226a moved (W53 area) are re-seated both ways to terrain - 0.05 by origin (undoes the lowest-vertex
#      offset for PinOak instances).
import bpy, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
DRY=os.environ.get('DRY','0')=='1'
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
sv=[m.show_viewport for m in t.modifiers]
for m in t.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); me=e.to_mesh(); M=t.matrix_world
B=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear()
for m,s in zip(t.modifiers,sv): m.show_viewport=s
prev=set(r[0] for r in json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws226/fix226a_report.json'))['trees'])
up=[]; two=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or not o.data.name.startswith('Tree_') or o.parent is not None or o.name.startswith('Tree_'): continue  # Tree_* = library templates at the origin
    Mw=o.matrix_world; ring=[v.co for v in o.data.vertices if abs(v.co.z)<0.03]
    if len(ring)<3: continue   # no trunk-base ring at local z=0 (e.g. WhitePine): leave
    w=[Mw@c for c in ring]; x=sum(p.x for p in w)/len(w); y=sum(p.y for p in w)/len(w); z=min(p.z for p in w)
    if not (-249<x<249 and -249<y<249): continue
    h=B.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    if h[0] is None: continue
    tz=h[0].z; d=float(A[int(y+250),int(x+250)])
    if o.name in prev:
        dz=(tz-0.05)-z
        if abs(dz)>0.05: two.append((o.name,round(x,1),round(y,1),round(z,2),round(tz,2),round(dz,2)));  o.location.z+= 0 if DRY else dz
    elif z<tz-0.3 and abs(tz-d)<0.7:
        dz=(tz-0.05)-z; up.append((o.name,round(x,1),round(y,1),round(z,2),round(tz,2),round(dz,2)))
        if not DRY: o.location.z+=dz
print('F226B (a) raised',len(up),'max',max([r[5] for r in up] or [0]),'(dry)' if DRY else '',flush=True)
print('F226B (b) re-seated fix226a trees',len(two),flush=True)
for r in sorted(up,key=lambda r:-r[5])[:12]: print('F226B up',r,flush=True)
for r in two: print('F226B two',r,flush=True)
json.dump({'up':up,'two':two},open('/workspace/nj-scenes/montclair-state/scripts/ws226/fix226b_report.json','w'))

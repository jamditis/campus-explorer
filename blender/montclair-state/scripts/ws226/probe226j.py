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
import collections
c=collections.Counter(); fl=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or not o.data.name.startswith('Tree_') or o.parent is not None or o.name.startswith('Tree_'): continue
    Mw=o.matrix_world; ring=[v.co for v in o.data.vertices if abs(v.co.z)<0.03]
    if len(ring)<3: c['noring']+=1; continue
    w=[Mw@q for q in ring]; x=sum(p.x for p in w)/len(w); y=sum(p.y for p in w)/len(w); z=min(p.z for p in w)
    h=B.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    if h[0] is None: c['nohit']+=1; continue
    dz=z-h[0].z; c['buried>0.3' if dz<-0.3 else 'float>0.3' if dz>0.3 else 'ok']+=1
    if dz>0.3: fl.append((o.name,round(x,1),round(y,1),round(dz,2)))
print('P226J',dict(c),flush=True)
for r in sorted(fl,key=lambda r:-r[3])[:15]: print('P226J F',r,flush=True)
json.dump(fl,open('/workspace/nj-scenes/montclair-state/scripts/ws226/probe226j_float.json','w'))
import sys; sys.stdout.flush(); os._exit(0)

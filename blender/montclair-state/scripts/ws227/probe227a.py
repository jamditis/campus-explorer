# W53c probe: SE corner base faces vs dtm_1m; evaluated top terrain vs dtm_1m; objects in the corner
import bpy, sys, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def d(x,y): return float(A[min(499,max(0,int(y+250))),min(499,max(0,int(x+250)))])
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
print('P227 mods',[(m.name,m.type,m.show_render) for m in t.modifiers][:60],flush=True)
fs=[]
for p in me.polygons:
    c=p.center
    if c.x>140 and c.y<-50 and p.area>500:
        vs=[me.vertices[i].co for i in p.vertices]
        dz=[round(v.z-d(v.x,v.y),2) for v in vs]
        fs.append((p.index,round(p.area),len(vs),round(c.x,1),round(c.y,1),dz[:12]))
print('P227 big SE base faces',len(fs),flush=True)
for f in fs: print('P227 F',f,flush=True)
sv=[m.show_viewport for m in t.modifiers]
for m in t.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); tm=e.to_mesh()
B=BVHTree.FromPolygons([v.co.copy() for v in tm.vertices],[p.vertices[:] for p in tm.polygons]); e.to_mesh_clear()
for m,s in zip(t.modifiers,sv): m.show_viewport=s
G=[]
for x in range(140,250,5):
    for y in range(-250,-40,5):
        h=B.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        G.append((x,y,None if h[0] is None else round(h[0].z-d(x,y),2)))
hi=[g for g in G if g[2] is not None and g[2]>0.5]; lo=[g for g in G if g[2] is not None and g[2]<-0.5]; nh=[g for g in G if g[2] is None]
print('P227 grid',len(G),'hi>0.5',len(hi),'lo<-0.5',len(lo),'nohit',len(nh),flush=True)
import collections
c=collections.Counter((g[0]//20*20,g[1]//20*20) for g in hi)
print('P227 hi cells',sorted(c.items()),flush=True)
print('P227 hi max',max(hi,key=lambda g:g[2]) if hi else None,flush=True)
ob=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o==t or o.hide_render: continue
    bb=[o.matrix_world@Vector(b) for b in o.bound_box]
    x0=min(b.x for b in bb);x1=max(b.x for b in bb);y0=min(b.y for b in bb);y1=max(b.y for b in bb)
    if x1>150 and y0<-60 and x0<250 and y1>-250:
        ob.append((o.name,round(x0),round(x1),round(y0),round(y1),round(min(b.z for b in bb),1),len(o.modifiers)))
print('P227 objs in SE corner',len(ob),flush=True)
for r in ob[:80]: print('P227 O',r,flush=True)
json.dump({'faces':fs,'grid':G,'objs':ob},open('/workspace/nj-scenes/montclair-state/scripts/ws227/'+os.environ.get('TAG','probe227a')+'.json','w'))
sys.stdout.flush(); os._exit(0)

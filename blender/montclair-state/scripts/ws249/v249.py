# ws249 check: top surface of (evaluated Terrain_LiDAR_DTM_1m + ws248 patch + ws249 SE patch) vs LiDAR in the SE berm box,
# 0.5 m samples; counts holes (no hit) and |d| bands. Read-only.
import bpy, os, sys, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws249b.blend')
NM=['Terrain_LiDAR_DTM_1m','WS248_E_stand_LiDAR2023_ground_patch_1m','WS249_SE_berm_LiDAR2023_ground_patch_1m']
with bpy.data.libraries.load(F) as (a,b): b.objects=[n for n in NM if n in a.objects]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
for m in b.objects[0].modifiers:
    if 'skirt_under' in m.name.lower(): m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get(); box=(-206,-168,38,76); TT=[]
for o in b.objects:
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(box[0]<vs[i].x<box[1] and box[2]<vs[i].y<box[3] for i in p.vertices)]
    TT.append((o.name,BVHTree.FromPolygons(vs,ps) if ps else None)); print('V249',o.name,'faces in box',len(ps),flush=True)
G23=np.load('scripts/ws248/g1m_23.npy'); G17=np.load('scripts/ws248/g1m_17.npy'); G=np.where(np.isfinite(G23),G23,G17)
R=[];holes=0;win={};HL=[]
for y in np.arange(40.25,74,0.5):
    for x in np.arange(-204.25,-170,0.5):
        best=None
        for n,t in TT:
            if t is None: continue
            h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
            if h[0] is not None and (best is None or h[0].z>best[1]): best=(n,h[0].z)
        if best is None:
            holes+=1; HL.append((x,y)); continue
        l=G[int(y+20),int(x+320)]
        if np.isfinite(l): R.append((x,y,best[1]-l)); win[best[0]]=win.get(best[0],0)+1
R=np.array(R); d=R[:,2]
if HL:
    H=np.array(HL); print('V249 hole x %.2f..%.2f y %.2f..%.2f'%(H[:,0].min(),H[:,0].max(),H[:,1].min(),H[:,1].max()),flush=True)
hi=R[R[:,2]>0.3]
if len(hi): print('V249 high x %.1f..%.1f y %.1f..%.1f'%(hi[:,0].min(),hi[:,0].max(),hi[:,1].min(),hi[:,1].max()),flush=True)
print('V249 holes',holes,'n',len(d),'>0.3',(d>0.3).sum(),'<-0.3',(d<-0.3).sum(),'max %.2f min %.2f'%(d.max(),d.min()),'top',win,flush=True)
for y in range(72,40,-4):
    print('V249 y%3d '%y+' '.join('%5.2f'%np.median(R[(R[:,0]>=x)&(R[:,0]<x+2)&(R[:,1]>=y)&(R[:,1]<y+4),2]) for x in range(-204,-170,2)),flush=True)
sys.stdout.flush(); os._exit(0)

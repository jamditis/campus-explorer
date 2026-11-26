# ws249: PK_Feliciano_west_DTM_fill_UNVERIFIED EVALUATED (its own modifiers on) vs 2023 LiDAR on the W slope; vertex density. Read-only.
import bpy, numpy as np, sys, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ON=os.environ.get('OBJ','PK_Feliciano_west_DTM_fill_UNVERIFIED')
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state.blend')) as (a,b): b.objects=[ON]
T=b.objects[0]; bpy.context.scene.collection.objects.link(T)
print('PK249 mods',[(m.name,m.show_viewport) for m in T.modifiers],flush=True)
dg=bpy.context.evaluated_depsgraph_get(); e=T.evaluated_get(dg); me=e.to_mesh(); M=T.matrix_world
vs=[M@v.co for v in me.vertices]
B=(-340,-280,90,220)
inb=[v for v in vs if B[0]<v.x<B[1] and B[2]<v.y<B[3]]
print('PK249 verts total',len(vs),'in W-slope box',len(inb),'density/m2 %.2f'%(len(inb)/((B[1]-B[0])*(B[3]-B[2]))),flush=True)
ar=[p.area for p in me.polygons if B[0]<p.center.x<B[1] and B[2]<p.center.y<B[3]]
if ar: print('PK249 face area median %.2f max %.1f'%(np.median(ar),max(ar)),flush=True)
t=BVHTree.FromPolygons(vs,[p.vertices[:] for p in me.polygons])
G=np.load('scripts/ws249/g1m_w23.npy'); X0,Y0=-340.,-20.; R=[]
for y in np.arange(-18,218,2.0):
    for x in np.arange(-338,-252,2.0):
        h=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600)
        if h[0] is None: continue
        l=G[int(y-Y0),int(x-X0)]
        if np.isfinite(l): R.append((x,y,h[0].z-l))
R=np.array(R); np.save('scripts/ws249/pk249_%s.npy'%os.environ.get('TAG','before'),R)
d=R[:,2]; print('PK249 eval n',len(d),'|d|>0.3',(abs(d)>0.3).sum(),'>1',(abs(d)>1).sum(),'max %.2f min %.2f'%(d.max(),d.min()),flush=True)
sys.stdout.flush(); os._exit(0)

# ws248: EVALUATED terrain (first ground hit among the terrain stack) vs LiDAR ground, 2 m raster, 10 m block medians
import bpy, os, sys, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws248a.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
T=b.objects[0]; bpy.context.scene.collection.objects.link(T)
for m in T.modifiers:
    if 'skirt_under' in m.name.lower() or m.name in os.environ.get('DIS','').split(): m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get(); e=T.evaluated_get(dg); me=e.to_mesh(); M=T.matrix_world
vs=[M@v.co for v in me.vertices]; box=(-322,-140,-20,220)
ps=[p.vertices[:] for p in me.polygons if any(box[0]<vs[i].x<box[1] and box[2]<vs[i].y<box[3] for i in p.vertices)]
nv=sum(1 for v in vs if box[0]<v.x<box[1] and box[2]<v.y<box[3]); print('E248 eval verts in box',nv,'faces',len(ps),flush=True)
t=BVHTree.FromPolygons(vs,ps)
G23=np.load(S:='/workspace/nj-scenes/montclair-state/scripts/ws248/g1m_23.npy'); G17=np.load(S.replace('_23','_17')); G=np.where(np.isfinite(G23),G23,G17)
X0,Y0=-320.,-20.; R={}
for y in np.arange(-18,218,2.0):
    for x in np.arange(-318,-142,2.0):
        h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
        if h[0] is None: continue
        l=G[int(y-Y0),int(x-X0)]
        if np.isfinite(l): R[(x,y)]=h[0].z-l
np.save('/workspace/nj-scenes/montclair-state/scripts/ws248/e248.npy',np.array([(k[0],k[1],v) for k,v in R.items()]))
for by in range(150,30,-10):
    row=[]
    for bx in range(-260,-170,5):
        d=[v for (x,y),v in R.items() if bx<=x<bx+10 and by<=y<by+10]
        row.append('%5.1f'%np.median(d) if len(d)>3 else '   . ')
    print('E248 y%4d '%by+' '.join(row),flush=True)
sys.stdout.flush(); os._exit(0)

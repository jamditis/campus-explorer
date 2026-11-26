# ws250 read-only: fine transects of evaluated Terrain (grooves?) + attribute check
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws250d.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
T=b.objects[0]; bpy.context.scene.collection.objects.link(T)
print('TR250 base attrs',[(a.name,a.domain,a.data_type) for a in T.data.attributes],flush=True)
dg=bpy.context.evaluated_depsgraph_get(); me=T.evaluated_get(dg).to_mesh(); M=T.matrix_world
print('TR250 eval attrs',[(a.name,a.domain) for a in me.attributes],flush=True)
vs=[M@v.co for v in me.vertices]; box=(-175,-140,175,200)
ps=[p.vertices[:] for p in me.polygons if box[0]<(M@p.center).x<box[1] and box[2]<(M@p.center).y<box[3]]
t=BVHTree.FromPolygons(vs,ps)
for y in (185.0,190.0,195.0):
    zs=[];ns=[]
    for x in np.arange(-170,-146,0.25):
        h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
        zs.append(h[0].z if h[0] else np.nan); ns.append(h[1].z if h[0] else np.nan)
    zs=np.array(zs); d2=zs[2:]-2*zs[1:-1]+zs[:-2]
    print('TR250 y',y,'z range %.2f..%.2f'%(np.nanmin(zs),np.nanmax(zs)),'max|d2| %.3f'%np.nanmax(abs(d2)),'normal z min %.4f'%np.nanmin(ns),flush=True)
    print('TR250 z',' '.join('%.2f'%z for z in zs[::4]),flush=True)
# smooth flags / sharp edges in the eval mesh near box
sm=[p.use_smooth for p in me.polygons if box[0]<(M@p.center).x<box[1] and box[2]<(M@p.center).y<box[3]]
print('TR250 smooth frac %.2f n %d'%(np.mean(sm),len(sm)),flush=True)
os._exit(0)

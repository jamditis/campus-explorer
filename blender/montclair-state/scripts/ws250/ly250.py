import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws250e.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
T=b.objects[0]; bpy.context.scene.collection.objects.link(T)
dg=bpy.context.evaluated_depsgraph_get(); me=T.evaluated_get(dg).to_mesh(); M=T.matrix_world
vs=[M@v.co for v in me.vertices]; box=(-196,-140,141,214)
ps=[p.vertices[:] for p in me.polygons if any(box[0]-20<vs[i].x<box[1]+20 and box[2]-20<vs[i].y<box[3]+20 for i in p.vertices)]
t=BVHTree.FromPolygons(vs,ps); multi=[]; n=0
for y in np.arange(176,200,0.37):
    for x in np.arange(-170,-146,0.37):
        o=Vector((x,y,300)); hs=[]
        for k in range(4):
            h=t.ray_cast(o,Vector((0,0,-1)),600)
            if h[0] is None: break
            hs.append((h[0].z,h[1].z)); o=h[0]-Vector((0,0,0.002))
        n+=1
        if len(hs)>1 and hs[0][0]-hs[1][0]<1.0: multi.append((round(x,2),round(y,2),[ (round(a,3),round(b,2)) for a,b in hs]))
print('LY250 samples',n,'with 2+ layers within 1 m',len(multi),flush=True)
for m in multi[::max(1,len(multi)//25)]: print('LY250',m,flush=True)
os._exit(0)

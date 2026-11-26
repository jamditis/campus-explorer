# ws253 read-only check: evaluated terrain (GN joins on) vs the new W63d objects (top surface clearance), 0.25 m sampling
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws253b.blend')
NEW=['WS253_W63d_Feliciano_E_walk_and_stairs_UNVERIFIED','WS253_W63d_Feliciano_E_walk_slabs','WS253_W63d_Feliciano_E_stair_cheek_walls_UNVERIFIED','WS253_W63d_diagonal_walk_grass_plot_NE_to_Dickson_NW','WS253_W63d_Feliciano_E_recess_apron_raise_only_UNVERIFIED']
with bpy.data.libraries.load(F) as (a,b): b.objects=[n for n in ['Terrain_LiDAR_DTM_1m','WS250_W63_lawn_LiDAR2023_ground_patch_1m','WS251_W63b_passage_LiDAR2023_ground_patch_1m']+NEW if n in a.objects]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
dg=bpy.context.evaluated_depsgraph_get(); em=T.evaluated_get(dg).to_mesh(); M=T.matrix_world
vs=[M@v.co for v in em.vertices]
ps=[p.vertices[:] for p in em.polygons if any(-200<vs[i].x<-170 and 150<vs[i].y<190 for i in p.vertices)]
bt=BVHTree.FromPolygons(vs,ps)
for n in NEW:
    o=bpy.data.objects[n]; bo=BVHTree.FromObject(o,dg); bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0,x1=min(v.x for v in bb),max(v.x for v in bb); y0,y1=min(v.y for v in bb),max(v.y for v in bb)
    d=[];pk=[]
    for x in np.arange(x0+0.05,x1,0.25):
        for y in np.arange(y0+0.05,y1,0.25):
            h=bo.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600)
            if not h[0]: continue
            g=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600)
            if not g[0]: pk.append(('hole',round(x,2),round(y,2))); continue
            dd=h[0].z-g[0].z; d.append(dd)
            if dd<0.0: pk.append((round(x,2),round(y,2),round(dd,3)))
    d=np.array(d); print('Q253',n,'n',len(d),'top-ground min %.3f p5 %.3f p50 %.3f max %.3f'%(d.min(),np.percentile(d,5),np.median(d),d.max()),'pokes',len(pk),pk[:12],flush=True)
os._exit(0)

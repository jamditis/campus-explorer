# ws250 probe (READ-ONLY): W63 box — evaluated z of each ground-ish object vs 2023 LiDAR class-2 (2017 fallback), 2 m grid
import bpy, os, sys, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state.blend')
NAMES=os.environ['NAMES'].split('|')
with bpy.data.libraries.load(F) as (a,b): b.objects=NAMES
for o in b.objects:
    bpy.context.scene.collection.objects.link(o)
    print('P250 MODS',o.name,[(m.name,m.show_viewport,m.show_render) for m in o.modifiers],flush=True)
dg=bpy.context.evaluated_depsgraph_get()
box=(-200,-106,140,216)
G23=np.load('scripts/ws248/g1m_23.npy'); G17=np.load('scripts/ws248/g1m_17.npy'); G0=np.where(np.isfinite(G23),G23,G17+0.12)
E=np.load('scripts/ws250/g1m_e23.npy'); G=np.full((250,220),np.nan); G[0:240,0:180]=G0; S_=G[160:250,160:220]; G[160:250,160:220]=np.where(np.isfinite(S_),S_,E)
T={}
for o in b.objects:
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(box[0]-4<vs[i].x<box[1]+4 and box[2]-4<vs[i].y<box[3]+4 for i in p.vertices)]
    print('P250',o.name,'faces in box',len(ps),flush=True)
    if ps: T[o.name]=BVHTree.FromPolygons(vs,ps)
    e.to_mesh_clear()
R={}
for y in np.arange(box[2],box[3],2.0):
    for x in np.arange(box[0],box[1],2.0):
        l=G[int(y+20),int(x+320)]
        row={}
        for n,t in T.items():
            h=t.ray_cast(Vector((x+0.5,y+0.5,300)),Vector((0,0,-1)),400)
            if h[0] is not None: row[n]=h[0].z
        R[(x,y)]=(l,row)
import pickle; pickle.dump(R,open('scripts/ws250/p250_'+os.environ.get('TAGP','x')+'.pkl','wb'))
print('P250 done',len(R),flush=True); os._exit(0)

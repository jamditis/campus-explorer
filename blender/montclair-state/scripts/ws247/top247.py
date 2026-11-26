# ws247: which ground surface is on top over the east bank (x,y box) - append only the 7 ground stacks, evaluate one at a time
import bpy, os, numpy as np, gc
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F=os.environ.get('FILE','/workspace/nj-scenes/montclair-state/montclair_state.blend')
G=['Terrain_LiDAR_DTM_1m','WS60_terrain_edge_apron_LiDAR_to_skirt','M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam','PK_Feliciano_west_DTM_fill_UNVERIFIED','PZ_Feliciano_SW_DTM_edge_feather_UNVERIFIED','Context_skirt_3DEP_ortho_4km']+os.environ.get('G247X','').split('|')
with bpy.data.libraries.load(F) as (a,b):
    have=set(a.objects); b.objects=[n for n in have if n in G or n.startswith('WS68_RHD_ground_northDTM')]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
print('T247 appended',[o.name[:40] for o in b.objects],flush=True)
BX=[float(v) for v in os.environ.get('BOX','-236,-200,112,150').split(',')]; ST=float(os.environ.get('STEP','1'))
xs=np.arange(BX[0],BX[1]+1e-6,ST); ys=np.arange(BX[2],BX[3]+1e-6,ST)
H={}
for o in b.objects:
    for m in o.modifiers:
        if m.type=='NODES' and 'skirt_under' in m.name.lower(): m.show_viewport=False
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    vs=[M@v.co for v in me.vertices]
    # keep only polys near box
    ps=[p.vertices[:] for p in me.polygons if any(BX[0]-3<vs[i].x<BX[1]+3 and BX[2]-3<vs[i].y<BX[3]+3 for i in p.vertices)]
    mats=[(p.material_index) for p in me.polygons]
    if ps:
        t=BVHTree.FromPolygons(vs,ps); z=np.full((len(ys),len(xs)),np.nan)
        for j,y in enumerate(ys):
            for i,x in enumerate(xs):
                h=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600)
                if h[0] is not None: z[j,i]=h[0].z
        H[o.name]=z; print('T247',o.name[:40],'polys in box',len(ps),'cells hit',int(np.isfinite(z).sum()),flush=True)
    e.to_mesh_clear(); del vs, ps; gc.collect()
T=H.get('Terrain_LiDAR_DTM_1m')
for n,z in H.items():
    if n=='Terrain_LiDAR_DTM_1m' or T is None: continue
    d=z-T; ok=np.isfinite(d)
    up=ok&(d>-0.02)
    print('T247 vs terrain',n[:40],'overlap',int(ok.sum()),'above(>-2cm)',int(up.sum()),'max',round(float(np.nanmax(d)),2) if ok.any() else None,flush=True)
    for j,i in list(zip(*np.where(up)))[:40]: print('T247 up',n[:20],round(xs[i],1),round(ys[j],1),round(float(d[j,i]),2),flush=True)
np.save('/workspace/nj-scenes/montclair-state/scripts/ws247/top247_T.npy',T if T is not None else np.zeros(1))
os._exit(0)

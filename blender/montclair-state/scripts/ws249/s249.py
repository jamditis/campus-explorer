# ws249: on the W slope box, does any other ground (evaluated Context_skirt_3DEP_ortho_4km, M3b corridor, PZ feather,
# WS60 apron, WS68) now stand ABOVE the re-snapped PK fill? Read-only; F=file.
import bpy, os, sys, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws249d.blend')
NM=['PK_Feliciano_west_DTM_fill_UNVERIFIED','Context_skirt_3DEP_ortho_4km','M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam','PZ_Feliciano_SW_DTM_edge_feather_UNVERIFIED','WS60_terrain_edge_apron_LiDAR_to_skirt','fs_turf']
with bpy.data.libraries.load(F) as (a,b): b.objects=[n for n in NM if n in a.objects]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); box=(-342,-280,90,218); TT={}
for o in b.objects:
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(box[0]<vs[i].x<box[1] and box[2]<vs[i].y<box[3] for i in p.vertices)]
    TT[o.name]=BVHTree.FromPolygons(vs,ps) if ps else None
def z(t,x,y):
    if t is None: return None
    h=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return None if h[0] is None else h[0].z
pk=TT[NM[0]]; C={}
for y in np.arange(92,216,1.0):
    for x in np.arange(-340,-282,1.0):
        zp=z(pk,x,y)
        if zp is None: continue
        for n,t in TT.items():
            if n==NM[0]: continue
            zo=z(t,x,y)
            if zo is not None and zo>zp+0.02: C.setdefault(n,[]).append((x,y,zo-zp))
for n,L in C.items():
    A=np.array(L); print('S249',n[:40],'above PK samples',len(A),'max %.2f'%A[:,2].max(),'x %.0f..%.0f y %.0f..%.0f'%(A[:,0].min(),A[:,0].max(),A[:,1].min(),A[:,1].max()),flush=True)
print('S249 done',os.environ.get('F'),flush=True)
sys.stdout.flush(); os._exit(0)

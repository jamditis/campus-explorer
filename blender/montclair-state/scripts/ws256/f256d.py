# ws256d: along the ws254 walk extension's E edge (x -189.5, y 183.5..190.6) the lawn dipped 6-13 cm below the edge within
# ~0.5 m (probe256e: a gutter at the bottom of the 2023 LiDAR swale; the lawn rises above the edge again 1 m out), so the walk's
# edge face showed. Ground verts (terrain + W63 patches; the 1 m patch columns straddle the edge) from 1.0 m under the walk to
# 0.9 m E of the edge are raised (raise-only, max 0.25 m): under the walk to edge - 5 cm, outside to edge - 2 cm feathered to 0.
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F256D'
eo=bpy.data.objects['WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED']; M=eo.matrix_world
vs=[M@v.co for v in eo.data.vertices]; EB=BVHTree.FromPolygons(vs,[p.vertices[:] for p in eo.data.polygons])
def ez(y):
    h=EB.ray_cast(Vector((-189.56,y,300)),Vector((0,0,-1)),400); return h[0].z if h[0] else None
XE=-189.5; R=0.9
for gnm in ('Terrain_LiDAR_DTM_1m','WS250_W63_lawn_LiDAR2023_ground_patch_1m','WS251_W63b_passage_LiDAR2023_ground_patch_1m'):
    go=bpy.data.objects.get(gnm)
    if not go: continue
    Mg=go.matrix_world; Mgi=Mg.inverted(); k=0; mx=0
    for v in go.data.vertices:
        w=Mg@v.co
        if 183.6<=w.y<=190.5 and XE-1.0<=w.x<=XE+R:
            e=ez(w.y)
            if e is None: continue
            tgt=(e-0.05) if w.x<=XE else w.z+(1.0-(w.x-XE)/R)*max(0.0,(e-0.02)-w.z)
            if tgt-w.z>0.25: continue
            if tgt>w.z+1e-4: mx=max(mx,tgt-w.z); v.co=Mgi@Vector((w.x,w.y,tgt)); k+=1
    go.data.update(); print(TAG,'raised',gnm,k,'max %.3f'%mx,flush=True)

# ws174d: UNIFY #82 — diagonal light/dark bands on the front-yard lawn = FLAT-shaded 1 m DTM triangles (each facet lit differently).
# Shade smooth the lawn-ground meshes that were flat (normals only; no geometry change). WS110 patch was already smooth.
import bpy
for n in ['WS172_frontyards_S_of_NormalAve_W_DTM2023_J5D5','WS163_walk_back_lawn_lip_S_UNVERIFIED','WS163_walk_back_lawn_lip_N_UNVERIFIED','WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED']:
    o=bpy.data.objects.get(n)
    if not o: continue
    for p in o.data.polygons: p.use_smooth=True
    o.data.update(); print('FIX174d smooth',n,len(o.data.polygons),flush=True)

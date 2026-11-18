# UNIFY #53 candidate fix (ws147, NOT yet run on main: memory-blocked).
# Hypothesis: the flat orange patches / yellow wedge N of Freeman are Terrain_LiDAR_DTM_1m faces using
# 'Lawn_Varied_Oct_local_fade' (ortho2020-driven tint + ScatteredLeaves where the leaf-off 2020 ortho is brown/shadowed),
# sitting beside faces already on 'COLE_lawn_post2020_bs' (the lawn material used N of y -164 and for UNIFY #1).
# Fix = put those faces on COLE_lawn_post2020_bs inside the box below (same treatment as UNIFY #1, ws110).
# Run inside a loaded main (or test copy), then render WS143_CAM_eye_forecourt_from_N_aisle to confirm patches are gone.
import bpy
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=o.data; mw=o.matrix_world
names=[s.material.name if s.material else None for s in o.material_slots]
src=names.index('Lawn_Varied_Oct_local_fade'); dst=names.index('COLE_lawn_post2020_bs')
n=0
for p in me.polygons:
    if p.material_index!=src: continue
    c=mw@p.center
    if -92<c.x<-55 and -182<c.y<-150:
        p.material_index=dst; n+=1
me.update(); print("FIX53_REASSIGNED",n)

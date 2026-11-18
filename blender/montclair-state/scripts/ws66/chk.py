import bpy
from mathutils import Vector
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src) as (fr,to): n=[x for x in fr.objects if x.startswith(('KY_','LH_college','KX_','LF_','ey_','cf_','ce_','fu_','eu_','gb_','fo_'))]+['WS27_CollegeAve_carriageway_2020ortho']
with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=n
for o in to.objects:
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]; zs=[p.z for p in bb]
    print('CK',o.name[:50],round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),round(min(zs),1),round(max(zs),1))

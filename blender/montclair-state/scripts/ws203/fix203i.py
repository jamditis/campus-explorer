# ws203 W21 (new, E-lawn eye 0444): dark notch beside the Lot 3 S strip's E end = the WS163 lawn patch's 1 m LiDAR vertex at (-300,-237)
# on its E edge peaks 7-8 cm above the finer (0.2 m) WS191b gap lawn it meets -> a proud ridge whose E face is in shadow.
# Designer call: one lawn; the coarse 1 m patch tucks 4 mm under the fine fill at their shared edge (lawn only, no paving touched).
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=[o for o in bpy.data.objects if o.name.startswith('WS163_ground_patch_W_of_WS110')][0]
B=[o for o in bpy.data.objects if o.name.startswith('WS191b_Lot3_S_gap_lawn')][0]; mb=B.matrix_world
T=BVHTree.FromPolygons([mb@v.co for v in B.data.vertices],[tuple(p.vertices) for p in B.data.polygons])
mw=P.matrix_world; mi=mw.inverted(); n=0
for v in P.data.vertices:
    p=mw@v.co
    if not (-300.3<p.x<-299.7 and -238.4<p.y<-235.6): continue
    h=T.ray_cast(Vector((p.x+0.02,p.y,p.z+0.5)),Vector((0,0,-1)),1.0)
    if h[0] is None: continue
    t=h[0].z-0.004
    if 0.003<p.z-t<0.12: print('F203i',tuple(round(c,3) for c in p),'->',round(t,3),flush=True); p.z=t; v.co=mi@p; n+=1
P.data.update(); print('F203i lowered',n,flush=True)

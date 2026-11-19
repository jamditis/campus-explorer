# ws224d (WS215/landing seam by the RHD SE crossing, ws222 NEXT): (1) the WS72 landing W edge (x -255.5) stands 0.1-1.7 cm
# over the WS215 street-level walk it laps (WS215 runs 3 cm under it), a lit step line in the eye-from-W view. Raise-only:
# WS215 verts under the landing are RAISED to landing top - 2 mm. (2) the landing SW corner v0/v1 juts 19 cm south of the
# WS215 S edge onto the College Ave asphalt as a pointed plate; v0/v1 moved north (horizontal only, same z) onto the
# WS215 S edge line (y -53.10). Asphalt under it stays (no hole).
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; ML=L.matrix_world; MLI=ML.inverted()
F=[o for o in bpy.data.objects if o.name.startswith('WS215_RHD_SE_core_street_level')][0]; MF=F.matrix_world; MFI=MF.inverted()
TL=BVHTree.FromPolygons([ML@v.co for v in L.data.vertices],[p.vertices[:] for p in L.data.polygons if (ML.to_3x3()@p.normal).z>0.3])
n=0
for v in F.data.vertices:
    w=MF@v.co
    if not (-255.55<w.x<-255.0 and -54<w.y<-51): continue
    h=TL.ray_cast(Vector((w.x,w.y,130)),Vector((0,0,-1)))
    if h[0] is None: continue
    zt=h[0].z-0.002
    if zt>w.z and zt-w.z<0.05:
        print('F224D WS215 v%d (%.3f,%.3f) %.3f -> %.3f'%(v.index,w.x,w.y,w.z,zt),flush=True); w.z=zt; v.co=MFI@w; n+=1
F.data.update(); print('F224D raised',n,flush=True)
for i in (0,1):
    v=L.data.vertices[i]; w=ML@v.co; assert abs(w.x+255.5)<1e-3 and abs(w.y+53.283)<2e-3,(w.x,w.y)
    w.y=-53.10; v.co=MLI@w
L.data.update(); print('F224D v0/v1 moved to y -53.10',flush=True)

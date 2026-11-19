# ws222c: RHD SE crosswalk flush edge. The WS215 street-level sidewalk's road-side top edge (v525..v600, a straight run along
# the depressed-curb crossing) sat 3-10 cm BELOW the road surface just outside it (WS214 underfill / KY / WS67 rows at
# 125.10-125.16), so the asphalt faces rose through the walk edge as a sawtooth and the walk end stood 6-9 cm below the
# Kasser landing at their seam. A depressed-curb crossing is flush (ADA: <= 6 mm lip), so each edge top vert is RAISED to the
# road surface 8 cm outside it + 5 mm (raise-only; no paving lowered; bottom verts unchanged).
import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
o=[o for o in bpy.data.objects if o.name.startswith('WS215_RHD_SE_core_street_level_sidewalk')][0]; M=o.matrix_world; MI=M.inverted()
ROAD=('WS214_N_berm_tip_gap_asphalt','KY_college_ave_carriageway','WS67_CollegeAve_gap_asphalt')
def road(x,y):
    z=128.0
    for _ in range(10):
        h,loc,n,i,ob,m=sc.ray_cast(dg,Vector((x,y,z)),Vector((0,0,-1)))
        if not h: return None
        if ob.name.startswith(ROAD): return loc.z
        z=loc.z-0.001
    return None
EDGE=[525,540,555,570,585,600]
# outward normal of the edge line (toward the road, -y side)
p0=(M@o.data.vertices[525].co).xy; p1=(M@o.data.vertices[600].co).xy; d=(p1-p0).normalized(); nrm=Vector((d.y,-d.x))
if nrm.y>0: nrm=-nrm
for i in EDGE:
    v=o.data.vertices[i]; w=M@v.co; q=w.xy+nrm*0.08; rz=road(q.x,q.y)
    if rz is None: print('F222C v%d no road'%i,flush=True); continue
    nz=max(w.z,rz+0.005)
    print('F222C v%d (%.3f,%.3f) z %.3f road %.3f -> %.3f'%(i,w.x,w.y,w.z,rz,nz),flush=True); w.z=nz; v.co=MI@w
o.data.update()

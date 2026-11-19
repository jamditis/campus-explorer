# ws222b (found in the ws222a test renders): at the RHD SE / Kasser crosswalk (College Ave, x -256..-254) asphalt sheets
# (WS214 N berm-tip underfill 125.16-125.19, WS67 gap asphalt 125.155-125.163, KY carriageway 125.20) lie ABOVE the walk
# slabs they run under (WS72 Kasser landing W end 125.14-125.19, WS215 RHD SE street-level sidewalk end 125.05-125.16), so a
# dark asphalt wedge reached up into the walk between the curb end and the sidewalk end. Every asphalt vert whose XY lies
# under WS72 or WS215 and sits above (slab top - 2 cm) is set to slab top - 3 cm. Walks are not moved.
import bpy
from mathutils import Vector
WALKS=[bpy.data.objects[n] for n in ('WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width',)]+[o for o in bpy.data.objects if o.name.startswith('WS215_RHD_SE_core_street_level_sidewalk')]
def slab_top(x,y,z):
    best=None
    for s in WALKS:
        SM=s.matrix_world; SI=SM.inverted()
        ok,loc,n,fi=s.ray_cast(SI@Vector((x,y,z+2.0)),(SI.to_3x3()@Vector((0,0,-1))).normalized(),distance=6.0)
        if ok:
            hz=(SM@loc).z
            if abs(hz-z)<0.6 and (best is None or hz>best[0]): best=(hz,s.name[:6])
    return best
A=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith('WS214_N_berm_tip_gap_asphalt_underfill') or o.name.startswith('WS67_CollegeAve_gap_asphalt') or o.name.startswith('KY_college_ave_carriageway_asphalt'))]
for a in A:
    M=a.matrix_world; MI=M.inverted(); n=0
    for i,v in enumerate(a.data.vertices):
        w=M@v.co
        if not (-256.2<=w.x<=-253.8 and -54.2<=w.y<=-52.3): continue
        b=slab_top(w.x,w.y,w.z)
        if b and w.z>b[0]-0.02:
            nz=b[0]-0.03; print('F222B %s v%d (%.3f,%.3f) z %.3f -> %.3f under %s'%(a.name[:6],i,w.x,w.y,w.z,nz,b[1]),flush=True)
            w.z=nz; v.co=MI@w; n+=1
    a.data.update(); print('F222B',a.name[:30],'moved',n,flush=True)

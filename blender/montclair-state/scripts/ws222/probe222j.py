# ws222: after fix222i, list asphalt verts within 1 cm of (or above) the crossing walk tops they run under
import bpy
from mathutils import Vector
PFX=('WS214_N_berm_tip_gap_asphalt_underfill','WS67_CollegeAve_gap_asphalt','KY_college_ave_carriageway_asphalt')
A=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(PFX)]
BOX=(-257.2,-253.8,-54.2,-52.1)
inb=lambda w:BOX[0]<=w.x<=BOX[1] and BOX[2]<=w.y<=BOX[3]
WALKS=[bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']]+[o for o in bpy.data.objects if o.name.startswith('WS215_RHD_SE_core_street_level_sidewalk')]
def slab_top(s,x,y,z):
    SM=s.matrix_world; SI=SM.inverted()
    ok,loc,n,fi=s.ray_cast(SI@Vector((x,y,z+2.0)),(SI.to_3x3()@Vector((0,0,-1))).normalized(),distance=6.0)
    if ok:
        hz=(SM@loc).z
        if abs(hz-z)<0.6: return hz
    return None
need=[]   # asphalt points that poke within 1 cm of a walk top
for o in A:
    M=o.matrix_world
    for v in o.data.vertices:
        w=M@v.co
        if not inb(w): continue
        for s in WALKS:
            t=slab_top(s,w.x,w.y,w.z)
            if t is not None and w.z>t-0.01: need.append((s.name,w.copy(),t))
print('P222 asphalt points too close to a walk top:',len(need),flush=True)
for nm,w,t in need: print('P222 close %s (%.3f,%.3f) asph %.3f walk %.3f'%(nm[:6],w.x,w.y,w.z,t))

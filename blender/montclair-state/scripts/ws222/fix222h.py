# ws222h W42b: the asphalt faces that cross the flush RHD SE crossing edge ran from verts hidden under the walk (125.02-125.04,
# 4-10 cm below the walk top) up to the road row just outside (125.10-125.15), so the visible part of each face sloped steeply
# and read as a crumpled dark band at eye level. Raise-only: every WS214 underfill / KY / WS67 vert under the WS215 sidewalk or
# the WS72 landing (ray test) is raised to slab top - 1.5 cm, so faces leaving the walk edge are near-flat.
import bpy
from mathutils import Vector
S=[bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']]+[o for o in bpy.data.objects if o.name.startswith('WS215_RHD_SE_core_street_level_sidewalk')]
def slab_top(x,y,z):
    best=None
    for s in S:
        SM=s.matrix_world; SI=SM.inverted()
        ok,loc,n,fi=s.ray_cast(SI@Vector((x,y,z+2.0)),(SI.to_3x3()@Vector((0,0,-1))).normalized(),distance=6.0)
        if ok:
            hz=(SM@loc).z
            if abs(hz-z)<0.6 and (best is None or hz>best): best=hz
    return best
A=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS214_N_berm_tip_gap_asphalt_underfill','WS67_CollegeAve_gap_asphalt','KY_college_ave_carriageway_asphalt'))]
for a in A:
    M=a.matrix_world; MI=M.inverted(); n=0
    for i,v in enumerate(a.data.vertices):
        w=M@v.co
        if not (-257.1<=w.x<=-255.2 and -53.6<=w.y<=-52.2): continue
        b=slab_top(w.x,w.y,w.z)
        if b is not None and w.z<b-0.015:
            print('F222H %s v%d (%.3f,%.3f) z %.3f -> %.3f'%(a.name[:6],i,w.x,w.y,w.z,b-0.015),flush=True)
            w.z=b-0.015; v.co=MI@w; n+=1
    a.data.update(); print('F222H',a.name[:30],'raised',n,flush=True)

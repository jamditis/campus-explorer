# ws222a W41b: WS70 verge grass verts that lie UNDER the WS72 Kasser landing (W of the W40 chord, along the WS69 curb back)
# sat at/above the slab top (125.53 vs slab 125.49-125.56), so grass showed through the slab as a sawtooth triangle and a
# 10-15 cm grass strip between the curb back and the slab. Drop every WS70 vert whose XY falls inside the landing footprint to
# slab top - 4 cm (grass only lowered where hidden under paving; no paving moved).
import bpy
from mathutils import Vector
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; LM=L.matrix_world; LI=LM.inverted()
g=bpy.data.objects['WS70_gap_strip_grass_berms']; GM=g.matrix_world; GI=GM.inverted()
n=0
for i,v in enumerate(g.data.vertices):
    w=GM@v.co
    if not (-253.6<=w.x<=-250.8 and -55.4<=w.y<=-52.8): continue
    o=LI@Vector((w.x,w.y,w.z+3.0)); d=(LI.to_3x3()@Vector((0,0,-1))).normalized()
    ok,loc,nrm,fi=L.ray_cast(o,d,distance=10.0)
    if not ok: continue
    hz=(LM@loc).z
    if abs(hz-w.z)>0.5: continue
    nz=hz-0.04
    if w.z>nz:
        print('F222A grass v%d (%.3f,%.3f) z %.3f -> %.3f (slab %.3f)'%(i,w.x,w.y,w.z,nz,hz),flush=True)
        w.z=nz; v.co=GI@w; n+=1
g.data.update(); print('F222A moved',n,flush=True)

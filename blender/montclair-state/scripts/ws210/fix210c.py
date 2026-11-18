# ws210 post-pass for fix210a: terrain verts in the W30 regrade box must stay >= 3 cm below any paved/bed surface that covers them
# (probe found the raised bank poking 0.4-4.5 cm through the WS205 lot-entry apron fill at x -207..-203, y -97..-95.5).
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
COV=['WS205_lotE_entry_apron_asphalt_fill_ortho2020_UNVERIFIED','Footpaths_OSM','WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_carriageway_2020ortho','WS99_lotE_padS_bed_MULCH_ortho2020_LiDARshrubs_UNVERIFIED','WS98_lotE_raised_concrete_walk_pad_LiDAR15cm_curb_ortho2020_UNV']
BV=[]
for n in COV:
    o=bpy.data.objects.get(n)
    if o is None or o.type!='MESH': print('F210c missing',n,flush=True); continue
    mw=o.matrix_world; V=[mw@v.co for v in o.data.vertices]
    F=[tuple(p.vertices) for p in o.data.polygons if -230<(mw@p.center).x<-195 and -120<(mw@p.center).y<-84]
    if F: BV.append((n,BVHTree.FromPolygons(V,F)))
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data; mw=T.matrix_world; mi=mw.inverted()
n=0
for v in me.vertices:
    p=mw@v.co
    if not (-216.3<p.x<-202.5 and -114.3<p.y<-94.0): continue
    top=None
    for nm,b in BV:
        offs=((0,0),) if nm!='WS205_lotE_entry_apron_asphalt_fill_ortho2020_UNVERIFIED' else ((0,0),(0.7,0),(-0.7,0),(0,0.7),(0,-0.7))
        for ox,oy in offs:
            h=b.ray_cast(Vector((p.x+ox,p.y+oy,p.z+3.0)),Vector((0,0,-1)),6.0)
            if h[0] is not None and h[0].z>p.z-0.5: top=h[0].z if top is None else min(top,h[0].z) if (ox or oy) else max(top,h[0].z)
    if top is not None and p.z>top-0.03:
        v.co=mi@Vector((p.x,p.y,top-0.03)); n+=1
me.update(); print('F210c clamped',n,flush=True)

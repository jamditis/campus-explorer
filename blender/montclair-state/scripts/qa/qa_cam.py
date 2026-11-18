# qa: close-up of the wing's south end (both former gaps) + an eye-level camera on the pz SW slope west of Feliciano
# and a south-end eye cam. REVERT=1 removes them.
import bpy, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
def gz(x,y):
    dg=bpy.context.evaluated_depsgraph_get(); best=None
    for on in ('Terrain_LiDAR_DTM_1m','PZ_Feliciano_SW_DTM_edge_feather_UNVERIFIED','Context_skirt_3DEP_ortho_4km'):
        o=bpy.data.objects.get(on)
        if not o: continue
        oe=o.evaluated_get(dg); mi=o.matrix_world.inverted()
        ok,loc,nr,fi=oe.ray_cast(mi@Vector((x,y,400.0)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
        if ok:
            z=(o.matrix_world@loc).z
            if best is None or z>best: best=z
    return best
CAMS=[('QA_CAM_closeup_dickson_wing_south_end',(-193.0,68.0,157.0),(-180.2,81.5,152.2),35,None),
      ('QA_CAM_eye_dickson_south_end',(-205.0,55.0,None),(-180.0,82.0,149.0),28,1.65),
      ('QA_CAM_closeup_dickson_wing_scupper',(-187.5,91.0,153.6),(-181.2,96.0,152.45),40,None),
      ('QA_CAM_eye_feliciano_sw_slope',(-268.0,70.0,None),(-240.0,95.0,None),24,1.65)]
for N,_,_,_,_ in CAMS:
    if N in bpy.data.objects:
        o=bpy.data.objects[N]; c=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(c); print('REVERTED',N)
if not REV:
    coll=bpy.data.objects['PV_CAM_closeup_dickson_north_toprow'].users_collection[0]
    for N,p,tg,lens,eh in CAMS:
        c=bpy.data.cameras.new(N); c.lens=lens; o=bpy.data.objects.new(N,c)
        z=p[2] if p[2] is not None else gz(p[0],p[1])+eh
        tz=tg[2] if tg[2] is not None else gz(tg[0],tg[1])+1.2
        o.location=Vector((p[0],p[1],z)); d=Vector((tg[0],tg[1],tz))-o.location
        o.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); coll.objects.link(o); print('QA_CAM',N,tuple(round(v,2) for v in o.location),'tz %.2f'%tz)

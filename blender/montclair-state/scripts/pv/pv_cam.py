# pv: close-up camera on the Dickson north-wing top row (clipped slots now framed) + an eye-level camera from the north
# (ground-snapped, 1.7 m). REVERT=1 removes both.
import bpy, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
CAMS={'PV_CAM_closeup_dickson_north_toprow':((-157.0,178.0,140.5),(-169.0,159.2,147.0),35,False),
      'PV_CAM_eye_dickson_north':((-146.0,196.0,None),(-166.0,159.0,143.5),28,True)}
for N in CAMS:
    if N in bpy.data.objects:
        o=bpy.data.objects[N]; d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d); print('REVERTED_PV_CAM',N)
if not REV:
    dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
    for N,(loc,tgt,lens,snap) in CAMS.items():
        loc=Vector((loc[0],loc[1],loc[2] or 0.0))
        if snap:
            hit,p,_,_,ob,_=sc.ray_cast(dg,Vector((loc.x,loc.y,300.0)),Vector((0,0,-1)))
            loc.z=(p.z if hit else 136.0)+1.7; print('PV_CAM_GROUND',N,ob.name if hit else None,round(loc.z,2))
        d=bpy.data.cameras.new(N); d.lens=lens; o=bpy.data.objects.new(N,d); o.location=loc
        o.rotation_euler=(Vector(tgt)-loc).to_track_quat('-Z','Y').to_euler()
        bpy.data.objects['PE_CAM_eye_dickson_west'].users_collection[0].objects.link(o); print('PV_CAM',N)

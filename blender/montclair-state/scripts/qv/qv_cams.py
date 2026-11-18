# qv cameras (REVERT=1 removes QV_CAM*). UNVERIFIED viewpoints.
import bpy,os
from mathutils import Vector
for o in [o for o in bpy.data.objects if o.name.startswith('QV_CAM')]: bpy.data.objects.remove(o,do_unlink=True)
for c in [c for c in bpy.data.cameras if c.name.startswith('QV_CAM') and c.users==0]: bpy.data.cameras.remove(c)
if os.environ.get('REVERT')!='1':
    dg=bpy.context.evaluated_depsgraph_get()
    S=[bpy.data.objects[n] for n in ('Context_skirt_3DEP_ortho_4km','Terrain_LiDAR_DTM_1m')]
    def gz(x,y):
        b=None
        for o in S:
            e=o.evaluated_get(dg); iw=o.matrix_world.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),Vector((0,0,-1)))
            if r[0]:
                z=(o.matrix_world@r[1]).z; b=z if b is None or z>b else b
        return b
    col=bpy.data.collections.get('QS_Richardson_walks_UNVERIFIED')
    for nm,eye,tgt,lens,h in (('QV_CAM_eye_richardson_from_NW',(28,328),(85,272),24,1.65),('QV_CAM_oblique_richardson_from_NW',(-10,360),(85,265),30,45),('QV_CAM_closeup_richardson_NW_ground',(48,312),(66,300),28,1.5)):
        cd=bpy.data.cameras.new(nm); cd.lens=lens; c=bpy.data.objects.new(nm,cd); col.objects.link(c)
        z0=gz(*eye) or 137.5; zt=gz(*tgt) or 137.5
        c.location=(eye[0],eye[1],z0+h); d=Vector((tgt[0],tgt[1],zt+(1.5 if h<5 else 0)))-c.location
        c.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); print('QVCAM',nm,tuple(round(v,2) for v in c.location))
if os.environ.get('QVSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

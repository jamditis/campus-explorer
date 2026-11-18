# qw cameras (REVERT=1 removes QW_CAM*). UNVERIFIED viewpoints.
import bpy,os
from mathutils import Vector
for o in [o for o in bpy.data.objects if o.name.startswith('QW_CAM')]: bpy.data.objects.remove(o,do_unlink=True)
for c in [c for c in bpy.data.cameras if c.name.startswith('QW_CAM') and c.users==0]: bpy.data.cameras.remove(c)
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
    col=bpy.data.collections.get('QW_Richardson_walk_ext_UNVERIFIED')
    for nm,eye,tgt,lens,h in (('QW_CAM_closeup_walk_to_student_center',(37,297),(23,262),26,1.6),('QW_CAM_eye_north_walk_junction',(70,312),(58,345),26,1.65)):
        cd=bpy.data.cameras.new(nm); cd.lens=lens; c=bpy.data.objects.new(nm,cd); col.objects.link(c)
        z0=gz(*eye) or 137.5; zt=gz(*tgt) or 137.5
        c.location=(eye[0],eye[1],z0+h); d=Vector((tgt[0],tgt[1],zt+(1.5 if h<5 else 0)))-c.location
        c.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); print('QVCAM',nm,tuple(round(v,2) for v in c.location))
if os.environ.get('QWSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

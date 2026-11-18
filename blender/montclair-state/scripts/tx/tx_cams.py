"""tw cameras for College Hall WIPs. REVERT=1 removes tx_obj cameras."""
import bpy, os
from mathutils import Vector, Matrix, Euler
REV=os.environ.get('REVERT')=='1'
SAVE=os.environ.get('SAVE')=='1'

def revert():
    for o in [o for o in list(bpy.data.objects) if o.get('tx_obj') and o.type=='CAMERA']:
        cam=o.data; bpy.data.objects.remove(o, do_unlink=True)
        if cam and cam.users==0: bpy.data.cameras.remove(cam)
    print('TX cams REVERTED')

if REV:
    revert()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# remove prior tw cams then recreate (idempotent)
revert()

def ground_z(x,y):
    dg=bpy.context.evaluated_depsgraph_get()
    best=None
    for nm in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','SA_ground_lower_patch_UNVERIFIED'):
        o=bpy.data.objects.get(nm)
        if not o: continue
        e=o.evaluated_get(dg); iw=o.matrix_world.inverted()
        r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(o.matrix_world@r[1]).z
            if best is None or z>best: best=z
    return best if best is not None else 132.0

def add_cam(name, loc, target, lens=50):
    cam=bpy.data.cameras.new(name); cam.lens=lens; cam.clip_start=0.3; cam.clip_end=6000
    o=bpy.data.objects.new(name,cam); bpy.context.scene.collection.objects.link(o)
    o.location=Vector(loc); d=Vector(target)-o.location
    o.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); o['tx_obj']=1
    print('TX CAM',name,tuple(round(v,1) for v in loc)); return o
def eye(x,y,h=1.7): return (x,y,ground_z(x,y)+h)
add_cam('TX_CAM_oblique_Nursing_from_SW',(-150,185,200),(-83,257,148),40)
add_cam('TX_CAM_eye_Nursing_from_W',eye(-124,236),(-84,258,148),30)
add_cam('TX_CAM_eye_Nursing_from_SE',eye(-48,214),(-84,256,148),30)
add_cam('TX_CAM_closeup_Nursing_W_entrance',eye(-108,244,1.8),(-97.3,251.5,143.0),28)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

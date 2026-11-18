"""tw cameras for College Hall WIPs. REVERT=1 removes tw_obj cameras."""
import bpy, os
from mathutils import Vector, Matrix, Euler
REV=os.environ.get('REVERT')=='1'
SAVE=os.environ.get('SAVE')=='1'

def revert():
    for o in [o for o in list(bpy.data.objects) if o.get('tw_obj') and o.type=='CAMERA']:
        cam=o.data; bpy.data.objects.remove(o, do_unlink=True)
        if cam and cam.users==0: bpy.data.cameras.remove(cam)
    print('TW cams REVERTED')

if REV:
    revert()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# remove prior tw cams then recreate (idempotent)
revert()

def ground_z(x,y):
    dg=bpy.context.evaluated_depsgraph_get()
    best=None
    for nm in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','Susan A. Cole Hall walls'):
        o=bpy.data.objects.get(nm)
        if not o: continue
        e=o.evaluated_get(dg); iw=o.matrix_world.inverted()
        r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(o.matrix_world@r[1]).z
            if best is None or z>best: best=z
    return best if best is not None else 132.0

def add_cam(name, loc, target, lens=50):
    cam=bpy.data.cameras.new(name); cam.lens=lens
    o=bpy.data.objects.new(name,cam); bpy.context.scene.collection.objects.link(o)
    o.location=Vector(loc)
    # aim
    direction=Vector(target)-o.location
    o.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    o['tw_obj']=1
    return o

# central cupola ~ (-113.2,-95.5,157.96); building south front ~ (-116,-120)
gz=ground_z(-115.7,-155)
add_cam('TW_CAM_oblique_CollegeHall_from_SSW', (-40,-220,188), (-113,-95,148), lens=35)
add_cam('TW_CAM_eye_CollegeHall_from_S', (-115.7, -155.0, gz+1.65), (-116,-108,140), lens=40)
gz2=ground_z(-195,-100)
add_cam('TW_CAM_eye_CollegeHall_from_W', (-195.0, -100.0, gz2+1.65), (-150,-95,140), lens=40)
add_cam('TW_CAM_closeup_CollegeHall_cupola', (-100.0, -125.0, 152.5), (-113.2,-95.5,154.5), lens=85)
print('TW cams added', [o.name for o in bpy.data.objects if o.get('tw_obj') and o.type=='CAMERA'])
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

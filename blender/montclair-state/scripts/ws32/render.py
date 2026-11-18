import bpy, os
from datetime import datetime
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state'
if os.environ.get('FIX')=='1':
    exec(open(R+'/scripts/ws32/fix.py').read()); exec(open(R+'/scripts/ws32/fix2.py').read()); exec(open(R+'/scripts/ws32/fix3.py').read())
sc=bpy.context.scene
TAG=os.environ.get('OUT_TAG','goldenhour'); DIRV=os.environ.get('DIR','test')
ts=datetime.now().strftime('%Y%m%d-%H%M')
base=bpy.data.objects.get('Sun')
def golden():
    sc.world=bpy.data.worlds['WP2_World_GOLDEN']
    if base: base.hide_render=True
    for k in ('MORNING','GOLDEN','OVERCAST'):
        o=bpy.data.objects.get('WP2_Sun_'+k)
        if o: o.hide_render=(k!='GOLDEN')
CAMS={'WS32_CAM_oblique_CCOM_dock_from_SE':((24,-70,170),(2,-32,136),26),
 'WS32_CAM_eye_walk_over_apron_from_SW':((-4,-44,None),(5,-28,136.2),24),
 'WS32_CAM_eye_dock_apron_from_E':((16,-36,None),(-2,-28,136.4),22),
 'WS32_CAM_closeup_walk_apron_seam':((1,-36.5,None),(4,-30,135.9),26)}
golden()
dg=bpy.context.evaluated_depsgraph_get()
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for n,(loc,tgt,lens) in CAMS.items():
    if loc[2] is None:
        # terrain-only ray so the camera never lands in a tree crown
        e=ter.evaluated_get(dg); mi=ter.matrix_world.inverted()
        ok,hp,_,_=e.ray_cast(mi@Vector((loc[0],loc[1],200)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
        z=(ter.matrix_world@hp).z if ok else 136
        loc=(loc[0],loc[1],z+(1.6 if 'eye' in n else 1.3)); print('cam',n,round(loc[2],2))
    c=bpy.data.objects.get(n)
    if not c:
        cd=bpy.data.cameras.new(n); c=bpy.data.objects.new(n,cd); sc.collection.objects.link(c)
    c.location=loc; c.data.lens=lens; c.data.clip_start=0.1; c.data.clip_end=3000
    c.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
if os.environ.get('SAVE')=='1':
    sc.world=bpy.data.worlds.get('Sky') or sc.world
    if base: base.hide_render=False
    for k in ('MORNING','GOLDEN','OVERCAST'):
        o=bpy.data.objects.get('WP2_Sun_'+k)
        if o: o.hide_render=True
    bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)
    golden()
for ONLY,LABEL in [x.split('=') for x in os.environ['CAMS'].split(',') if x]:
    sc.camera=bpy.data.objects[ONLY]
    sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=int(os.environ.get('SAMP','16')); sc.cycles.use_denoising=True
    sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=int(os.environ.get('PCT','60'))
    sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=90
    sc.render.threads_mode='FIXED'; sc.render.threads=4
    fp=f'{R}/renders/{DIRV}/{ts}_{LABEL}_{TAG}.jpg'; sc.render.filepath=fp
    bpy.ops.render.render(write_still=True); print('WROTE',fp,flush=True)

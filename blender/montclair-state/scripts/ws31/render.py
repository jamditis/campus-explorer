import bpy, os
from datetime import datetime
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state'
if os.environ.get('BUILD')=='1': exec(open(R+'/scripts/ws31/dock.py').read())
if os.environ.get('FIX2')=='1': exec(open(R+'/scripts/ws31/fix2.py').read())
if os.environ.get('FIX3')=='1': exec(open(R+'/scripts/ws31/fix3.py').read())
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
CAMS={'WS31_CAM_oblique_CCOM_dock_Morehead_from_SE':((22,-78,182),(-2,-36,136),24),
 'WS31_CAM_eye_dock_drive_from_N':((-3,-62,None),(-1,-30,136.4),24),
 'WS31_CAM_eye_dock_apron_from_E':((12,-42,None),(-5,-27,136.4),22),
 'WS31_CAM_closeup_dock_drive_apron_seam':((6,-43,None),(-1,-30,135.8),24)}
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

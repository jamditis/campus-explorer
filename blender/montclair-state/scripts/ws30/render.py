import bpy, os, sys
from datetime import datetime
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state'
exec(open(R+'/scripts/ws30/fix.py').read()) if os.environ.get('BUILD')=='1' else None
sc=bpy.context.scene
TAG=os.environ.get('OUT_TAG','goldenhour'); DIRV=os.environ.get('DIR','test')
ts=datetime.now().strftime('%Y%m%d-%H%M')
sc.world=bpy.data.worlds['WP2_World_GOLDEN']
base=bpy.data.objects.get('Sun')
if base: base.hide_render=True
for k in ('MORNING','GOLDEN','OVERCAST'):
    o=bpy.data.objects.get('WP2_Sun_'+k)
    if o: o.hide_render=(k!='GOLDEN')
CAMS={'WS30_CAM_oblique_Cole_Kasser_corridor_from_S':((-95,-175,185),(-100,-60,136),28),
 'WS30_CAM_eye_KasserE_walk_from_S':((-112,-96,None),(-106,-66,137.5),26),
 'WS30_CAM_eye_Cole_walk_from_W':((-98,-45,None),(-60,-50,137.0),26),
 'WS30_CAM_closeup_KasserE_walk_joints':((-110,-88,None),(-107,-76,136.6),30),
 'WS30_CAM_closeup_dock_apron_road_edge':((-7,-40,None),(-1,-31,135.9),30),
 'WS30_CAM_eye_east_walk_e56':((50,-96,None),(55,-80,115.0),26),
 'WS30_CAM_closeup_SouthCollegeAve_walk':((-173,-199,None),(-168,-186,124.0),30)}
dg=bpy.context.evaluated_depsgraph_get()
for n,(loc,tgt,lens) in CAMS.items():
    if loc[2] is None:
        h=sc.ray_cast(dg,Vector((loc[0],loc[1],170)),Vector((0,0,-1)))
        z=(h[1].z if h[0] else 126)+ (1.6 if 'eye' in n else 1.3); loc=(loc[0],loc[1],z)
        print('cam ground',n,round(z,2))
    c=bpy.data.objects.get(n)
    if not c:
        cd=bpy.data.cameras.new(n); c=bpy.data.objects.new(n,cd); sc.collection.objects.link(c)
    c.location=loc; c.data.lens=lens; c.data.clip_start=0.1; c.data.clip_end=3000
    c.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
if os.environ.get('SAVEAS'):
    bpy.ops.wm.save_as_mainfile(filepath=os.environ['SAVEAS'],copy=True); print('SAVEDAS')
if os.environ.get('SAVE')=='1':
    sc.world=bpy.data.worlds.get('Sky') or sc.world
    if base: base.hide_render=False
    for k in ('MORNING','GOLDEN','OVERCAST'):
        o=bpy.data.objects.get('WP2_Sun_'+k)
        if o: o.hide_render=True
    bpy.ops.wm.save_mainfile(); print('SAVED')
    sc.world=bpy.data.worlds['WP2_World_GOLDEN']
    if base: base.hide_render=True
    bpy.data.objects['WP2_Sun_GOLDEN'].hide_render=False
for ONLY,LABEL in [x.split('=') for x in os.environ['CAMS'].split(',')]:
    sc.camera=bpy.data.objects[ONLY]
    sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=int(os.environ.get('SAMP','16')); sc.cycles.use_denoising=True
    sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=int(os.environ.get('PCT','60'))
    sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=90
    sc.render.threads_mode='FIXED'; sc.render.threads=4
    fp=f'{R}/renders/{DIRV}/{ts}_{LABEL}_{TAG}.jpg'; sc.render.filepath=fp
    bpy.ops.render.render(write_still=True); print('WROTE',fp,flush=True)

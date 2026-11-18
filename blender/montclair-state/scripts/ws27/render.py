import bpy, os, sys
from datetime import datetime
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state'
exec(open(R+'/scripts/ws27/road.py').read()) if os.environ.get('BUILD')=='1' else None
sc=bpy.context.scene
TAG=os.environ.get('OUT_TAG','goldenhour'); DIRV=os.environ.get('DIR','test')
ts=datetime.now().strftime('%Y%m%d-%H%M')
sc.world=bpy.data.worlds['WP2_World_GOLDEN']
base=bpy.data.objects.get('Sun')
if base: base.hide_render=True
for k in ('MORNING','GOLDEN','OVERCAST'):
    o=bpy.data.objects.get('WP2_Sun_'+k)
    if o: o.hide_render=(k!='GOLDEN')
CAMS={'WS27_CAM_oblique_CollegeAve_Kasser_from_SW':((-168,-168,158),(-214,-96,126),30),
 'WS27_CAM_eye_CollegeAve_W_toward_curve':((-246,-60.2,None),(-205,-72,126.5),28),
 'WS27_CAM_eye_CollegeAve_S_looking_N':((-213.5,-157,None),(-203,-105,126.5),28),
 'WS27_CAM_closeup_CollegeAve_curb_crosswalk':((-213.0,-133.5,None),(-208.5,-140.5,125.2),30)}
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

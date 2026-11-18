import bpy, os
from datetime import datetime
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state'
if False:
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
CAMS={'WS33_CAM_oblique_CCOM_dock_drive_from_SW':((-30,-80,165),(-3,-38,136),28),
 'WS33_CAM_eye_dock_drive_curbs_from_S':((-4.2,-64,None),(-3.8,-30,135.6),26),
 'WS33_CAM_eye_walk_over_apron_from_SW':((-4,-44,None),(5,-28,136.2),24),
 'WS33_CAM_closeup_dock_drive_east_curb':((-3.6,-49,None),(-1.6,-40,135.0),30)}
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
CULL=os.environ.get('CULL')
if CULL:
    cx0,cx1,cy0,cy1=map(float,CULL.split(',')); nh=0
    for o in sc.objects:
        if o.type in ('CAMERA','LIGHT') or o.hide_render: continue
        if o.name.startswith('Terrain_LiDAR'): continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        xs=[v.x for v in bb]; ys=[v.y for v in bb]
        if max(xs)<cx0 or min(xs)>cx1 or max(ys)<cy0 or min(ys)>cy1:
            o.hide_render=True; nh+=1
    print('CULLED',nh,flush=True)
for ONLY,LABEL in [x.split('=') for x in os.environ['CAMS'].split(',') if x]:
    sc.camera=bpy.data.objects[ONLY]
    sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=int(os.environ.get('SAMP','16')); sc.cycles.use_denoising=True
    sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=int(os.environ.get('PCT','60'))
    sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=90
    sc.render.threads_mode='FIXED'; sc.render.threads=4; sc.render.use_simplify=True; sc.render.simplify_subdivision_render=min(sc.render.simplify_subdivision_render,2); sc.cycles.texture_limit_render=os.environ.get('TEXLIM','2048'); sc.render.simplify_child_particles_render=float(os.environ.get('CHILD','1'))
    fp=f'{R}/renders/{DIRV}/{ts}_{LABEL}_{TAG}.jpg'; sc.render.filepath=fp
    bpy.ops.render.render(write_still=True); print('WROTE',fp,flush=True)

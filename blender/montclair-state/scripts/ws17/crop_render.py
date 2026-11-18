sc=bpy.context.scene
import sys; sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws5'); import cams
cams.CAMS.update({'WS10_CAM_eye_walk_from_sign_E':((-80.5,-57.6,136.5),(-50,-54,135.6),28)}); cams.ensure(sc)
sc.world=bpy.data.worlds['WP2_World_GOLDEN']
for k in ('MORNING','GOLDEN','OVERCAST'):
    s=bpy.data.objects.get('WP2_Sun_'+k)
    if s: s.hide_render=(k!='GOLDEN')
b=bpy.data.objects.get('Sun')
if b: b.hide_render=True
sc.camera=bpy.data.objects['WS10_CAM_eye_walk_from_sign_E']
sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=80
sc.render.use_border=True; sc.render.use_crop_to_border=True
sc.render.border_min_x=0.42; sc.render.border_max_x=0.86; sc.render.border_min_y=1-0.26; sc.render.border_max_y=1-0.08
sc.render.image_settings.file_format='JPEG'; sc.render.threads_mode='FIXED'; sc.render.threads=4
sc.render.filepath='/workspace/nj-scenes/montclair-state/renders/wip/20261110-0145_ws17_probe_morehead_eavetop_tile.jpg'
bpy.ops.render.render(write_still=True); print('WROTE')

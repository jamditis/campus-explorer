import bpy, os
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects; sc=bpy.context.scene
if os.environ.get('NODECAL')=='1': O['QY_walk_junction_wear_decals_UNVERIFIED'].hide_render=True
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=16; sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=100
sc.render.use_border=True; sc.render.use_crop_to_border=True
sc.render.border_min_x=0.12; sc.render.border_max_x=0.55; sc.render.border_min_y=0.40; sc.render.border_max_y=0.75
sc.render.image_settings.file_format='JPEG'; sc.render.threads_mode='FIXED'; sc.render.threads=4
sc.camera=O['WF_CAM_closeup_436_east_edge']; sc.render.filepath=f'{R}/renders/wip/test_wg_crop_{os.environ.get("TAG","x")}.jpg'
bpy.ops.render.render(write_still=True); print('DONE',flush=True)

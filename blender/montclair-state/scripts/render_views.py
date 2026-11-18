"""Render cameras. Args after --: outdir prefix res_x samples [cam names...]"""
import bpy, sys, os
a = sys.argv[sys.argv.index('--')+1:]
outdir, prefix, rx, spp = a[0], a[1], int(a[2]), int(a[3]); cams = a[4:]
sc = bpy.context.scene; sc.render.resolution_x = rx; sc.render.resolution_y = int(rx*9/16); sc.cycles.samples = spp
os.makedirs(outdir, exist_ok=True)
if os.environ.get('DNQ'): sc.cycles.denoising_quality = os.environ['DNQ']; sc.cycles.denoising_prefilter = 'FAST'
if os.environ.get('NODN'): sc.cycles.use_denoising = False
if os.environ.get('EXR'):  # two-stage (memory): noisy EXR + denoise passes here, OIDN in a separate small process (denoise_exr.py)
    sc.cycles.use_denoising = False; bpy.context.view_layer.cycles.denoising_store_passes = True
    sc.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'; sc.render.image_settings.color_depth = '16'
    vs = sc.view_settings; print('VIEWSET', vs.view_transform, vs.look, vs.exposure, vs.gamma, sc.display_settings.display_device)
if os.environ.get('NOPERSIST'): sc.render.use_persistent_data = False
if os.environ.get('CULL'):   # memory: drop trees/furniture/details that are outside the frustum AND farther than CULL m (near off-screen casters kept for shadows)
    sc.cycles.use_camera_cull = True; sc.cycles.use_distance_cull = True; sc.cycles.camera_cull_margin = 0.1; sc.cycles.distance_cull_margin = float(os.environ['CULL'])
    for cn in ('Trees_assets_LiDAR', 'Site_furniture', 'Day2_details', 'Buildings_context', 'Curbs_granite'):
        if bpy.data.collections.get(cn):
            for o in bpy.data.collections[cn].all_objects: o.cycles.use_camera_cull = True; o.cycles.use_distance_cull = True
if os.environ.get('COMPACT'):   # memory: Embree compact BVH (slower, less RAM)
    sc.cycles.debug_use_compact_bvh = True; sc.cycles.debug_use_spatial_splits = False
for m in bpy.data.materials:   # memory: daytime lamp globes glow but are not light-tree emitters (the light tree build peaked ~+220 MB)
    if m.name.startswith('Lamp_glass'): m.cycles.emission_sampling = 'NONE'
if os.environ.get('NOLT'): sc.cycles.use_light_tree = False
if os.environ.get('WMAP'): sc.world.cycles.sampling_method = 'MANUAL'; sc.world.cycles.sample_map_resolution = int(os.environ['WMAP'])
if os.environ.get('TILE'): sc.cycles.use_auto_tile = True; sc.cycles.tile_size = int(os.environ['TILE'])   # memory: smaller device tiles
if os.environ.get('TEXLIM'): sc.cycles.texture_limit_render = os.environ['TEXLIM']
if os.environ.get('THREADS'): sc.render.threads_mode = 'FIXED'; sc.render.threads = int(os.environ['THREADS'])
for n in filter(None, os.environ.get('HIDE', '').split(',')):  # diagnostics: hide collections/objects from render
    t = bpy.data.collections.get(n) or bpy.data.objects.get(n)
    if t: t.hide_render = True
for c in cams or [o.name for o in sc.objects if o.type == 'CAMERA']:
    sc.camera = bpy.data.objects[c]
    sc.render.filepath = os.path.join(outdir, f'{prefix}{c}.' + ('exr' if os.environ.get('EXR') else 'jpg'))
    bpy.ops.render.render(write_still=True); print('RENDERED', sc.render.filepath)

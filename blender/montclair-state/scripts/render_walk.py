"""Low-res walk preview (session 3g). Args after --: outdir start end step res_x spp [denoise: none|fast]
Renders CAM_walk_west frame by frame in one process (persistent data), skips frames already on disk (so it can be resumed),
prints per-frame peak RSS. Then: ffmpeg -framerate 12 -i outdir/walk_%04d.png ... (every 2nd frame of a 24 fps, 240-frame walk)."""
import bpy, sys, os, time, resource
a = sys.argv[sys.argv.index('--') + 1:]
out, f0, f1, st, rx, spp = a[0], int(a[1]), int(a[2]), int(a[3]), int(a[4]), int(a[5]); dn = a[6] if len(a) > 6 else 'fast'
sc = bpy.context.scene; sc.camera = bpy.data.objects['CAM_walk_west']
sc.render.resolution_x = rx; sc.render.resolution_y = int(rx * 9 / 16); sc.render.resolution_percentage = 100
sc.cycles.samples = spp; sc.cycles.use_adaptive_sampling = True; sc.render.use_persistent_data = os.environ.get('PERSIST', '1') == '1'
sc.cycles.use_denoising = dn != 'none'
if dn == 'fast': sc.cycles.denoiser = 'OPENIMAGEDENOISE'; sc.cycles.denoising_prefilter = 'FAST'; sc.cycles.denoising_quality = 'FAST'
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'
for m in bpy.data.materials:
    if m.name.startswith('Lamp_glass'): m.cycles.emission_sampling = 'NONE'
for n in filter(None, os.environ.get('HIDE', '').split(',')):
    t = bpy.data.collections.get(n) or bpy.data.objects.get(n)
    if t: t.hide_render = True
os.makedirs(out, exist_ok=True)
for fr in range(f0, f1 + 1, st):
    fp = os.path.join(out, f'walk_{fr:04d}.png')
    if os.path.exists(fp): continue
    sc.frame_set(fr); sc.render.filepath = fp; t0 = time.time()
    bpy.ops.render.render(write_still=True)
    print('FRAME', fr, 'sec', round(time.time() - t0, 1), 'peakRSS_MB', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024, flush=True)

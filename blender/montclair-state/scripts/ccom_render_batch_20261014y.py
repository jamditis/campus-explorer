"""Prep + render CCOM WIP cams with memory caps.
Args after --: mode(exterior|interior) outdir prefix res_x samples cam [cam...]
Env: EXR COMPACT CULL TILE TEXLIM NOLT NOPERSIST WMAP THREADS HIDE
     TREE_HIDE_M TREE_HIDE_SEG_M EXPOSURE (default 0 exterior / set for interior)
"""
import bpy, sys, os, resource
from mathutils import Vector
argv = sys.argv[sys.argv.index('--')+1:]
mode, outdir, prefix, rx, spp = argv[0], argv[1], argv[2], int(argv[3]), int(argv[4])
cams_spec = argv[5:]
cams = [c.split(":")[0] for c in cams_spec]
res = {c.split(":")[0]: c.split(":")[1] for c in cams_spec if ":" in c}
print('BATCH', mode, outdir, prefix, rx, spp, cams, flush=True)

def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

sc = bpy.context.scene
vs = sc.view_settings
vs.view_transform = 'AgX'
vs.look = 'AgX - Medium High Contrast'
vs.exposure = float(os.environ.get('EXPOSURE', '0.0'))

# visibility prep
for o in bpy.data.objects:
    if o.name.startswith('CCOM_east_clear_'):
        o.hide_render = (mode == 'exterior')
hide_room = (mode == 'interior')
for nm in ('CCOM_Win_Wing_A_wall','CCOM_Win_Wing_A_back','CCOM_Win_Wing_A_blind',
           'CCOM_Win_Wing_A_floor','CCOM_Win_Wing_A_ceil','CCOM_Win_Wing_A_light'):
    o = bpy.data.objects.get(nm)
    if o:
        o.hide_render = hide_room
print('PREP', mode, 'room_hidden', hide_room, 'exposure', vs.exposure, flush=True)

# ---- Memory knobs (defaults applied when env unset: we FORCE safe defaults for CCOM WIP)
sc.render.use_persistent_data = False  # was True in blend; caused RSS climb across cams
sc.cycles.debug_use_compact_bvh = True
sc.cycles.debug_use_spatial_splits = False
sc.cycles.use_auto_tile = True
sc.cycles.tile_size = int(os.environ.get('TILE', '512'))
# texture limit: 1024 for WIP
tex = os.environ.get('TEXLIM', '1024')
# Blender enum: 'OFF','128','256','512','1024','2048','4096','8192'
try:
    sc.cycles.texture_limit_render = tex
except Exception:
    pass
sc.cycles.use_light_tree = os.environ.get('NOLT', '1') != '1'  # default OFF for mem
if os.environ.get('WMAP', '512'):
    sc.world.cycles.sampling_method = 'MANUAL'
    sc.world.cycles.sample_map_resolution = int(os.environ.get('WMAP', '512'))
sc.render.threads_mode = 'FIXED'
sc.render.threads = int(os.environ.get('THREADS', '2'))

# camera + distance cull
cull = float(os.environ.get('CULL', '60'))
sc.cycles.use_camera_cull = True
sc.cycles.use_distance_cull = True
sc.cycles.camera_cull_margin = 0.1
sc.cycles.distance_cull_margin = cull
for cn in ('Trees_assets_LiDAR', 'Site_furniture', 'Day2_details', 'Buildings_context',
           'Curbs_granite', 'grass_tiles_3g', 'Lawn_grass_leaves_3f', 'Morehead_windows_modelled',
           'Facades_3i'):
    col = bpy.data.collections.get(cn)
    if col:
        for o in col.all_objects:
            o.cycles.use_camera_cull = True
            o.cycles.use_distance_cull = True

# Hide off-camera / low-value collections for CCOM east WIP (render-only)
hide_cols = [x for x in os.environ.get('HIDE', 'grass_tiles_3g,Lawn_grass_leaves_3f,Morehead_windows_modelled,Site_furniture').split(',') if x]
# For exterior close/eye also hide interior shell lights? Keep them — they don't show outside much.
# For interior: hide west-front Day2 details less critical
if mode == 'interior':
    hide_cols += ['Day2_details']
for n in hide_cols:
    t = bpy.data.collections.get(n) or bpy.data.objects.get(n)
    if t:
        t.hide_render = True
        print('HIDE', n, flush=True)

for m in bpy.data.materials:
    if m.name.startswith('Lamp_glass'):
        m.cycles.emission_sampling = 'NONE'

# TREE_HIDE_M: render-only hide T_* / NT* trees near cam or along sightline (do NOT save)
r = float(os.environ.get('TREE_HIDE_M', '0'))
seg_m = float(os.environ.get('TREE_HIDE_SEG_M', '0'))
k = 0
if (r > 0 or seg_m > 0) and cams:
    # use first cam for hide (all cams in a batch share mode)
    cam0 = bpy.data.objects[cams[0]]
    cxy = cam0.location.xy
    fwd = (cam0.matrix_world.to_quaternion() @ Vector((0, 0, -1))).xy
    look = cxy + fwd.normalized() * 80.0 if fwd.length > 1e-6 else cxy
    ab = look - cxy
    L2 = ab.length_squared or 1e-9
    for ob in bpy.data.objects:
        if not (ob.name.startswith('T_') or ob.name.startswith('NT') or ob.name.startswith('NTx_')):
            continue
        pxy = ob.location.xy
        hide = False
        if r > 0 and (pxy - cxy).length < r:
            hide = True
        if seg_m > 0:
            t = max(0.0, min(1.0, (pxy - cxy).dot(ab) / L2))
            if (pxy - (cxy + ab * t)).length < seg_m:
                hide = True
        if hide:
            ob.hide_render = True
            k += 1
print('TREE_HIDE', 'r', r, 'seg', seg_m, 'hid', k, flush=True)

sc.render.resolution_x = rx
sc.render.resolution_y = int(rx * 9 / 16)
sc.cycles.samples = spp
os.makedirs(outdir, exist_ok=True)
if os.environ.get('EXR'):
    sc.cycles.use_denoising = False
    bpy.context.view_layer.cycles.denoising_store_passes = True
    sc.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
    sc.render.image_settings.color_depth = '16'
    print('VIEWSET', vs.view_transform, vs.look, vs.exposure, 'tile', sc.cycles.tile_size,
          'texlim', sc.cycles.texture_limit_render, 'persist', sc.render.use_persistent_data,
          'compact', sc.cycles.debug_use_compact_bvh, 'lt', sc.cycles.use_light_tree, flush=True)

ext = 'exr' if os.environ.get('EXR') else 'jpg'
peaks = []
for c in cams:
    sc.camera = bpy.data.objects[c]
    if c in res:
        sc.render.resolution_x, sc.render.resolution_y = map(int, res[c].split("x"))
    else:
        sc.render.resolution_x, sc.render.resolution_y = rx, int(rx*9/16)
    sc.render.resolution_percentage = 100
    sc.render.filepath = os.path.join(outdir, f'{prefix}{c}.{ext}')
    print('RENDER start', c, 'rss', f'{rss():.0f}', flush=True)
    bpy.ops.render.render(write_still=True)
    peak = rss()
    peaks.append(peak)
    print('RENDERED', sc.render.filepath, 'rss', f'{peak:.0f}', flush=True)
print('BATCH DONE peakrss', f'{max(peaks) if peaks else rss():.0f}', 'peaks', [round(p) for p in peaks], flush=True)
# NEVER save — tree hides / collection hides stay render-only

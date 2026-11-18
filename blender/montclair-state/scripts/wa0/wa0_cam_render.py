"""wz: render WIP cameras. By default re-renders the existing four WY cameras
WITHOUT moving them (for A/B against 20261108-1351_*_wy.jpg). Set ADD_WZ=1 to
also create four new WZ_CAM_* views after the crack has been assessed.
"""
import bpy, os, json
from mathutils import Vector
from datetime import datetime

R = '/workspace/nj-scenes/montclair-state'
os.chdir(R)
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()
SAVE = os.environ.get('SAVE') == '1'
ADD_WZ = True

WY = [
    'WY_CAM_oblique_reid_hole_from_NE',
    'WY_CAM_eye_reid_hole_from_S',
    'WY_CAM_eye_reid_hole_from_N',
    'WY_CAM_closeup_reid_hole_seam',
]

GROUND = ('Context_skirt', 'Terrain_LiDAR', 'RZ2_', 'QW_DTM', 'WF_east',
          'WT_rich', 'WU_richardson', 'WV_stone', 'WN_south', 'WO_gully')

def gz(x, y):
    o = Vector((x, y, 300.0))
    for _ in range(30):
        h, loc, nrm, idx, ob, mat = sc.ray_cast(dg, o, Vector((0, 0, -1)))
        if not h:
            return None
        if ob.name.startswith(GROUND):
            return loc.z
        o = loc - Vector((0, 0, 0.01))
    return None

def first(o, d, dist=1e4):
    h, loc, nrm, idx, ob, mat = sc.ray_cast(dg, o, d, distance=dist)
    return ((loc - o).length, ob.name) if h else (None, None)

def z_of(x, y, s):
    g = gz(x, y)
    if g is None:
        g = 137.6
    return g + float(s)

# optional new WZ cameras (only when ADD_WZ=1)
SPEC = {
    'WA0_CAM_oblique_richardson_E_corner_from_SE': [
        [[130, 266, '+24'], [113, 280, '+0'], 30],
        [[132, 262, '+28'], [113, 280, '+0'], 30],
    ],
    'WA0_CAM_eye_richardson_E_corner_from_NE': [
        [[122, 288, '+1.7'], [113.5, 280.6, '+0.6'], 30],
        [[121, 290, '+1.7'], [113.5, 280.6, '+0.6'], 30],
        [[124, 286, '+1.7'], [113.5, 280.6, '+0.6'], 30],
    ],
    'WA0_CAM_eye_qw_tuck_from_SE': [
        [[129, 271, '+1.7'], [119, 278, '+0.3'], 30],
        [[130, 273, '+1.7'], [119, 278, '+0.3'], 30],
        [[128, 270, '+1.8'], [118, 278, '+0.3'], 30],
    ],
    'WA0_CAM_closeup_richardson_E_corner_wall_foot': [
        [[116.5, 278.8, '+1.4'], [113.2, 281.0, '+0.1'], 35],
        [[117.0, 278.5, '+1.5'], [113.2, 281.0, '+0.1'], 35],
        [[116.0, 279.5, '+1.4'], [113.0, 281.2, '+0.1'], 35],
    ],
}

chk = {}
if ADD_WZ:
    col = bpy.data.collections.get('WU_richardson_reid_LiDAR_UNVERIFIED')
    if col is None:
        col = bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'].users_collection[0]
    for name, cands in SPEC.items():
        chosen = None
        tried = []
        for (p, t, lens) in cands:
            P = Vector((p[0], p[1], z_of(p[0], p[1], p[2])))
            T = Vector((t[0], t[1], z_of(t[0], t[1], t[2])))
            d = (T - P)
            dist = d.length
            d.normalize()
            fh, fo = first(P, d)
            dirs = [Vector(v) for v in ((1, 0, 0), (-1, 0, 0), (0, 1, 0),
                                        (0, -1, 0), (0, 0, 1), (0, 0, -1))]
            near = [first(P, v, 2.0)[0] for v in dirs]
            inside = sum(1 for n in near if n is not None and n < 0.4)
            up = first(P, Vector((0, 0, 1)), 25.0) if ('eye' in name or 'close' in name) else (None, None)
            ok = (fh is None or fh > 0.8 * dist) and inside == 0 and up[0] is None
            tried.append({'P': [round(c, 2) for c in P], 'T': [round(c, 2) for c in T],
                          'first_hit': [round(fh, 2) if fh else None, fo],
                          'dist': round(dist, 1), 'inside_dirs': inside, 'up': up, 'ok': ok})
            if ok:
                chosen = (P, T, lens)
                break
        if chosen is None:
            chosen = (Vector(tried[0]['P']), Vector(tried[0]['T']), cands[0][2])
            tried.append('NONE_OK_used_first')
        P, T, lens = chosen
        cam = bpy.data.objects.get(name)
        if not cam:
            cd = bpy.data.cameras.new(name)
            cam = bpy.data.objects.new(name, cd)
            col.objects.link(cam)
        cam['wa0_obj'] = 1
        cam.location = P
        cam.data.lens = lens
        cam.data.clip_start = 0.1
        cam.data.clip_end = 5000
        cam.rotation_euler = (T - P).to_track_quat('-Z', 'Y').to_euler()
        chk[name] = tried
    json.dump(chk, open(f'{R}/data/wa0/cam_check.json', 'w'), indent=1, default=str)
    for k, v in chk.items():
        print('CAM', k, json.dumps(v, default=str)[:700], flush=True)
    if SAVE:
        bpy.ops.wm.save_mainfile(compress=True)
        print('SAVED cams', flush=True)

ONLY = [c for c in os.environ.get('ONLY', '').split(',') if c]
if not ONLY:
    ONLY = list(SPEC.keys())

# verify WY cams still exist and are not moved
for name in ONLY:
    if name not in bpy.data.objects:
        raise SystemExit(f'missing camera {name}')
    print('WILL_RENDER', name,
          [round(c, 3) for c in bpy.data.objects[name].location], flush=True)

if os.environ.get('NORENDER'):
    raise SystemExit(0)

ts = datetime.now().strftime('%Y%m%d-%H%M')
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 24
sc.cycles.use_denoising = True
sc.render.resolution_x = 1280
sc.render.resolution_y = 720
sc.render.resolution_percentage = 80
sc.render.image_settings.file_format = 'JPEG'
sc.render.image_settings.quality = 90
sc.render.threads_mode = 'FIXED'
sc.render.threads = 4
paths = []
for name in ONLY:
    sc.camera = bpy.data.objects[name]
    fp = f'{R}/renders/wip/{ts}_{name}_wa0.jpg'
    sc.render.filepath = fp
    bpy.ops.render.render(write_still=True)
    print('DONE', name, fp, datetime.now().strftime('%H:%M:%S'), flush=True)
    paths.append(fp)
print('PATHS', paths, flush=True)
print('EXIT', flush=True)

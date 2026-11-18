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
ADD_WZ = os.environ.get('ADD_WZ') == '1'

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
    'WZ_CAM_oblique_reid_seam_from_SE': [
        [[105, 300, '+35'], [89, 320, '+0'], 32],
        [[110, 295, '+40'], [89, 320, '+0'], 32],
        [[100, 305, '+32'], [90, 321, '+0'], 32],
    ],
    'WZ_CAM_eye_reid_seam_from_SW': [
        [[78, 308, '+1.7'], [89, 321, '+0.15'], 30],
        [[75, 310, '+1.7'], [88, 320, '+0.15'], 30],
        [[80, 305, '+1.8'], [90, 322, '+0.2'], 30],
    ],
    'WZ_CAM_eye_reid_seam_from_SE': [
        [[100, 308, '+1.7'], [89, 321, '+0.15'], 30],
        [[104, 310, '+1.7'], [90, 320, '+0.15'], 30],
        [[98, 305, '+1.8'], [88, 322, '+0.2'], 30],
    ],
    'WZ_CAM_closeup_reid_seam_flap': [
        [[86, 315, '+1.8'], [89, 319.2, '+0.1'], 35],
        [[88, 314, '+2.0'], [90, 319.5, '+0.1'], 35],
        [[84, 316, '+1.9'], [88, 319.0, '+0.12'], 35],
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
        cam['wz_obj'] = 1
        cam.location = P
        cam.data.lens = lens
        cam.data.clip_start = 0.1
        cam.data.clip_end = 5000
        cam.rotation_euler = (T - P).to_track_quat('-Z', 'Y').to_euler()
        chk[name] = tried
    json.dump(chk, open(f'{R}/data/wz/cam_check.json', 'w'), indent=1, default=str)
    for k, v in chk.items():
        print('CAM', k, json.dumps(v, default=str)[:700], flush=True)
    if SAVE:
        bpy.ops.wm.save_mainfile(compress=True)
        print('SAVED cams', flush=True)

ONLY = [c for c in os.environ.get('ONLY', '').split(',') if c]
if not ONLY:
    ONLY = WY + (list(SPEC.keys()) if ADD_WZ else [])

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
    fp = f'{R}/renders/wip/{ts}_{name}_wz.jpg'
    sc.render.filepath = fp
    bpy.ops.render.render(write_still=True)
    print('DONE', name, fp, datetime.now().strftime('%H:%M:%S'), flush=True)
    paths.append(fp)
print('PATHS', paths, flush=True)
print('EXIT', flush=True)

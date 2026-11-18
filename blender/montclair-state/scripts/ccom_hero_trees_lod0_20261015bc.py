"""2026-10-16 bc (tag 20261015bc): limited LOD0 hero-tree swap near the CCOM eye-level cam.

Main blend only. Picks up to CAP asset trees (T_*) that are (a) visible in
CAM_eye_CCOM_grade_lab's frustum, (b) NOT hidden by that cam's render-time hide rule
(TREE_HIDE_M=40 radius / TREE_HIDE_SEG_M=12 sightline, same maths as
ccom_render_batch_20261015ax.py), (c) nearest the cam. Swaps their mesh LOD1 -> LOD0 of
the SAME species (linked from assets/campus_assets.blend), then uniformly rescales so
the world crown top stays at the pre-swap height (LiDAR top) with the base and xy
unchanged. Lean/yaw/autumn untouched. Stores obj['bc_lod1_mesh'] for revert.
Idempotent (skips objects already flagged bc_hero_lod0). Args: [--save] [--revert]
Only campus_assets species (WhitePine/HoneyLocust/Sweetgum/NorwaySpruce/TulipPoplar);
the v2Oct foursome has no LOD0 twin and is skipped. LOD0 detail level is an artistic choice — UNVERIFIED; tree xy/top stay LiDAR.
"""
import bpy, sys
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SAVE = '--save' in argv; REVERT = '--revert' in argv
CAP = 6; CAM = 'CAM_eye_CCOM_grade_lab'; HIDE_R = 40.0; HIDE_SEG = 12.0; MAXD = 140.0
ASSET = '/workspace/nj-scenes/assets/campus_assets.blend'
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()

def world_top(o):
    return max((o.matrix_world @ Vector(c)).z for c in o.bound_box)
def world_bot(o):
    return min((o.matrix_world @ Vector(c)).z for c in o.bound_box)

if REVERT:
    for o in bpy.data.objects:
        if o.get('bc_hero_lod0'):
            me = bpy.data.meshes.get(o['bc_lod1_mesh']); s = o['bc_pre_scale']
            o.data = me; o.scale = s
            if 'bc_pre_locz' in o: o.location.z = o['bc_pre_locz']
            del o['bc_hero_lod0']; print('REVERT', o.name)
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
cam = bpy.data.objects[CAM]
cxy = cam.location.xy
fwd = (cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))).xy
look = cxy + fwd.normalized() * 80.0; ab = look - cxy; L2 = ab.length_squared
cands = []
for o in bpy.data.objects:
    if not o.name.startswith('T_') or o.type != 'MESH' or not o.data or 'LOD1' not in o.data.name:
        continue
    if o.hide_render or o.get('bc_hero_lod0'):
        continue
    # only species whose LOD1 lives in campus_assets.blend (same leaf/bark mats as its LOD0);
    # the four *_LOD1_v2Oct meshes come from campus_trees_v2.blend which has no LOD0 twin
    if not (o.data.library and 'campus_assets.blend' in o.data.library.filepath):
        continue
    pxy = o.location.xy; d = (pxy - cxy).length
    if d < HIDE_R or d > MAXD: continue
    t = max(0.0, min(1.0, (pxy - cxy).dot(ab) / L2))
    if (pxy - (cxy + ab * t)).length < HIDE_SEG: continue
    top = world_top(o); mid = Vector((o.location.x, o.location.y, (o.location.z + top) / 2))
    v = world_to_camera_view(sc, cam, mid)
    if not (0.02 < v.x < 0.98 and 0.02 < v.y < 0.98 and v.z > 0): continue
    cands.append((d, o))
cands.sort(key=lambda x: x[0])
pick = [o for d, o in cands[:CAP]]
print('CANDIDATES', len(cands), 'PICK', [(o.name, o.data.name, round(d, 1)) for d, o in cands[:CAP]])
need = sorted({o.data.name.replace('LOD1', 'LOD0') for o in pick})
missing = [n for n in need if n not in bpy.data.meshes]
if missing:
    with bpy.data.libraries.load(ASSET, link=True) as (df, dt):
        dt.meshes = [n for n in missing if n in df.meshes]
print('LINKED_LOD0', missing)
for o in pick:
    # LOD1 meshes may not start at z=0 (ax White Pine LOD1 starts at +3.53 and was dropped
    # in az), so keep the WORLD trunk base and WORLD crown top, not the object origin.
    bot0 = world_bot(o); top0 = world_top(o); h0 = top0 - bot0
    lod1 = o.data.name; lod0 = bpy.data.meshes[lod1.replace('LOD1', 'LOD0')]
    o['bc_lod1_mesh'] = lod1; o['bc_pre_scale'] = list(o.scale); o['bc_pre_locz'] = o.location.z
    o.data = lod0
    bpy.context.view_layer.update()
    h1 = world_top(o) - world_bot(o); k = h0 / h1 if h1 > 1e-3 else 1.0
    o.scale = [s * k for s in o.scale]
    bpy.context.view_layer.update()
    o.location.z += bot0 - world_bot(o)
    bpy.context.view_layer.update()
    o['bc_hero_lod0'] = 1
    print('SWAP', o.name, lod1, '->', lod0.name, 'base', round(bot0, 2), '->', round(world_bot(o), 2),
          'top', round(top0, 2), '->', round(world_top(o), 2), 'xy', tuple(round(c, 2) for c in o.location.xy), 'k', round(k, 3))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED', bpy.data.filepath)

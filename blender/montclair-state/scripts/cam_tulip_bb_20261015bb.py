"""2026-10-15 bb: close-up cam aimed at a visible Tulip Poplar near CCOM (main).
Same pattern as cam_species_az_20261015az.py. Args after --: [--save] [lensx=1.5]
"""
import bpy, sys, math
from mathutils import Vector
SAVE = '--save' in sys.argv
A = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SRCS = [a for a in A if a.startswith('CAM_')] or ['CAM_oblique_CCOM_east_jf', 'CAM_eye_CCOM_grade_lab']
LENSX = float(next((a.split('=')[1] for a in A if a.startswith('lensx=')), '1.6'))
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
cands = []
for sn in SRCS:
    src = bpy.data.objects.get(sn)
    if not src:
        continue
    P = src.matrix_world.translation.copy()
    fwd = (src.matrix_world.to_quaternion() @ Vector((0, 0, -1))).normalized()
    for o in bpy.data.objects:
        if o.get('ax_species') != 'TulipPoplar' or not o.get('bb_tulip'):
            continue
        c = o.location + Vector((0, 0, o.dimensions.z * 0.55))
        d = c - P
        if d.length > 280 or d.normalized().dot(fwd) < 0.25:
            continue
        hit, loc, nor, idx, ob, _ = sc.ray_cast(dg, P, d.normalized(), distance=d.length + 5)
        score = d.length
        if hit and ob.original == o:
            score -= 30  # prefer unobstructed
        cands.append((score, o, c, src, P, bool(hit and ob.original == o)))
cands.sort(key=lambda x: x[0])
print('CANDS', [(round(l), o.name, 'hit' if hit else 'miss', sr.name) for l, o, c, sr, P, hit in cands[:12]])
if cands:
    l, o, c, src, P, hit = cands[0]
    nm = 'CAM_closeup_trees_tulip_bb'
    cd = bpy.data.cameras.get(nm) or bpy.data.cameras.new(nm)
    cd.lens = src.data.lens * LENSX
    cd.clip_end = 30000
    co = bpy.data.objects.get(nm) or bpy.data.objects.new(nm, cd)
    if co.name not in sc.collection.objects:
        sc.collection.objects.link(co)
    co.location = P
    co.rotation_euler = (c - P).to_track_quat('-Z', 'Y').to_euler()
    co['bb_target'] = o.name
    co['bb_src_cam'] = src.name
    print('CAM', nm, o.name, round(l, 1), 'lens', round(cd.lens, 1), 'hit', hit)
else:
    print('NO_TULIP_CAND — leave CAM_closeup_trees_species_az as fallback')
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')

"""2026-10-15 ~9:43 AM ET (tag 20261015an). CCOM east lounge: the 6-column curtain-wall mullions from ccom_lounge_mullions_20261015al.py
are 0.073 m wide but ~0.36 m deep, so at the photo-cam angle they read as thick maroon fins. Joe's/CCOM's photo refs/ccom_x/02 shows slim,
shallow mullions. Reduce depth to DEPTH (0.16 m, UNVERIFIED typical curtain-wall mullion) keeping the face nearest the lounge glass,
so nothing detaches from the glass. Same for the am short/tall/short transom rows (depth capped at DEPTH).
Run: ../tools/blender_slot.sh -b montclair_state.blend --python scripts/ccom_lounge_mullion_depth_20261015an.py -- --save"""
import bpy, sys
from mathutils import Vector
DEPTH = 0.16
ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
col = bpy.data.collections['CCOM_lounge_photo_20261015al']
targets = [o for o in col.all_objects if o.type == 'MESH' and (o.name.startswith('CCOM_lounge_mull6_') or o.name.startswith('CCOM_lounge_row2_'))]
glass = [o for c_ in ('CCOM_east_glazing_20261014jf', 'CCOM_lounge_east_20261014jf', 'CCOM_lounge_photo_20261015al') if c_ in bpy.data.collections
         for o in bpy.data.collections[c_].all_objects if o.type == 'MESH' and not o.hide_render and
         ('glass' in o.name.lower() or any(m and 'glass' in m.name.lower() for m in o.data.materials))]
GV = [o.matrix_world @ v.co for o in glass for v in o.data.vertices]
print('targets', len(targets), 'glass objs', [g.name for g in glass], flush=True)
if not GV: raise SystemExit('no lounge glass found; abort (no change)')
for o in targets:
    mw = o.matrix_world; inv = mw.inverted()
    W = [mw @ v.co for v in o.data.vertices]
    # horizontal edge directions of the box
    best = None
    for e in o.data.edges:   # real box edges only (vertex pairs would pick the face diagonal)
        a, b = W[e.vertices[0]], W[e.vertices[1]]
        d = b - a
        if abs(d.z) < 1e-4 and d.length > 1e-3:
            if best is None or d.length > best.length: best = d
    if o.name.startswith('CCOM_lounge_row2_'):
        # rows: long horizontal = along wall; depth = perpendicular horizontal
        t = best.normalized(); n = Vector((-t.y, t.x, 0))
    else:
        n = best.normalized()
    s = [w.dot(n) for w in W]; s0, s1 = min(s), max(s)
    if s1 - s0 <= DEPTH + 1e-3:
        print('skip', o.name, 'depth', round(s1 - s0, 3)); continue
    c = sum(W, Vector()) / len(W)
    near = [g for g in GV if (g - c).xy.length < 4.0]
    gs = sum(g.dot(n) for g in near) / len(near) if near else s0
    keep_lo = abs(gs - s0) <= abs(gs - s1)
    for v, w in zip(o.data.vertices, W):
        sv = w.dot(n)
        if keep_lo and sv > s0 + DEPTH: w2 = w - n * (sv - (s0 + DEPTH))
        elif not keep_lo and sv < s1 - DEPTH: w2 = w + n * ((s1 - DEPTH) - sv)
        else: continue
        v.co = inv @ w2
    o.data.update(); o['depth_20261015an'] = 'depth %.3f -> %.2f (photo refs/ccom_x/02 slim mullions; UNVERIFIED)' % (s1 - s0, DEPTH)
    print(o.name, 'depth', round(s1 - s0, 3), '->', DEPTH, 'keep', 'lo' if keep_lo else 'hi', 'glass pts', len(near), flush=True)
if '--save' in ARGV:
    bpy.ops.wm.save_mainfile(); print('SAVED', bpy.data.filepath, flush=True)

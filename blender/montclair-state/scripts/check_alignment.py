"""Alignment check for CCOM signs / lettering / windows (Joe, 2026-10-14). Read-only; prints a report and writes data/alignment_ccom.json.
blender -b montclair_state.blend --python scripts/check_alignment.py [-- --tol 0.05]
Offsets are in metres along the face (u) or height (z). PASS if |offset| <= tol (default 0.05 m) unless an intended offset is listed."""
import bpy, json, os, sys, statistics as st
from mathutils import Vector
ROOT = os.path.dirname(bpy.data.filepath); a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
TOL = float(a[a.index('--tol') + 1]) if '--tol' in a else 0.05
TW = {}; exec(open(os.path.join(ROOT, 'scripts', 'ccom_tower.py')).read().split('col = None')[0], TW)
A, T, NO, W, G = TW['A'], TW['T'], TW['NO'], TW['W'], TW['G']
def uw(p): q = Vector((p.x, p.y)) - A; return q.dot(T), q.dot(NO)
def bbox_world(o):
    dg = bpy.context.evaluated_depsgraph_get(); oe = o.evaluated_get(dg)
    return [o.matrix_world @ Vector(c) for c in oe.bound_box]
R = {'tolerance_m': TOL, 'items': []}
def item(name, offset, ref, intended=0.0, note=''):
    ok = abs(offset - intended) <= TOL
    R['items'].append(dict(name=name, offset_m=round(offset, 3), reference=ref, intended_m=intended, result='PASS' if ok else 'FAIL', note=note))
# --- tower west face
face_c = W / 2
win = bpy.data.objects.get('CCOM tower 4a tall arched window glass')
if win:
    us = [uw(p)[0] for p in bbox_world(win)]; wc = (min(us) + max(us)) / 2
    item('Tower arched window centre vs tower face centre', wc - face_c, 'face centre u=%.2f' % face_c, intended=0.6, note='photo (2021): window sits ~0.6 m north of centre (UNVERIFIED)')
for o in [o for o in bpy.data.objects if o.name.startswith('CCOM tower 4a lettering')]:
    us = [uw(p)[0] for p in bbox_world(o)]; lc = (min(us) + max(us)) / 2
    item(f'{o.name[24:]} lettering centre vs tower face centre', lc - face_c, 'face centre', note=f'width {max(us)-min(us):.2f} m')
    if win: item(f'{o.name[24:]} lettering centre vs arched window centre', lc - wc, 'window centre', intended=face_c - wc, note='photo: lettering is face-centred, window offset north; lettering spans the window')
bel = bpy.data.objects.get('CCOM tower 4a belfry openings (UNVERIFIED N/E)')
if bel:
    vs = [bel.matrix_world @ v.co for v in bel.data.vertices]; wv = [p for p in vs if abs(uw(p)[1]) < 0.05]
    if wv: us = [uw(p)[0] for p in wv]; item('Belfry pair (west face) centre vs face centre', (min(us) + max(us)) / 2 - face_c, 'face centre')
# --- entrance
pa, pb = bpy.data.objects.get('CCOM entrance pier +1'), bpy.data.objects.get('CCOM entrance pier -1'); gl = bpy.data.objects.get('CCOM atrium glass (arched, 7x10 grid)')
if pa and pb and gl:
    cen = lambda o: sum(bbox_world(o), Vector()) / 8
    mid = (cen(pa) + cen(pb)) / 2; axis = (cen(pa) - cen(pb)).normalized()
    item('Entrance glass centre vs pier pair centre', (cen(gl) - mid).dot(axis), 'pier midpoint')
# --- wing windows (modelled instances)
E = [o for o in bpy.data.objects if o.name.startswith('CCOM_win_') and o.instance_type == 'COLLECTION']
wo = bpy.data.objects['School of Communication and Media walls']; pw, fh, wb = float(wo['win_pitch']), float(wo['floor_h']), float(wo['win_bottom']); u0 = float(wo.get('win_u0', 0))
runs = {}
for e in E:
    bu = e['bay_u']; off = ((bu - u0) / pw - 0.5) % 1.0; off = (off if off < 0.5 else off - 1.0) * pw
    item(f'{e.name} centre vs bay centre', off, f'bay grid pitch {pw} m') if abs(off) > TOL else None
    nx = e.get('run') or (round(e.matrix_world[0][1], 2), round(e.matrix_world[1][1], 2)); runs.setdefault(nx, []).append(e)
spacing = []; rows = []
for k, es in runs.items():
    for r in sorted({e['row'] for e in es}):
        rs = sorted([e for e in es if e['row'] == r], key=lambda e: e['bay_u']); zs = [e.matrix_world[2][3] for e in rs]
        d = [rs[i + 1]['bay_u'] - rs[i]['bay_u'] for i in range(len(rs) - 1)]
        dev = [abs(x - pw * round(x / pw)) for x in d]
        spacing.append(dict(face_normal=k, row=r, count=len(rs), max_spacing_dev_m=round(max(dev), 4) if dev else 0.0, gaps_in_bays=[round(x / pw) for x in d if round(x / pw) > 1]))
        rows.append(dict(face_normal=k, row=r, sill_z_spread_m=round(max(zs) - min(zs), 3)))
        item(f'Wing windows run {k} row {r}: max spacing deviation from {pw} m bays', max(dev) if dev else 0.0, 'bay pitch')
        item(f'Wing windows run {k} row {r}: sill level spread (level floor line)', max(zs) - min(zs), 'one floor datum per run')
R['wing_runs'] = spacing; R['wing_rows_sill_spread'] = rows; R['wing_windows'] = len(E)
sag = [e.get('sill_above_ground') for e in E if e.get('row') == 0 and e.get('sill_above_ground') is not None]
if sag: R['ground_floor_sill_above_local_ground_m'] = [round(min(sag), 2), round(max(sag), 2)]; print('  INFO ground-floor sills above local ground: %.2f..%.2f m' % (min(sag), max(sag)))
# --- free-standing signs
sp, pn = bpy.data.objects.get('Campus sign posts (UNVERIFIED position)'), bpy.data.objects.get('Campus building ID sign panel (UNVERIFIED)')
if sp and pn:
    vs = [sp.matrix_world @ v.co for v in sp.data.vertices]; pv = [pn.matrix_world @ v.co for v in pn.data.vertices]
    pc = sum(pv, Vector()) / len(pv); sc = sum(vs, Vector()) / len(vs)
    ax = (max(pv, key=lambda p: (p - pc).length) - pc); ax.z = 0; ax = ax.normalized()
    item('Building ID sign panel centre vs its posts centre (along panel)', (pc - sc).dot(ax), 'post midpoint', note='position itself UNVERIFIED (flagged for Joe)')
fails = [i for i in R['items'] if i['result'] == 'FAIL']
print('ALIGNMENT CCOM: items', len(R['items']), 'fail', len(fails), 'tol', TOL)
for i in R['items']: print(f"  {i['result']:4s} {i['name']}: {i.get('offset_m','')} (intended {i.get('intended_m','')}) {i.get('note','')}")
for s_ in spacing: print('  RUN', s_)
os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True); json.dump(R, open(os.path.join(ROOT, 'data', 'alignment_ccom.json'), 'w'), indent=1)

# --- Morehead Hall modelled windows (Joe, 2026-10-14 Morehead real-windows session)
RM = {'tolerance_m': TOL, 'items': [], 'building': 'Morehead Hall'}
def mitem(name, offset, ref, intended=0.0, note=''):
    ok = abs(offset - intended) <= TOL
    RM['items'].append(dict(name=name, offset_m=round(offset, 3), reference=ref, intended_m=intended, result='PASS' if ok else 'FAIL', note=note))
ME = [o for o in bpy.data.objects if o.name.startswith('MH_win_') and o.instance_type == 'COLLECTION']
wo_m = next((o for o in bpy.data.objects if o.get('osm_id') == '312933183' and o.name.endswith('walls')), None)
if wo_m and ME:
    pw_m, fh_m, wb_m = float(wo_m['win_pitch']), float(wo_m['floor_h']), float(wo_m['win_bottom']); u0_m = float(wo_m.get('win_u0', 0))
    runs_m = {}
    for e in ME:
        bu = e['bay_u']; off = ((bu - u0_m) / pw_m - 0.5) % 1.0; off = (off if off < 0.5 else off - 1.0) * pw_m
        if abs(off) > TOL: mitem(f'{e.name} centre vs bay centre', off, f'bay grid pitch {pw_m} m')
        nx = e.get('run') or 'unknown'; runs_m.setdefault(nx, []).append(e)
    spacing_m = []; rows_m = []
    for k, es in runs_m.items():
        for r in sorted({e['row'] for e in es}):
            rs = sorted([e for e in es if e['row'] == r], key=lambda e: e['bay_u']); zs = [e.matrix_world[2][3] for e in rs]
            d = [rs[i + 1]['bay_u'] - rs[i]['bay_u'] for i in range(len(rs) - 1)]
            # allow intentional multi-bay gaps (pavilion / entrances) — only flag within-gap deviation from integer bays
            dev = [abs(x - pw_m * round(x / pw_m)) for x in d]
            spacing_m.append(dict(face_normal=k, row=r, count=len(rs), max_spacing_dev_m=round(max(dev), 4) if dev else 0.0, gaps_in_bays=[round(x / pw_m) for x in d if round(x / pw_m) > 1]))
            rows_m.append(dict(face_normal=k, row=r, sill_z_spread_m=round(max(zs) - min(zs), 3)))
            mitem(f'Morehead run {k} row {r}: max spacing deviation from {pw_m} m bays', max(dev) if dev else 0.0, 'bay pitch')
            mitem(f'Morehead run {k} row {r}: sill level spread (level floor line)', max(zs) - min(zs), 'one floor datum per run')
    RM['wing_runs'] = spacing_m; RM['wing_rows_sill_spread'] = rows_m; RM['wing_windows'] = len(ME)
    sag_m = [e.get('sill_above_ground') for e in ME if e.get('row') == 0 and e.get('sill_above_ground') is not None]
    if sag_m:
        RM['ground_floor_sill_above_local_ground_m'] = [round(min(sag_m), 2), round(max(sag_m), 2)]
        print('  INFO Morehead ground-floor sills above local ground: %.2f..%.2f m' % (min(sag_m), max(sag_m)))
    # pavilion left alone: no MH_win within pavilion radius
    pav = bpy.data.objects.get('Morehead entrance pavilion body')
    if pav:
        pvs = [pav.matrix_world @ v.co for v in pav.data.vertices]; pc = sum(pvs, Vector()) / len(pvs)
        near = [e for e in ME if (e.matrix_world.translation.xy - pc.xy).length < 2.95]
        mitem('No MH_win inside pavilion half-width (2.95 m)', 0.0 if not near else 1.0, 'pavilion clear', note=f'{len(near)} inside' if near else 'clear')
fails_m = [i for i in RM['items'] if i['result'] == 'FAIL']
print('ALIGNMENT MOREHEAD: items', len(RM['items']), 'fail', len(fails_m), 'tol', TOL, 'windows', RM.get('wing_windows', 0))
for i in RM['items']: print(f"  {i['result']:4s} {i['name']}: {i.get('offset_m','')} (intended {i.get('intended_m','')}) {i.get('note','')}")
for s_ in RM.get('wing_runs', []): print('  RUN', s_)
json.dump(RM, open(os.path.join(ROOT, 'data', 'alignment_morehead.json'), 'w'), indent=1)
print('WROTE data/alignment_morehead.json')

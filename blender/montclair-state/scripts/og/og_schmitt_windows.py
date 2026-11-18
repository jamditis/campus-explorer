"""2026-10-31 session og (~8:30 AM ET). Schmitt Hall (OSM 313023306) in MAIN: generated facade-shader windows -> real
modelled punched windows (Joe's standing real-windows item). Port of scripts/morehead_windows.py.
Type: linked assets/windows_ccom.blend 'CCOM_Win_Wing_A' (campus mission family), instanced with a non-uniform scale to a
SMALLER 1.6 x 1.8 m opening so three storeys fit under the eave (wall 137.8 -> 149.0, soffit ~147.9; survey: ~3 storeys).
Cells whose outward ray hits another building within 3 m (e.g. the Finley join) are skipped.
NO photo of Schmitt Hall yet: size, pitch, storey height (3.5 m) and row count ALL UNVERIFIED.
Run: blender -b montclair_state.blend --python scripts/og/og_schmitt_windows.py -- [--plan-only] [--save]
REVERT=1: restores the pre-cut wall mesh + facade UVs, removes SCH_win_* and the collection."""
import bpy, math, os, sys
from mathutils import Vector, Matrix
ROOT_ = os.path.dirname(bpy.data.filepath)
ASSET = '/workspace/nj-scenes/assets/windows_ccom.blend'
TYPE = 'CCOM_Win_Wing_A'
PLAN_ONLY = '--plan-only' in sys.argv
REVERT = os.environ.get('REVERT') == '1'
wo = bpy.data.objects['Schmitt Hall walls']
me = wo.data; mw = wo.matrix_world
ORIG = bpy.data.meshes.get('Schmitt walls (pre-window-cut)')
if REVERT:
    if ORIG is not None and wo.get('windows_modelled'):
        cutm = wo.data; wo.data = ORIG.copy(); wo.data.name = 'Schmitt Hall walls'; bpy.data.meshes.remove(cutm)
        bpy.data.meshes.remove(ORIG)
        del wo['windows_modelled']
    for o in [o for o in bpy.data.objects if o.name.startswith('SCH_win_')]: bpy.data.objects.remove(o, do_unlink=True)
    c = bpy.data.collections.get('OG_Schmitt_Hall_windows_modelled_20261031og')
    if c: bpy.data.collections.remove(c)
    for k in ('og_note', 'UNVERIFIED_windows'):
        if k in wo: del wo[k]
    print('REVERTED'); 
    if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
pw, fh, wb = 3.6, 3.5, 0.9
ww, wh = 1.6, 1.8
u0off = float(wo.get('win_u0', 0.0))
if wo.get('windows_modelled') and ORIG is not None:
    cutm = wo.data; wo.data = ORIG.copy(); wo.data.name = 'Schmitt Hall walls'; bpy.data.meshes.remove(cutm); me = wo.data
elif ORIG is None:
    ORIG = me.copy(); ORIG.name = 'Schmitt walls (pre-window-cut)'; ORIG.use_fake_user = True
uvl = me.uv_layers['facade']
# og plinth (was og_plinth.py): terrain falls ~5 m to the N/NE outside the footprint; wall-bottom verts (z < 138.3) drop to
# (min terrain within 0.8 m) - 0.3 m so the stucco reaches grade (exposed lower storey on the slope). UNVERIFIED.
ter = bpy.data.objects['Terrain_LiDAR_DTM_1m']; ti = ter.matrix_world.inverted()
def tz(x, y):
    h, l, n_, i_ = ter.ray_cast(ti @ Vector((x, y, 400)), (0, 0, -1))
    return (ter.matrix_world @ l).z if h else None
_mi = mw.inverted(); _moved = 0
for v in me.vertices:
    p_ = mw @ v.co
    if p_.z >= 138.3: continue
    zs = [tz(p_.x + dx, p_.y + dy) for dx, dy in ((0, 0), (0.8, 0), (-0.8, 0), (0, 0.8), (0, -0.8), (0.56, 0.56), (-0.56, 0.56), (0.56, -0.56), (-0.56, -0.56))]
    zs = [z for z in zs if z is not None]
    if zs and min(zs) - 0.3 < p_.z: v.co = _mi @ Vector((p_.x, p_.y, min(zs) - 0.3)); _moved += 1
me.update(); wo['og_plinth'] = 'wall bottoms dropped to grade - 0.3 m (%d verts), og' % _moved
print('plinth verts moved', _moved)
FACES = []
for f in me.polygons:
    L = list(f.loop_indices); P = [mw @ me.vertices[me.loops[l].vertex_index].co for l in L]; U = [uvl.data[l].uv.copy() for l in L]
    o = sorted(range(4), key=lambda k: (U[k].x, U[k].y)); a0, a1 = o[0], o[1]; b0, b1 = o[2], o[3]
    if U[a1].y < U[a0].y: a0, a1 = a1, a0
    if U[b1].y < U[b0].y: b0, b1 = b1, b0
    if abs(U[b0].x - U[a0].x) < 1e-4: continue
    FACES.append(dict(u0=U[a0].x, u1=U[b0].x, p0=P[a0], p1=P[b0], g0=P[a0].z - U[a0].y, g1=P[b0].z - U[b0].y, t0=P[a1].z, t1=P[b1].z, n=Vector(f.normal)))
FACES.sort(key=lambda d: d['u0'])
cen = sum((d['p0'] for d in FACES), Vector()) / max(len(FACES), 1)
def at(u):
    for d in FACES:
        if d['u0'] - 1e-6 <= u <= d['u1'] + 1e-6:
            s = (u - d['u0']) / (d['u1'] - d['u0']); p = d['p0'].lerp(d['p1'], s)
            return d, p, d['g0'] + (d['g1'] - d['g0']) * s, d['t0'] + (d['t1'] - d['t0']) * s
    return None, None, None, None
def tdir(d):
    v = (d['p1'] - d['p0']); v.z = 0; return v.normalized() if v.length > 1e-6 else Vector((1, 0, 0))
DG = bpy.context.evaluated_depsgraph_get()
def neighbour(p, n):
    o0 = p + n * 0.05 + Vector((0, 0, 1.5))
    hit, loc, nor, idx, ob, _ = bpy.context.scene.ray_cast(DG, o0, n, distance=3.0)
    if not hit or ob is None: return None
    nm = ob.name
    if ob == wo or nm.startswith('Schmitt'): return None
    low = nm.lower()
    if low.startswith('t_') or any(k in low for k in ('tree', 'terrain', 'lamp', 'shrub', 'grass', 'hedge', 'bush', 'nt_', 'plant', 'light', 'lidar ground', 'walk', 'path')): return None
    return nm
GAP = 0.15
def along_near(pc, t, q, half, depth=2.5):
    d = (q.xy - pc.xy); return abs(d.dot(t.xy)) < half + ww / 2 + GAP and abs(d.dot(Vector((t.y, -t.x)))) < depth
total = max(d['u1'] for d in FACES) if FACES else 0
cells = []; skipped = {}; NB = set()
m = 0
while (m + 0.5) * pw + u0off < total:
    uc = (m + 0.5) * pw + u0off; m += 1
    dA, pA, _, _ = at(uc - ww / 2 - 0.2); dB, pB, _, _ = at(uc + ww / 2 + 0.2); dC, pC, gC, _ = at(uc)
    if dA is None or dB is None or dC is None: continue
    t = tdir(dC)
    if tdir(dA).dot(t) < 0.995 or tdir(dB).dot(t) < 0.995: skipped['corner'] = skipped.get('corner', 0) + 1; continue
    n = Vector((t.y, -t.x, 0))
    if ((pC + n) - cen).xy.length < ((pC - n) - cen).xy.length: n = -n
    tops = [at(uc + s)[3] for s in (-ww / 2, 0, ww / 2)]
    nb = neighbour(Vector((pC.x, pC.y, gC)), n)
    if nb: skipped['neighbour'] = skipped.get('neighbour', 0) + 1; NB.add(nb); continue
    sec = False
    cells.append(dict(u=uc, g=gC, top=min(tops), pc=pC, t=t, n=n, sec=sec))
# level floors: one floor datum per straight wall run; same row count on every bay of the run
RUNS = {}
for c in cells:
    key = (round(c['n'].x, 2), round(c['n'].y, 2), round(c['pc'].xy.dot(c['n'].xy)))
    RUNS.setdefault(key, []).append(c)
DATUM = {}
_so = bpy.data.objects.get('Schmitt Hall eave soffit + fascia + rafter tails')
SOFFIT_MIN = min((_so.matrix_world @ v.co).z for v in _so.data.vertices) if _so else 1e9
print('soffit bottom', round(SOFFIT_MIN, 2))
GDATUM = 138.38   # og: the datum 9 of 14 runs chose (lowest high-ground + eave fit)
cols, cells = cells, []
for key, cs in RUNS.items():
    g_hi = max(c['g'] for c in cs); top_min = min(min(c['top'] for c in cs), SOFFIT_MIN + 0.35 + 0.15)   # window head <= 0.15 m above the global soffit/rafter minimum (west soffit sits higher; per-cell soffit check is a TODO)
    nr = 0
    while g_hi + wb + nr * fh + wh + 0.35 <= top_min: nr += 1
    datum = g_hi
    d2 = top_min - 0.35 - wh - nr * fh - wb      # could one more row fit if the datum drops a little (sill still >= 0.5 m above the high ground)?
    lowcut = -99.0
    if d2 >= g_hi - 0.4: nr += 1; datum = min(g_hi, d2)
    elif d2 >= min(c['g'] for c in cs) - 0.4:   # sloping run: level floors from the eave; ground-floor openings only where grade is low enough (sill >= 0.5 m)
        nr += 1; datum = d2; lowcut = 0.5
    # og: one building-wide floor datum (storeys line up all round the building); ground row only where sill >= 0.5 m above grade
    datum = GDATUM; nr = 0; lowcut = 0.5
    while datum + wb + nr * fh + wh + 0.35 <= top_min + 1e-6: nr += 1
    DATUM[str(key)] = (datum, nr)
    for c in cs:
        for row in range(nr):
            zb = datum + wb + row * fh
            if row == 0 and zb - c['g'] < lowcut: skipped['below_grade_row0'] = skipped.get('below_grade_row0', 0) + 1; continue
            cells.append(dict(u=c['u'], row=row, p=Vector((c['pc'].x, c['pc'].y, zb)), t=c['t'], n=c['n'], run=str(key), g_local=c['g']))
        # og: lower (walk-out) storey where the terrain has fallen away: sill >= 0.5 m above the lowest grade 1-2 m out
        zl = datum + wb - fh
        gl = [tz(*(c['pc'] + c['n'] * dd).xy) for dd in (1.0, 2.0)]
        gl = [z for z in gl if z is not None]
        if gl and max(gl) <= zl - 0.5:
            cells.append(dict(u=c['u'], row=-1, p=Vector((c['pc'].x, c['pc'].y, zl)), t=c['t'], n=c['n'], run=str(key), g_local=max(gl)))
        elif gl and max(gl) < datum - 0.3: skipped['lower_row_grade_too_high'] = skipped.get('lower_row_grade_too_high', 0) + 1
print('Schmitt windows: cells', len(cells), 'skipped', skipped, 'runs', len(RUNS), 'props', pw, ww, fh, wh, wb)
for k_, (d_, r_) in DATUM.items(): print('  run', k_, 'datum', round(d_, 2), 'rows', r_)
print('neighbours hit', sorted(NB))
if PLAN_ONLY: raise SystemExit(0)
for o in [o for o in bpy.data.objects if o.name.startswith('SCH_win_') or o.name.startswith('Schmitt window cutter')]:
    bpy.data.objects.remove(o, do_unlink=True)
col = bpy.data.collections.get('OG_Schmitt_Hall_windows_modelled_20261031og')
if col is None: col = bpy.data.collections.new('OG_Schmitt_Hall_windows_modelled_20261031og'); bpy.context.scene.collection.children.link(col)
# cut openings
V, F = [], []
for c in cells:
    hw = ww / 2; p, t, n = c['p'], c['t'], c['n']; b = len(V)
    for z in (p.z, p.z + wh):
        for a, w in ((-hw, -0.6), (hw, -0.6), (hw, 0.6), (-hw, 0.6)):
            q = p + t * a + n * w; V.append((q.x, q.y, z))
    F += [tuple(b + i for i in f) for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))]
cme = bpy.data.meshes.new('Schmitt window cutter'); cme.from_pydata(V, [], F); cme.validate(); cme.update()
cut = bpy.data.objects.new('Schmitt window cutter', cme); bpy.context.scene.collection.objects.link(cut)
nf0 = len(me.polygons)
md = wo.modifiers.new('sch_window_cut', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.solver = 'EXACT'; md.object = cut
try: md.use_hole_tolerant = True
except Exception: pass
with bpy.context.temp_override(object=wo, active_object=wo, selected_objects=[wo]):
    bpy.ops.object.modifier_apply(modifier=md.name)
bpy.data.objects.remove(cut, do_unlink=True); bpy.data.meshes.remove(cme)
print('wall faces', nf0, '->', len(wo.data.polygons))
# shader windows off
uvl = wo.data.uv_layers['facade']
for d in uvl.data:
    if d.uv.y > -500: d.uv.y -= 1000.0
wo['windows_modelled'] = 'CCOM_Win_Wing_A instances scaled to 1.6x1.8 (scripts/og/og_schmitt_windows.py, 2026-10-31 og)'
wo['UNVERIFIED_windows'] = 'no photo: size, pitch, 3.5 m storeys, rows all guessed (og)'
# instances
if TYPE not in bpy.data.collections:
    with bpy.data.libraries.load(ASSET, link=True) as (src_, dst_): dst_.collections = [TYPE]
ac = bpy.data.collections[TYPE]
for k, c in enumerate(cells):
    X = c['t']; Y = c['n']; Z = Vector((0, 0, 1)); X = Y.cross(Z)
    e = bpy.data.objects.new((f'SCH_win_{k:03d}_r{c["row"]}' if c['row'] >= 0 else f'SCH_win_{k:03d}_rL'), None); e.instance_type = 'COLLECTION'; e.instance_collection = ac
    SX = ww / float(ac.get('opening_w', 2.6)); SZ = wh / float(ac.get('opening_h', 2.6))
    e.matrix_world = Matrix(((X.x * SX, Y.x, 0, c['p'].x), (X.y * SX, Y.y, 0, c['p'].y), (0, 0, SZ, c['p'].z), (0, 0, 0, 1)))
    e['bay_u'] = round(c['u'], 3); e['row'] = c['row']; e['run'] = c['run']
    e['sill_above_ground'] = round(c['p'].z - c['g_local'], 2); e['type'] = TYPE; e['status'] = 'UNVERIFIED size/pattern'
    e['UNVERIFIED'] = '1'
    col.objects.link(e)
print('Schmitt windows placed', len(cells), 'asset', ASSET)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')

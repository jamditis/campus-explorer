"""Morehead Hall wing windows: generated facade-shader windows -> real modelled windows (Joe, 2026-10-14).
West pavilion arched/round windows are already geometry and are left alone. N/S/E secondary entrances skipped.
Runs standalone:
    blender -b montclair_state.blend --python scripts/morehead_windows.py -- --save
What it does on 'Morehead Hall walls':
  1. window cells = facade grid (bay pitch win_pitch, floor_h, win_w x win_h, sill win_bottom), only where the whole
     opening sits on ONE straight wall run below the eave, clear of the west pavilion and N/S/E secondary entrances;
  2. cuts real openings (boolean EXACT) and turns the shader windows off on Morehead (facade v shifted -1000);
  3. places linked instances of assets/windows_morehead.blend 'MH_Win_Paired_Casement';
  4. deletes superseded 'Morehead Hall window reveals + sills' (and any Morehead aluminium frames if present).
  5. one level floor datum per straight wall run (Joe's rule).
UNVERIFIED: wing window size/muntin on N/S/E (only west Commons photo); pavilion already geometry."""
import bpy, math, os, sys
from mathutils import Vector, Matrix
ROOT_ = globals().get('ROOT') or os.path.dirname(bpy.data.filepath)
ASSET = '/workspace/nj-scenes/assets/windows_morehead.blend'
TYPE = 'MH_Win_Paired_Casement'
# find Morehead walls
wo = None
for o in bpy.data.objects:
    if o.get('osm_id') == '312933183' and o.name.endswith('walls'):
        wo = o; break
if wo is None:
    wo = next(o for o in bpy.data.objects if o.name.startswith('Morehead Hall walls'))
me = wo.data; mw = wo.matrix_world
pw, ww, fh, wh, wb = (float(wo[k]) for k in ('win_pitch', 'win_w', 'floor_h', 'win_h', 'win_bottom')); u0off = float(wo.get('win_u0', 0.0))
uvl = me.uv_layers['facade']
ORIG = bpy.data.meshes.get('Morehead walls (pre-window-cut)')
if wo.get('windows_modelled') and ORIG is not None:
    cutm = wo.data; wo.data = ORIG.copy(); wo.data.name = cutm.name + '_r'; bpy.data.meshes.remove(cutm); me = wo.data
elif ORIG is None:
    ORIG = me.copy(); ORIG.name = 'Morehead walls (pre-window-cut)'; ORIG.use_fake_user = True
uvl = me.uv_layers['facade']
# 2026-10-14 SE-view fix: 70 east/south wall strips (u ~94-133) stop at 139-141.3 m under a roof whose eave edge is ~143.4 m,
# leaving a dark void under the soffit. Raise those wall tops to the main wall-top level (UNVERIFIED: LiDAR eave read low there).
_zs = sorted(v.co.z for v in me.vertices); WALL_TOP = _zs[-1]
_lifted = 0
_bot = {}
for f in me.polygons:
    zz = [me.vertices[i].co.z for i in f.vertices]
    for i in f.vertices: _bot[i] = min(_bot.get(i, 1e9), min(zz))
for f in me.polygons:
    for li in f.loop_indices:
        vi = me.loops[li].vertex_index; v = me.vertices[vi]
        if v.co.z - _bot[vi] > 3.0 and v.co.z < WALL_TOP - 0.3:
            dz = WALL_TOP - v.co.z
            uvl.data[li].uv.y += dz
for v in me.vertices:
    if v.co.z - _bot[v.index] > 3.0 and v.co.z < WALL_TOP - 0.3: v.co.z = WALL_TOP; _lifted += 1
me.update(); wo['wall_top_lift_note'] = f'{_lifted} low wall-top verts raised to {WALL_TOP:.2f} m (UNVERIFIED; morehead_windows.py)'
print('wall tops lifted', _lifted, 'to', round(WALL_TOP, 2))
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
# exclusions: west pavilion + N/S/E secondary entrances
PAV = None
me_obj = bpy.data.objects.get('Morehead entrance pavilion body')
if me_obj:
    vs = [me_obj.matrix_world @ v.co for v in me_obj.data.vertices]
    PAV = sum(vs, Vector()) / len(vs)
# also try scene custom prop / lettering centre
if PAV is None:
    for nm in ('Morehead lettering', 'Morehead door recess'):
        o = bpy.data.objects.get(nm)
        if o:
            vs = [o.matrix_world @ Vector(c) for c in o.bound_box]
            PAV = sum(vs, Vector()) / len(vs); break
PAV_W2 = 2.95   # pavilion body half-width along the wall (build_scene.py W2)
PAV_T = None
if me_obj:
    _vs = [me_obj.matrix_world @ v.co for v in me_obj.data.vertices]
# secondary portals (3i, UNVERIFIED positions): the door surround covers the ground-floor cell only (cornice +-1.62 m, top 3.6 m)
SEC = []
for o in bpy.data.objects:
    n = o.name
    if n.startswith('Morehead') and 'entrance (secondary' in n and n.endswith('entablature'):
        vs = [o.matrix_world @ Vector(c) for c in o.bound_box]; SEC.append(sum(vs, Vector()) / len(vs))
SEC_C = []
for p in SEC:
    if all((p - q).xy.length > 2.0 for q in SEC_C): SEC_C.append(p)
SEC_HALF, SEC_TOP = 1.62, 3.6
print('Morehead PAV', None if PAV is None else (round(PAV.x, 2), round(PAV.y, 2)), 'SEC centres', len(SEC_C), [(round(p.x,1), round(p.y,1)) for p in SEC_C])
GAP = 0.15
def along_near(pc, t, q, half, depth=2.5):
    d = (q.xy - pc.xy); return abs(d.dot(t.xy)) < half + ww / 2 + GAP and abs(d.dot(Vector((t.y, -t.x)))) < depth
total = max(d['u1'] for d in FACES) if FACES else 0
cells = []; skipped = {}
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
    if PAV is not None and along_near(pC, t, PAV, PAV_W2): skipped['pavilion'] = skipped.get('pavilion', 0) + 1; continue
    sec = any(along_near(pC, t, q, SEC_HALF) for q in SEC_C)
    cells.append(dict(u=uc, g=gC, top=min(tops), pc=pC, t=t, n=n, sec=sec))
# level floors: one floor datum per straight wall run; same row count on every bay of the run
RUNS = {}
for c in cells:
    key = (round(c['n'].x, 2), round(c['n'].y, 2), round(c['pc'].xy.dot(c['n'].xy)))
    RUNS.setdefault(key, []).append(c)
DATUM = {}
_so = bpy.data.objects.get('Morehead Hall eave soffit + fascia + rafter tails')
SOFFIT_MIN = min((_so.matrix_world @ v.co).z for v in _so.data.vertices) if _so else 1e9
print('soffit bottom', round(SOFFIT_MIN, 2))
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
    DATUM[str(key)] = (datum, nr)
    for c in cs:
        for row in range(nr):
            zb = datum + wb + row * fh
            if c['sec'] and row == 0 and zb - datum < SEC_TOP: skipped['entrance_row0'] = skipped.get('entrance_row0', 0) + 1; continue
            if row == 0 and zb - c['g'] < lowcut: skipped['below_grade_row0'] = skipped.get('below_grade_row0', 0) + 1; continue
            cells.append(dict(u=c['u'], row=row, p=Vector((c['pc'].x, c['pc'].y, zb)), t=c['t'], n=c['n'], run=str(key), g_local=c['g']))
print('Morehead windows: cells', len(cells), 'skipped', skipped, 'runs', len(RUNS), 'props', pw, ww, fh, wh, wb)
for k_, (d_, r_) in DATUM.items(): print('  run', k_, 'datum', round(d_, 2), 'rows', r_)
# clean previous + delete superseded reveal/frame objects (Morehead only)
for o in [o for o in bpy.data.objects if o.name.startswith('MH_win_') or o.name.startswith('Morehead window cutter')]:
    bpy.data.objects.remove(o, do_unlink=True)
for nm in ('Morehead Hall window reveals + sills', 'Morehead Hall window frames (aluminium)'):
    o = bpy.data.objects.get(nm)
    if o: bpy.data.objects.remove(o, do_unlink=True)
col = bpy.data.collections.get('Morehead_windows_modelled')
if col is None: col = bpy.data.collections.new('Morehead_windows_modelled'); bpy.context.scene.collection.children.link(col)
# cut openings
V, F = [], []
for c in cells:
    hw = ww / 2; p, t, n = c['p'], c['t'], c['n']; b = len(V)
    for z in (p.z, p.z + wh):
        for a, w in ((-hw, -0.6), (hw, -0.6), (hw, 0.6), (-hw, 0.6)):
            q = p + t * a + n * w; V.append((q.x, q.y, z))
    F += [tuple(b + i for i in f) for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))]
cme = bpy.data.meshes.new('Morehead window cutter'); cme.from_pydata(V, [], F); cme.validate(); cme.update()
cut = bpy.data.objects.new('Morehead window cutter', cme); bpy.context.scene.collection.objects.link(cut)
nf0 = len(me.polygons)
md = wo.modifiers.new('mh_window_cut', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.solver = 'EXACT'; md.object = cut
try: md.use_hole_tolerant = True
except Exception: pass
with bpy.context.temp_override(object=wo, active_object=wo, selected_objects=[wo]):
    bpy.ops.object.modifier_apply(modifier=md.name)
bpy.data.objects.remove(cut, do_unlink=True); bpy.data.meshes.remove(cme)
print('wall faces', nf0, '->', len(wo.data.polygons))
# level sill course: the 3i sill band (box 0 of each 3-box segment) follows the run datum where a window run covers it
sco = bpy.data.objects.get('Morehead Hall sill course + base moulding (3i)')
moved = 0
if sco:
    if 'sill_z_orig' not in sco:
        sco['sill_z_orig'] = [v.co.z for v in sco.data.vertices]
    zo = list(sco['sill_z_orig']); vv = sco.data.vertices; smw = sco.matrix_world
    for b in range(0, len(vv) // 8):
        if b % 3: continue
        cc = sum((smw @ vv[b * 8 + j].co for j in range(8)), Vector()) / 8
        best = None
        for k_, (d_, r_) in DATUM.items():
            nx, ny, off = eval(k_)
            if abs(cc.x * nx + cc.y * ny - off) > 0.9: continue
            # same run: nearest window cell on that run within 2 bays along the wall
            ds = [(cc.xy - c['p'].xy).length for c in cells if c['run'] == k_]
            if ds and min(ds) < 2.0 * pw and (best is None or min(ds) < best[0]): best = (min(ds), d_)
        for j in range(8):
            vv[b * 8 + j].co.z = zo[b * 8 + j]
        if best:
            z0, z1 = best[1] + wb - 0.12, best[1] + wb - 0.02
            for j in range(8): vv[b * 8 + j].co.z = z0 if j < 4 else z1
            moved += 1
    sco.data.update(); sco['sill_course_note'] = 'sill band levelled to the window run datum where windows exist (morehead_windows.py 2026-10-14)'
print('sill course boxes levelled', moved)
# shader windows off
uvl = wo.data.uv_layers['facade']
for d in uvl.data:
    if d.uv.y > -500: d.uv.y -= 1000.0
wo['windows_modelled'] = 'MH_Win_Paired_Casement instances (scripts/morehead_windows.py, 2026-10-14)'
wo['UNVERIFIED'] = 'window sizes/muntins from Commons west photo + facade grid; N/S/E faces unphotographed'
# instances
if TYPE not in bpy.data.collections:
    with bpy.data.libraries.load(ASSET, link=True) as (src_, dst_): dst_.collections = [TYPE]
ac = bpy.data.collections[TYPE]
for k, c in enumerate(cells):
    X = c['t']; Y = c['n']; Z = Vector((0, 0, 1)); X = Y.cross(Z)
    e = bpy.data.objects.new(f'MH_win_{k:03d}_r{c["row"]}', None); e.instance_type = 'COLLECTION'; e.instance_collection = ac
    e.matrix_world = Matrix(((X.x, Y.x, 0, c['p'].x), (X.y, Y.y, 0, c['p'].y), (0, 0, 1, c['p'].z), (0, 0, 0, 1)))
    e['bay_u'] = round(c['u'], 3); e['row'] = c['row']; e['run'] = c['run']
    e['sill_above_ground'] = round(c['p'].z - c['g_local'], 2); e['type'] = TYPE; e['status'] = 'UNVERIFIED size/pattern'
    e['UNVERIFIED'] = '1'
    col.objects.link(e)
print('Morehead windows placed', len(cells), 'asset', ASSET)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')

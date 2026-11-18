"""CCOM wing windows: generated facade-shader windows -> real modelled windows (Joe, 2026-10-14 8:03 AM ET).
Runs at the end of build_scene.py (after ccom_tower.py) and standalone:
    blender -b montclair_state.blend --python scripts/ccom_windows.py -- --save
What it does on 'School of Communication and Media walls':
  1. window cells = the facade grid the shader used (bay pitch win_pitch, floor_h, win_w x win_h, sill win_bottom above the wall's
     v=0 ground reference), only where the whole opening + 0.35 m sits on ONE straight wall run below the eave, clear of the tower
     (+1.5 m) and the main entrance surround (3.7 m radius);
  2. cuts real openings in the wall (boolean, EXACT, hole-tolerant) and turns the shader windows off on CCOM (facade v shifted -1000);
  3. places linked collection instances of assets/windows_ccom.blend 'CCOM_Win_Wing_A' (reveal liner, sill, frame + mullion +
     transom, inset glass pane, room box, blind) - one mesh set in memory, N empties;
  4. deletes the superseded day-2 'window reveals + sills' / 'window frames (aluminium)' objects of CCOM.
UNVERIFIED: wing window size / mullion pattern (grid + the 2021 render look; no close photo of the wing windows)."""
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix
ROOT_ = globals().get('ROOT') or os.path.dirname(bpy.data.filepath)
ASSET = os.path.join(os.path.dirname(os.path.dirname(ROOT_)) if ROOT_.endswith('montclair-state') else '/workspace/nj-scenes', 'assets', 'windows_ccom.blend')
ASSET = '/workspace/nj-scenes/assets/windows_ccom.blend' if not os.path.exists(ASSET) else ASSET
TYPE = 'CCOM_Win_Wing_A'
wo = bpy.data.objects['School of Communication and Media walls']; me = wo.data; mw = wo.matrix_world
pw, ww, fh, wh, wb = (float(wo[k]) for k in ('win_pitch', 'win_w', 'floor_h', 'win_h', 'win_bottom')); u0off = float(wo.get('win_u0', 0.0))
uvl = me.uv_layers['facade']
# already converted? restore the original v so the grid can be recomputed (idempotent re-run)
ORIG = bpy.data.meshes.get('CCOM walls (pre-window-cut)')
if wo.get('windows_modelled') and ORIG is not None:   # re-run: restore the uncut wall mesh (kept with a fake user), then redo
    cutm = wo.data; wo.data = ORIG.copy(); wo.data.name = cutm.name + '_r'; bpy.data.meshes.remove(cutm); me = wo.data
elif ORIG is None:
    ORIG = me.copy(); ORIG.name = 'CCOM walls (pre-window-cut)'; ORIG.use_fake_user = True
uvl = me.uv_layers['facade']
# ---- wall runs (faces are vertical quads, u = perimeter metres)
FACES = []
for f in me.polygons:
    L = list(f.loop_indices); P = [mw @ me.vertices[me.loops[l].vertex_index].co for l in L]; U = [uvl.data[l].uv.copy() for l in L]
    o = sorted(range(4), key=lambda k: (U[k].x, U[k].y)); a0, a1 = o[0], o[1]; b0, b1 = o[2], o[3]   # (u-min: low, high), (u-max: low, high)
    if U[a1].y < U[a0].y: a0, a1 = a1, a0
    if U[b1].y < U[b0].y: b0, b1 = b1, b0
    if abs(U[b0].x - U[a0].x) < 1e-4: continue
    FACES.append(dict(u0=U[a0].x, u1=U[b0].x, p0=P[a0], p1=P[b0], g0=P[a0].z - U[a0].y, g1=P[b0].z - U[b0].y, t0=P[a1].z, t1=P[b1].z, n=Vector(f.normal)))
FACES.sort(key=lambda d: d['u0'])
cen = sum((d['p0'] for d in FACES), Vector()) / len(FACES)
def at(u):
    for d in FACES:
        if d['u0'] - 1e-6 <= u <= d['u1'] + 1e-6:
            s = (u - d['u0']) / (d['u1'] - d['u0']); p = d['p0'].lerp(d['p1'], s)
            return d, p, d['g0'] + (d['g1'] - d['g0']) * s, d['t0'] + (d['t1'] - d['t0']) * s
    return None, None, None, None
def tdir(d): v = (d['p1'] - d['p0']); v.z = 0; return v.normalized()
# exclusions: tower shaft (+1.5 m) and entrance surround
TW = {}
try:
    src = open(os.path.join(ROOT_, 'scripts', 'ccom_tower.py')).read().split('col = None')[0]; exec(src, TW)
except Exception as ex: print('tower zone unavailable', ex)
pa, pb = bpy.data.objects.get('CCOM entrance pier +1'), bpy.data.objects.get('CCOM entrance pier -1')
ENT = None
if pa and pb:
    ca = sum((pa.matrix_world @ v.co for v in pa.data.vertices), Vector()) / len(pa.data.vertices)
    cb = sum((pb.matrix_world @ v.co for v in pb.data.vertices), Vector()) / len(pb.data.vertices); ENT = ((ca + cb) / 2).xy
def blocked(p2):
    if TW.get('_inside') and TW['_inside'](TW['SHAFT'], p2, 1.5): return 'tower'
    if ENT is not None and (p2 - ENT).length < 3.7 + ww / 2: return 'entrance'
    return None
total = max(d['u1'] for d in FACES); cells = []; skipped = {}
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
    why = blocked(pC.xy) or blocked((pC + t * (ww / 2)).xy) or blocked((pC - t * (ww / 2)).xy)
    if why: skipped[why] = skipped.get(why, 0) + 1; continue
    cells.append(dict(u=uc, g=gC, top=min(tops), pc=pC, t=t, n=n))
# level floors: every straight wall run uses ONE floor datum (the highest local ground reference on the run), so sills line up
# along the run instead of stepping with grade (the old facade grid followed grade per strip)
RUNS = {}
for c in cells:
    key = (round(c['n'].x, 2), round(c['n'].y, 2), round(c['pc'].xy.dot(c['n'].xy)))
    RUNS.setdefault(key, []).append(c)
cols, cells = cells, []
for key, cs in RUNS.items():
    g_run = max(c['g'] for c in cs)
    for c in cs:
        row = 0
        while True:
            zb = g_run + wb + row * fh; zt = zb + wh
            if zt + 0.35 > c['top']: break
            if zb - c['g'] > wb + 2.5 and row == 0: pass
            cells.append(dict(u=c['u'], row=row, p=Vector((c['pc'].x, c['pc'].y, zb)), t=c['t'], n=c['n'], run=str(key), g_local=c['g'])); row += 1
print('CCOM windows: cells', len(cells), 'skipped', skipped, 'runs', len(RUNS))
# ---- clean previous runs + superseded day-2 reveal/frame objects
for o in [o for o in bpy.data.objects if o.name.startswith('CCOM_win_') or o.name.startswith('CCOM window cutter')]: bpy.data.objects.remove(o, do_unlink=True)
for nm in ('School of Communication and Media window reveals + sills', 'School of Communication and Media window frames (aluminium)'):
    o = bpy.data.objects.get(nm)
    if o: bpy.data.objects.remove(o, do_unlink=True)
col = bpy.data.collections.get('CCOM_windows_modelled')
if col is None: col = bpy.data.collections.new('CCOM_windows_modelled'); bpy.context.scene.collection.children.link(col)
# ---- cut openings: one cutter mesh, boolean applied on the wall
V, F = [], []
for c in cells:
    hw = ww / 2; p, t, n = c['p'], c['t'], c['n']; b = len(V)
    for z in (p.z, p.z + wh):
        for a, w in ((-hw, -0.6), (hw, -0.6), (hw, 0.6), (-hw, 0.6)):
            q = p + t * a + n * w; V.append((q.x, q.y, z))
    F += [tuple(b + i for i in f) for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))]
cme = bpy.data.meshes.new('CCOM window cutter'); cme.from_pydata(V, [], F); cme.validate(); cme.update()
cut = bpy.data.objects.new('CCOM window cutter', cme); bpy.context.scene.collection.objects.link(cut)
nf0 = len(me.polygons)
if True:
    md = wo.modifiers.new('ccom_window_cut', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.solver = 'EXACT'; md.object = cut
    try: md.use_hole_tolerant = True
    except Exception: pass
    with bpy.context.temp_override(object=wo, active_object=wo, selected_objects=[wo]): bpy.ops.object.modifier_apply(modifier=md.name)
bpy.data.objects.remove(cut, do_unlink=True); bpy.data.meshes.remove(cme)
print('wall faces', nf0, '->', len(wo.data.polygons))
# shader windows off on CCOM (geometry replaces them)
uvl = wo.data.uv_layers['facade']
for d in uvl.data:
    if d.uv.y > -500: d.uv.y -= 1000.0
wo['windows_modelled'] = 'CCOM_Win_Wing_A instances (scripts/ccom_windows.py, 2026-10-14)'
# ---- instances
if TYPE not in bpy.data.collections:
    with bpy.data.libraries.load(ASSET, link=True) as (src_, dst_): dst_.collections = [TYPE]
ac = bpy.data.collections[TYPE]
for k, c in enumerate(cells):
    X = c['t']; Y = c['n']; Z = Vector((0, 0, 1)); X = Y.cross(Z)   # right-handed: X along the wall, Y outward
    e = bpy.data.objects.new(f'CCOM_win_{k:03d}_r{c["row"]}', None); e.instance_type = 'COLLECTION'; e.instance_collection = ac
    e.matrix_world = Matrix(((X.x, Y.x, 0, c['p'].x), (X.y, Y.y, 0, c['p'].y), (0, 0, 1, c['p'].z), (0, 0, 0, 1)))
    e['bay_u'] = round(c['u'], 3); e['row'] = c['row']; e['run'] = c['run']; e['sill_above_ground'] = round(c['p'].z - c['g_local'], 2); e['type'] = TYPE; e['status'] = 'UNVERIFIED size/pattern'; col.objects.link(e)
print('CCOM windows placed', len(cells), 'asset', ASSET)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')

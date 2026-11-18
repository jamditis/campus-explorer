"""CCOM (ex-SCM) bell tower: rebuild as ONE projecting square volume and clean the wing geometry around it.
Session 4a (2026-10-13). Runs at the end of build_scene.py (exec) and standalone on montclair_state.blend:
    blender -b montclair_state.blend --python scripts/ccom_tower.py -- --save
Massing sources:
  * OSM way 1188721159 footprint: tower = 1.1 m projection on the west face, SW corner (-20.0, 18.3) -> NW (-18.3, 25.0), 6.9 m.
  * USGS 3DEP DSM (data/dsm_1m.npy): hip roof, eave ~155.9 m, apex ~157.8 m, shaft+eaves ~8.4 x 7.8 m -> shaft ~6.9 m square.
    (DSM sits ~1.5 m S of OSM here; OSM kept so the tower lines up with the OSM wing walls.)
  * Commons File:School_of_Communications.jpg (2021): plain white square shaft, tan base, ONE tall arched window (single column
    of panes, maroon frames) on the west face, black lettering above it, two arched belfry openings per face under a deep
    red-brown hipped eave. The wing's own eave dies into the tower sides; the tower has no lower eave and no per-floor windows.
2026-10-14: lettering -> COLLEGE OF / COMMUNICATION AND MEDIA (Joe); Downspouts pad 0.45 -> 1.2 removes orphan elbow stubs ~9-10 m up on the west face.
UNVERIFIED (guessed): projection depth exactness, window width/offset, belfry size, north/east faces, eave overhang.
"""
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector, Matrix

_ROOT = globals().get('ROOT') or os.path.dirname(bpy.data.filepath)
_dtm = np.load(os.path.join(_ROOT, 'data', 'dtm_1m.npy')); _HH = _dtm.shape[0] / 2
def _gz(x, y): return float(_dtm[int(y + _HH), int(x + _HH)])

A = Vector((-20.0, 18.3)); T = Vector((1.7, 6.7)).normalized(); NO = Vector((-T.y, T.x))   # NO = outward (west)
if NO.x > 0: NO = -NO
W = 6.9; D = 6.9
G = min(_gz(*(A + T * u)) for u in (0.5, 3.4, 6.4)) ; G = max(G, 137.25)   # grade at the west face (DTM ~137.3)
Z_EAVE = 155.65; Z_APEX = 157.8; OVH = 0.85
def P(u, w): return A + T * u + NO * w        # u along west face (S->N), w outward (+) / inward (-)
SHAFT = [P(0, 0), P(W, 0), P(W, -D), P(0, -D)]

def _inside(poly, p, pad=0.0):
    # convex quad test in (u, w) space
    q = p - A; u = q.dot(T); w = q.dot(NO)
    return -pad <= u <= W + pad and -D - pad <= w <= pad
def _uw(p): q = p - A; return q.dot(T), q.dot(NO)
def _cut_zone(p):   # shaft + free-standing eave strips (west face full length, south face 1.1 m, north face first 3.7 m)
    u, w = _uw(p)
    if -0.03 <= u <= W + 0.03 and -D - 0.03 <= w <= 0.03: return True
    if -1.15 <= u <= W + 1.15 and 0 <= w <= 1.15: return True
    if W <= u <= W + 1.15 and -3.7 <= w <= 1.15: return True
    if -1.15 <= u <= 0 and -1.1 <= w <= 1.15: return True
    return False

col = None
old = bpy.data.objects.get('CCOM tall section (LiDAR 22 m)')
col = old.users_collection[0] if old else bpy.data.collections.get('Day2_details')
def mat(name, c=None, rough=0.5, metal=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*c, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    return m
def first_mat(objname, fallback):
    o = bpy.data.objects.get(objname)
    return o.data.materials[0] if o and o.data.materials else fallback
m_wall = mat('SCM_tower_precast', (0.90, 0.87, 0.80), 0.8)
m_base = mat('Cast_stone_tan', (0.62, 0.50, 0.34), 0.75)
m_glass = mat('Dark_glass', (0.02, 0.025, 0.03), 0.05)
m_frame = mat('Mullion_mahogany', (0.10, 0.026, 0.02), 0.45)
m_blk = mat('Lettering_black', (0.01, 0.01, 0.01), 0.4)
m_shadow = mat('Belfry_opening_shadow', (0.025, 0.022, 0.02), 0.9)
m_roof = first_mat('School of Communication and Media roof (LiDAR)', mat('Roof_tile_red', (0.25, 0.06, 0.03), 0.6))
m_fasc = first_mat('School of Communication and Media eave soffit + fascia + rafter', mat('Eave_fascia_dark_wood', (0.05, 0.027, 0.014), 0.85))

# ---- 1. delete the old tower pieces (LiDAR prism with per-floor generic windows, coping, lettering)
for nm in ('CCOM tall section (LiDAR 22 m)', 'CCOM tall section coping', 'CCOM tower trim (string courses, reveals, cornice)',
           'CCOM tower glass', 'CCOM tower mullions', 'CCOM tower lettering SCHOOL OF', 'CCOM tower lettering COLLEGE OF', 'CCOM tower lettering COMMUNICATION AND MEDIA'):
    o = bpy.data.objects.get(nm)
    if o: bpy.data.objects.remove(o, do_unlink=True)
for o in [o for o in bpy.data.objects if o.name.startswith('CCOM tower 4a')]: bpy.data.objects.remove(o, do_unlink=True)

# ---- 2. clean the wing around the tower
def cut_faces(name):
    o = bpy.data.objects.get(name)
    if not o or o.type != 'MESH': return 0
    bm = bmesh.new(); bm.from_mesh(o.data); mw = o.matrix_world
    kill = [f for f in bm.faces if (lambda c: _cut_zone(c.xy) and c.z > G + 3.0)(mw @ f.calc_center_median())]
    bmesh.ops.delete(bm, geom=kill, context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update(); return len(kill)
def cut_islands(name, pad):
    o = bpy.data.objects.get(name)
    if not o or o.type != 'MESH': return 0
    bm = bmesh.new(); bm.from_mesh(o.data); mw = o.matrix_world; bm.verts.ensure_lookup_table(); seen = set(); kill = []
    for v in bm.verts:
        if v.index in seen: continue
        isl = [v]; seen.add(v.index); st = [v]
        while st:
            x = st.pop()
            for e in x.link_edges:
                y = e.other_vert(x)
                if y.index not in seen: seen.add(y.index); isl.append(y); st.append(y)
        if any(_inside(SHAFT, (mw @ y.co).xy, pad) for y in isl): kill.extend(isl)
    bmesh.ops.delete(bm, geom=kill, context='VERTS'); bm.to_mesh(o.data); bm.free(); o.data.update(); return len(kill)
REP = {}
for nm in ('School of Communication and Media barrel tile eave course', 'School of Communication and Media eave soffit + fascia + rafter',
           'School of Communication and Media hip + ridge cap tiles', 'School of Communication and Media roof (LiDAR)',
           'Gutters half-round (3f, Life/CCOM UNVERIFIED)', 'Eave drip / moss streaks on stucco (3g)'):
    REP[nm] = cut_faces(nm)
for nm, pad in (('School of Communication and Media window reveals + sills', 0.35), ('School of Communication and Media window frames (aluminium)', 0.35),
                ('Downspouts (3f)', 1.2), ('Downspout boots + drain grates (3g, CCOM)', 0.6), ('Downspout cleanout plugs brass (3h, CCOM)', 0.6),
                ('Downspout splash blocks (3f)', 0.9)):
    REP[nm] = cut_islands(nm, pad)
# wing wall: no shader windows on the faces under/against the tower or within 1.5 m of it (no half windows cut by the tower)
wo = bpy.data.objects.get('School of Communication and Media walls'); nmask = 0
if wo:
    me = wo.data; uvl = me.uv_layers.get('facade'); mw = wo.matrix_world
    for f in me.polygons:
        c = (mw @ f.center).xy
        if _inside(SHAFT, c, 1.5) and uvl:
            for li in f.loop_indices:
                if uvl.data[li].uv.y > -500: uvl.data[li].uv.y -= 1000.0; nmask += 1
REP['wall loops masked'] = nmask

# ---- 3. build the tower
OBJ = []
def frame(u, w):   # local frame: x along T, y outward NO, z world
    p = P(u, w); return Matrix(((T.x, NO.x, 0, p.x), (T.y, NO.y, 0, p.y), (0, 0, 1, 0), (0, 0, 0, 1)))
XF = frame(0, 0)
VB = {}
def add(key, V, F):
    b = VB.setdefault(key, ([], [])); o_ = len(b[0]); b[0].extend(V); b[1].extend([tuple(i + o_ for i in f) for f in F])
def box(key, u0, u1, w0, w1, z0, z1):
    V = [(u, w, z) for z in (z0, z1) for (u, w) in ((u0, w0), (u1, w0), (u1, w1), (u0, w1))]
    add(key, V, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
def arch_prof(hw, zs, n=10):   # outline of an arched opening in (a, z): a across, springing at zs, radius hw
    return [(-hw, None)] + [(-hw * math.cos(math.pi * k / n), zs + hw * math.sin(math.pi * k / n)) for k in range(n + 1)]
def arch_slab(key, face, ac, hw, z0, zs, w0, w1, n=12):
    # prism with an arched top on a face; face: 0=W (u along), 1=S, 2=N, 3=E (local coordinates handled by fp())
    prof = [(ac - hw, z0), (ac + hw, z0)] + [(ac + hw * math.cos(math.pi * k / n), zs + hw * math.sin(math.pi * k / n)) for k in range(n + 1)]
    m_ = len(prof); V = [fp(face, a, w0, z) for a, z in prof] + [fp(face, a, w1, z) for a, z in prof]
    F = [tuple(range(m_))[::-1], tuple(range(m_, 2 * m_))] + [(k, (k + 1) % m_, m_ + (k + 1) % m_, m_ + k) for k in range(m_)]
    add(key, V, F)
def arch_ring(key, face, ac, hw, t, z0, zs, w0, w1, n=12):
    for s in (-1, 1): add_box_face(key, face, ac + s * hw - (t if s < 0 else 0), ac + s * hw + (t if s > 0 else 0), w0, w1, z0, zs)
    for k in range(n):
        a0, a1 = math.pi * k / n, math.pi * (k + 1) / n; pts = []
        for r in (hw, hw + t):
            pts += [(ac + r * math.cos(a0), zs + r * math.sin(a0)), (ac + r * math.cos(a1), zs + r * math.sin(a1))]
        q = [pts[0], pts[1], pts[3], pts[2]]
        V = [fp(face, a, w0, z) for a, z in q] + [fp(face, a, w1, z) for a, z in q]
        add(key, V, [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
def fp(face, a, w, z):
    # point on face `face` at across-coordinate a (0..W left->right seen from outside), outward offset w, height z -> local (u, w)
    if face == 0: return (W - a, w, z) if False else (a, w, z)                 # west: u = a
    if face == 1: return (-w, -a, z)                                           # south: outward = -u
    if face == 2: return (W + w, -D + a, z)                                    # north: outward = +u
    return (W - a, -D - w, z)                                                  # east: outward = -w
def add_box_face(key, face, a0, a1, w0, w1, z0, z1):
    q = [(a0, w0), (a1, w0), (a1, w1), (a0, w1)]
    V = [fp(face, a, w, z) for z in (z0, z1) for (a, w) in q]
    add(key, V, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])

zb = G - 0.6
box('shaft', 0, W, -D, 0, zb, Z_EAVE)                                          # the one volume
for f_ in range(4):
    add_box_face('base', f_, -0.08, W + 0.08 if f_ in (0, 3) else D + 0.08, -0.02, 0.08, zb + 0.4, G + 0.62)        # tan cast-stone base (photo)
    add_box_face('trim', f_, -0.1, W + 0.1 if f_ in (0, 3) else D + 0.1, -0.02, 0.12, G + 13.75, G + 13.95)          # sill band under the belfry
    for ac in (2.25, 4.65):                                                     # two arched belfry openings per face (photo; N/E UNVERIFIED)
        arch_slab('belfry', f_, ac, 0.55, G + 13.95, G + 16.85, -0.02, 0.006)
        arch_ring('trim', f_, ac, 0.55, 0.16, G + 13.95, G + 16.85, -0.02, 0.07)
# west face: one tall arched window, single column of panes (photo); offset 0.6 m north of centre UNVERIFIED
WC, WHW, WZ0, WZS = 4.05, 0.82, G + 0.95, G + 6.85
arch_slab('glass', 0, WC, WHW, WZ0, WZS, -0.02, 0.012)
arch_ring('frame', 0, WC, WHW - 0.06, 0.06, WZ0, WZS, -0.02, 0.05)
add_box_face('frame', 0, WC - WHW, WC + WHW, -0.02, 0.05, WZ0, WZ0 + 0.08)
for k in range(1, 11):
    z_ = WZ0 + k * (WZS - WZ0) / 8.0
    if z_ < WZS + WHW * 0.75:
        hw_ = WHW if z_ <= WZS else math.sqrt(max(WHW ** 2 - (z_ - WZS) ** 2, 0))
        add_box_face('frame', 0, WC - hw_, WC + hw_, -0.02, 0.045, z_ - 0.035, z_ + 0.035)
arch_ring('trim', 0, WC, WHW + 0.0, 0.14, WZ0 - 0.1, WZS, -0.02, 0.06)          # white surround (photo)
add_box_face('trim', 0, WC - WHW - 0.2, WC + WHW + 0.2, -0.02, 0.12, WZ0 - 0.18, WZ0 - 0.02)
# hipped roof: deep overhang, red-brown fascia/soffit, tile cover
o_ = OVH; cs = [(-o_, o_), (W + o_, o_), (W + o_, -D - o_), (-o_, -D - o_)]
apex = (W / 2, -D / 2, Z_APEX)
add('fascia', [(u, w, Z_EAVE - 0.05) for u, w in cs] + [(u, w, Z_EAVE + 0.32) for u, w in cs],
    [(0, 1, 2, 3)[::-1], (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
add('roof', [(u, w, Z_EAVE + 0.32) for u, w in cs] + [apex], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)])

names = {'shaft': ('CCOM tower 4a shaft (one volume, OSM+LiDAR)', m_wall), 'base': ('CCOM tower 4a cast-stone base', m_base),
         'trim': ('CCOM tower 4a trim (belfry band, arch surrounds)', m_wall), 'belfry': ('CCOM tower 4a belfry openings (UNVERIFIED N/E)', m_shadow),
         'glass': ('CCOM tower 4a tall arched window glass', m_glass), 'frame': ('CCOM tower 4a tall arched window frame', m_frame),
         'fascia': ('CCOM tower 4a hip eave fascia + soffit', m_fasc), 'roof': ('CCOM tower 4a hip roof tiles', m_roof)}
for k, (V, F) in VB.items():
    nm, m_ = names[k]; me = bpy.data.meshes.new(nm); me.from_pydata(V, [], F); me.validate(); me.update()
    o = bpy.data.objects.new(nm, me); col.objects.link(o); me.materials.append(m_); o.matrix_world = XF
    if k in ('belfry',): o['position'] = 'UNVERIFIED'
    OBJ.append(nm)
# lettering above the window, below the wing eave (layout from the 2021 photo; text = current name per Joe 2026-10-14)
for body, sz, z_ in (('COLLEGE OF', 0.26, G + 8.55), ('COMMUNICATION AND MEDIA', 0.22, G + 8.15)):
    cu = bpy.data.curves.new('CCOM tower 4a lettering ' + body, 'FONT'); cu.body = body; cu.size = sz; cu.extrude = 0.008
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.materials.append(m_blk)
    tx = bpy.data.objects.new('CCOM tower 4a lettering ' + body, cu); col.objects.link(tx)
    tx.matrix_world = XF @ Matrix.Translation((W * 0.5, 0.012, z_)) @ Matrix.Rotation(math.radians(180), 4, 'Z') @ Matrix.Rotation(math.radians(90), 4, 'X')
print('CCOM TOWER 4a grade', round(G, 2), 'objects', OBJ, 'cleanup', REP)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()

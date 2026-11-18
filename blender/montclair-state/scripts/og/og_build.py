"""Session og (Oct 31 2026 ~8:40 AM ET), MAIN, Schmitt Hall. ALL UNVERIFIED (no photo of Schmitt yet).
1) Flat membrane deck + dark-bronze coping cap at the top of the tile mansard band (inset 3.0 m from the OSM footprint, LiDAR flat
   roof 151.34) -> hides the sawtooth where the slope-switch shader met the LiDAR triangles; straight clean mansard top edge.
2) One entrance where OSM footways 1132693541/1132693542 end on the ESE facade at (10.6, 141.1): wall opening, storefront
   double door + transom, dark vestibule, concrete landing at LiDAR grade; nearby ground-row SCH_win hidden (not deleted).
REVERT=1 removes everything and restores the pre-og-build wall mesh + window visibility."""
import bpy, bmesh, json, math, os, sys
from mathutils import Vector, Matrix
REVERT = os.environ.get('REVERT') == '1'
CN = 'OG_Schmitt_Hall_mansard_cap_entrance_20261031og'
sc = bpy.context.scene
wo = bpy.data.objects['Schmitt Hall walls']
PRE = 'Schmitt walls (pre-og-entrance-cut)'
def rm_col():
    c = bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(c)
st = json.loads(wo.get('og_build_state', '{}'))
if st or REVERT:
    rm_col()
    for n in st.get('hidden', []):
        o = bpy.data.objects.get(n)
        if o: o.hide_render = False; o.hide_viewport = False
    pm = bpy.data.meshes.get(PRE)
    if pm is not None:
        old = wo.data; wo.data = pm.copy(); wo.data.name = 'Schmitt Hall walls'; bpy.data.meshes.remove(old); bpy.data.meshes.remove(pm)
    if 'og_build_state' in wo: del wo['og_build_state']
    if REVERT:
        print('REVERTED'); bpy.ops.wm.save_mainfile() if '--save' in sys.argv else None; raise SystemExit(0)
col = bpy.data.collections.new(CN); sc.collection.children.link(col)
def mat(name, rgb, rough, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    return m
M_MEM = mat('OG_roof_membrane_light_grey_UNVERIFIED', (0.55, 0.55, 0.53), 0.75)
M_CAP = mat('OG_coping_cap_dark_bronze_UNVERIFIED', (0.09, 0.07, 0.055), 0.45, 0.8)
M_BRZ = mat('OG_storefront_dark_bronze_UNVERIFIED', (0.07, 0.06, 0.05), 0.4, 0.85)
M_DARK = mat('OG_vestibule_dark_UNVERIFIED', (0.03, 0.03, 0.03), 0.9)
M_CON = mat('OG_landing_concrete_UNVERIFIED', (0.42, 0.41, 0.39), 0.85)
gm = bpy.data.materials.get('OG_door_glass_tinted_UNVERIFIED') or bpy.data.materials.new('OG_door_glass_tinted_UNVERIFIED'); gm.use_nodes = True
gb = gm.node_tree.nodes['Principled BSDF']; gb.inputs['Base Color'].default_value = (0.35, 0.38, 0.38, 1); gb.inputs['Roughness'].default_value = 0.03
gb.inputs['Transmission Weight'].default_value = 1.0; gb.inputs['IOR'].default_value = 1.5
def obj(name, bm, m):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(name, me); col.objects.link(o); o['UNVERIFIED'] = 'og: no photo of Schmitt Hall'; return o
def box(bm, c, X, Y, sx, sy, z0, z1):
    vs = []
    for z in (z0, z1):
        for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            p = c + X * (a * sx / 2) + Y * (b * sy / 2); vs.append(bm.verts.new((p.x, p.y, z)))
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): bm.faces.new([vs[i] for i in f])
# ---- 1) deck + coping
ring = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), 'data/og/schmitt_deck_inset3_og.json')))[0][0]
ZD = 151.37
bm = bmesh.new(); fv = [bm.verts.new((x, y, ZD)) for x, y in ring]
f = bm.faces.new(fv); f.normal_update()
if f.normal.z < 0: f.normal_flip()
obj('OG_Schmitt_roof_membrane_deck', bm, M_MEM)
bm = bmesh.new(); Z = Vector((0, 0, 1))
for i in range(len(ring)):
    a = Vector((*ring[i], 0)); b = Vector((*ring[(i + 1) % len(ring)], 0)); d = b - a; L = d.length
    if L < 0.05: continue
    X = d / L; Y = Z.cross(X)
    box(bm, (a + b) / 2, X, Y, L + 0.30, 0.30, 151.28, 151.47)
obj('OG_Schmitt_mansard_coping_cap', bm, M_CAP)
# ---- 2) entrance
DG = bpy.context.evaluated_depsgraph_get()
def rc(o, d, dist):
    t = 0.0
    while t < dist:
        h, l, nn, i, ob, _ = sc.ray_cast(DG, o + d * t, d, distance=dist - t)
        if not h: return None, None, None
        if ob.name.startswith('T_') or 'tree' in ob.name.lower() or ob.name.startswith('CCOM_Win'): t += (l - (o + d * t)).length + 0.05; continue
        return l, nn, ob
    return None, None, None
N = Vector((0.92, -0.40, 0)).normalized(); X = Vector((0, 0, 1)).cross(N)   # outward ESE normal; X along the wall
E0 = Vector((10.6, 141.1, 0))
g, _, gob = rc(Vector((E0.x + N.x * 1.5, E0.y + N.y * 1.5, 300)), Vector((0, 0, -1)), 400); G = g.z
wp, wn, wob = rc(Vector((E0.x, E0.y, 142.2)) + N * 4, -N, 8)
print('grade', round(G, 2), 'on', gob.name, 'wall hit', wob.name if wob else None, wp)
W0 = Vector((wp.x, wp.y, 0)); W0 = W0 + 0 * N
DW, DH, TR = 2.3, 2.35, 0.55            # door pair width, door height, transom height (campus storefront guess)
Z0 = G + 0.05; Z1 = Z0 + DH + TR
hidden = []
for o in bpy.data.objects:
    if o.name.startswith('SCH_win_') and o.name.endswith('_r0'):
        p = o.matrix_world.translation; d = (Vector((p.x, p.y, 0)) - W0)
        if abs(d.dot(X)) < DW / 2 + 1.0 and abs(d.dot(N)) < 1.0: o.hide_render = True; o.hide_viewport = True; hidden.append(o.name)
print('hidden windows', hidden)
pm = wo.data.copy(); pm.name = PRE; pm.use_fake_user = True
bm = bmesh.new(); box(bm, W0, X, N, DW + 0.2, 1.2, Z0 - 0.3, Z1 + 0.05)
cme = bpy.data.meshes.new('og_cut'); bm.to_mesh(cme); bm.free(); cut = bpy.data.objects.new('og_cut', cme); sc.collection.objects.link(cut)
md = wo.modifiers.new('og_door_cut', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.solver = 'EXACT'; md.object = cut
with bpy.context.temp_override(object=wo, active_object=wo, selected_objects=[wo]): bpy.ops.object.modifier_apply(modifier=md.name)
bpy.data.objects.remove(cut, do_unlink=True); bpy.data.meshes.remove(cme)
IN = W0 - N * 0.12                      # storefront plane, set 12 cm into the opening
bm = bmesh.new()
OW = DW + 0.2
box(bm, IN + X * (-OW / 2 + 0.05), X, N, 0.10, 0.15, Z0, Z1)     # jambs
box(bm, IN + X * (OW / 2 - 0.05), X, N, 0.10, 0.15, Z0, Z1)
box(bm, IN, X, N, OW, 0.15, Z1 - 0.10, Z1)                        # head
box(bm, IN, X, N, OW - 0.2, 0.15, Z0 + DH, Z0 + DH + 0.10)        # transom bar
box(bm, IN, X, N, 0.07, 0.15, Z0, Z0 + DH)                        # meeting stiles
for s in (-1, 1):
    lc = IN + X * (s * DW / 4)
    box(bm, lc, X, N, DW / 2 - 0.08, 0.06, Z0, Z0 + 0.25)          # bottom rails
    box(bm, lc + X * (-s * (DW / 4 - 0.12)), X, N, 0.03, 0.10, Z0 + 0.9, Z0 + 1.6)   # vertical pulls
    for side in (-1, 1): box(bm, lc + X * (side * (DW / 4 - 0.07)), X, N, 0.06, 0.06, Z0, Z0 + DH)   # leaf stiles
    box(bm, lc, X, N, DW / 2 - 0.08, 0.06, Z0 + DH - 0.08, Z0 + DH)   # top rails
obj('OG_Schmitt_E_entrance_storefront_frame', bm, M_BRZ)
bm = bmesh.new()
for s in (-1, 1): box(bm, IN + X * (s * DW / 4), X, N, DW / 2 - 0.15, 0.012, Z0 + 0.25, Z0 + DH - 0.08)
box(bm, IN, X, N, OW - 0.2, 0.012, Z0 + DH + 0.10, Z1 - 0.10)
obj('OG_Schmitt_E_entrance_glass', bm, gm)
bm = bmesh.new()
VC = W0 - N * 1.2
box(bm, VC + X * (-OW / 2 - 0.05), X, N, 0.1, 2.0, Z0 - 0.05, Z1 + 0.1); box(bm, VC + X * (OW / 2 + 0.05), X, N, 0.1, 2.0, Z0 - 0.05, Z1 + 0.1)
box(bm, W0 - N * 2.25, X, N, OW + 0.2, 0.1, Z0 - 0.05, Z1 + 0.1); box(bm, VC, X, N, OW + 0.2, 2.0, Z1 + 0.05, Z1 + 0.15); box(bm, VC, X, N, OW + 0.2, 2.0, Z0 - 0.06, Z0 - 0.0)
obj('OG_Schmitt_E_entrance_vestibule_dark', bm, M_DARK)
bm = bmesh.new(); box(bm, W0 + N * 0.9 + N * 0.0, X, N, 3.4, 2.0, G - 0.25, Z0 - 0.01)
obj('OG_Schmitt_E_entrance_landing', bm, M_CON)
wo['og_build_state'] = json.dumps(dict(hidden=hidden, grade=round(G, 3), wall=[round(wp.x, 3), round(wp.y, 3)]))
print('OG build done', len(col.objects))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')

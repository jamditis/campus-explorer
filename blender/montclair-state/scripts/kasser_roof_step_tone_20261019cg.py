"""Session cg (Oct 19 ~5:40 PM ET). MAIN blend (Kasser's owner). Idempotent, SAVE=1 saves.
RUN ORDER: this script FIRST re-runs scripts/kasser_rhd_junction_trim_20261019cf.py (SAVE forced 0; it restores the 4 Kasser meshes
from cf_orig_* and redoes the cf trim), THEN applies the cg fixes. So run THIS script instead of the cf one (it supersedes it as the entry
point; the cf script stays the trim implementation). Never run the cf script alone and save, or the cg fixes are lost (materials too,
because the cf restore copies mesh data incl. material slots).
cg fixes:
 1) Roof step: the jagged steep-faceted wedge (LiDAR facets with normal z 0.1-0.7) where the flat membrane strip along the deck meets
    the tile slope, just north of the RHD SE stair core (s = 1.8..~5 m into Kasser from the shared OSM edge, u = ~5..7.5 m along A->B),
    is deleted and covered by a clean box: flat top at the MEASURED strip height (median of the flat strip faces), vertical stucco
    sides down below the tile surface -> reads as a clean vertical step/parapet edge. Finish UNVERIFIED.
 2) Tone: Kasser-only material copies (*__kasser_cg) for roof tile/membrane, eave tile top/soffit and barrel-tile eave course with a
    Hue/Saturation/Value node before Base Color (SAT 0.90, VAL 0.80 by default after the cg test pair; first try 0.82/0.94 read pinkish; env KSAT/KVAL). Other main buildings keep the shared
    materials. Tone matching to the RHD hip roofs under north's light is UNVERIFIED.
 3) 4a BVH check of all 4 Kasser objects vs the RHD tris (cf npz) is printed (must be 0)."""
import bpy, bmesh, os, runpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
KSAT = float(os.environ.get('KSAT', '0.90')); KVAL = float(os.environ.get('KVAL', '0.80'))
os.environ['SAVE'] = '0'
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_rhd_junction_trim_20261019cf.py', run_name='__main__')
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def su(x, y): p = np.array([x, y]) - A; return float(p @ n), float(p @ d)
def xy(s, u): p = A + n * s + d * u; return float(p[0]), float(p[1])
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']
M = ro.matrix_world.copy(); Mi = M.inverted()
bm = bmesh.new(); bm.from_mesh(ro.data); bm.transform(M); bm.normal_update()
# --- 1) wedge faces
ZS, ZU = (1.7, 6.0), (4.0, 8.5)
wedge = []; strip = []
for f in bm.faces:
    if f.material_index != 0: continue
    c = f.calc_center_median(); s, u = su(c.x, c.y)
    if not (ZS[0] < s < ZS[1] and ZU[0] < u < ZU[1]): continue
    if 0.08 < f.normal.z < 0.75: wedge.append(f)
    elif f.normal.z > 0.995: strip.append(f)
SU = np.array([su(v.co.x, v.co.y) for f in wedge for v in f.verts])
zstrip = float(np.median([f.calc_center_median().z for f in strip]))
S0 = 1.85; S1 = min(float(SU[:, 0].max()) + 0.05, 5.6); U0 = float(SU[:, 1].min()) - 0.05; U1 = float(SU[:, 1].max()) + 0.05
print('cg wedge faces', len(wedge), 'strip faces', len(strip), 'zstrip(MEASURED median)', round(zstrip, 3), 'box s', round(S0, 2), round(S1, 2), 'u', round(U0, 2), round(U1, 2), flush=True)
# inside-box verts above the top would poke through: report
inside = [v for v in bm.verts if S0 <= su(v.co.x, v.co.y)[0] <= S1 and U0 <= su(v.co.x, v.co.y)[1] <= U1]
zin = [v.co.z for v in inside]
print('cg inside-box verts', len(inside), 'z range', round(min(zin), 2), round(max(zin), 2), flush=True)
ref = max(strip, key=lambda f: f.calc_area())
refl = ref.loops[0]
bmesh.ops.delete(bm, geom=wedge, context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
ztop = max(zstrip, max(zin)) + 0.01; zbot = min(zin) - 0.25
# stucco slot for the step sides
stucco = bpy.data.materials.get('Wall_stucco_mission')
if stucco.name not in [m.name for m in ro.data.materials if m]: ro.data.materials.append(stucco)
mi_st = [m.name if m else '' for m in ro.data.materials].index(stucco.name)
corners = [(S0, U0), (S1, U0), (S1, U1), (S0, U1)]
top = [bm.verts.new((*xy(s, u), ztop), ref.verts[0]) for s, u in corners]
bot = [bm.verts.new((*xy(s, u), zbot), ref.verts[0]) for s, u in corners]
newf = []
ft = bm.faces.new(top, ref); ft.material_index = 0; newf.append(ft)
if ft.normal_update() or True:
    if ft.normal.z < 0: ft.normal_flip()
for i in range(4):
    j = (i + 1) % 4
    f = bm.faces.new((bot[i], bot[j], top[j], top[i]), ref); f.material_index = mi_st; newf.append(f)
bm.normal_update()
cen = Vector((*xy((S0 + S1) / 2, (U0 + U1) / 2), (ztop + zbot) / 2))
for f in newf[1:]:
    if (f.calc_center_median() - cen).dot(f.normal) < 0: f.normal_flip()
# copy loop attributes (colour/alpha/uv) from the reference strip loop so the shader reads the new top as membrane
for lay in list(bm.loops.layers.color.values()) + list(bm.loops.layers.float_color.values()) + list(bm.loops.layers.uv.values()) + list(bm.loops.layers.float.values()):
    for f in newf:
        for l in f.loops:
            try: l[lay] = refl[lay]
            except Exception: pass
for lay in bm.loops.layers.uv.values():
    for f in newf:
        for l in f.loops: l[lay].uv = refl[lay].uv
print('cg step box ztop', round(ztop, 3), 'zbot', round(zbot, 2), 'step height at south edge ~', round(ztop - zbot - 0.25, 2), 'max (to lowest tile)', flush=True)
ro['cg_roof_step'] = f'box s {S0:.2f}..{S1:.2f} u {U0:.2f}..{U1:.2f} ztop {ztop:.3f} (strip median {zstrip:.3f}) wedge faces {len(wedge)}'
# --- 3) 4a check
z = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = z['tris']; ob = z['obj']; nm = z['names']; keep = np.array([not str(nm[i]).startswith('NT_') for i in ob]); T = T[keep]
RB = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3*i, 3*i+1, 3*i+2) for i in range(len(T))])
bm.verts.ensure_lookup_table()
print('cg 4a roof (after step) overlap pairs', len(BVHTree.FromBMesh(bm).overlap(RB)), flush=True)
bm.transform(Mi); bm.to_mesh(ro.data); bm.free(); ro.data.update()
for on in ['Alexander Kasser Theater walls', 'Alexander Kasser Theater eave soffit + fascia + rafter tails', 'Alexander Kasser Theater barrel tile eave course']:
    o = bpy.data.objects[on]; b2 = bmesh.new(); b2.from_mesh(o.data); b2.transform(o.matrix_world)
    print('cg 4a', on[:40], 'overlap pairs', len(BVHTree.FromBMesh(b2).overlap(RB)), flush=True); b2.free()
# --- 2) tone (Kasser-only copies)
def kmat(name):
    src = bpy.data.materials.get(name)
    if src is None: return None
    cn = name + '__kasser_cg'; m = bpy.data.materials.get(cn)
    if m is None:
        m = src.copy(); m.name = cn
        nt = m.node_tree; bsdf = next(nd for nd in nt.nodes if nd.type == 'BSDF_PRINCIPLED')
        sock = bsdf.inputs['Base Color']
        hsv = nt.nodes.new('ShaderNodeHueSaturation'); hsv.name = 'cg_kasser_tone'; hsv.location = bsdf.location.x - 200, bsdf.location.y - 300
        if sock.is_linked:
            fs = sock.links[0].from_socket; nt.links.new(fs, hsv.inputs['Color'])
        else:
            hsv.inputs['Color'].default_value = sock.default_value
        nt.links.new(hsv.outputs['Color'], sock)
    h = m.node_tree.nodes['cg_kasser_tone']; h.inputs['Saturation'].default_value = KSAT; h.inputs['Value'].default_value = KVAL
    return m
swap = {}
for on in ['Alexander Kasser Theater roof (LiDAR)', 'Alexander Kasser Theater eave soffit + fascia + rafter tails', 'Alexander Kasser Theater barrel tile eave course']:
    me = bpy.data.objects[on].data
    for i, m in enumerate(me.materials):
        if m and m.name in ('Roof_tile_or_membrane', 'Eave_tile_top_soffit_under', 'Roof_barrel_tile_course'):
            km = kmat(m.name); me.materials[i] = km; swap[on[:30] + '#' + str(i)] = km.name
print('cg tone swaps', swap, 'KSAT', KSAT, 'KVAL', KVAL, flush=True)
bpy.data.objects['Alexander Kasser Theater walls']['cg_kasser_tone'] = f'SAT {KSAT} VAL {KVAL} (UNVERIFIED tone match)'
if SAVE: bpy.ops.wm.save_mainfile(); print('cg main: SAVED', flush=True)

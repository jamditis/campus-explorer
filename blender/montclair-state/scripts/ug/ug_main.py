"""Session ug (Nov 5 2026 ~4:40 PM ET, MAIN, day-9 leftovers): Partridge E-side ground seam + approach cleanup.
A) Fill the 3 m DTM nodata seam (y~247.5-251) + SA_ground_lower_patch dip E of Partridge with an interpolated
   lawn patch (UNVERIFIED interpolation between trusted DTM row y=246.5 and row y=258).
B) Lift SA patch dip verts + paving/rim/footpath verts that sagged into the seam.
C) TY walk 404 no longer ramps over the W stair flight (trim to stair foot, sit on grade).
D) TY E door 407: false 4-riser flight (from the dip) flattened to a sill-level landing; TY E walks lifted.
REVERT=1 restores all meshes from UG_bak_* (fake-user) and deletes ug_obj objects.
"""
import bpy, bmesh, os, json, math
from mathutils import Vector
REV = os.environ.get('REVERT') == '1'; SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
COLN = 'UG_Partridge_E_seam_fix_UNVERIFIED'

def revert():
    for me in [m for m in bpy.data.meshes if m.get('ug_bak_of')]:
        on = me['ug_bak_of']; o = bpy.data.objects.get(on)
        if o:
            mod = o.data; o.data = me
            if mod.users == 0: bpy.data.meshes.remove(mod)
        nm = me['ug_orig_name']; del me['ug_bak_of']; del me['ug_orig_name']
        me.use_fake_user = False; me.name = nm
    for o in [o for o in list(bpy.data.objects) if o.get('ug_obj')]:
        me = o.data; t = o.type
        bpy.data.objects.remove(o, do_unlink=True)
        if me is not None and me.users == 0:
            (bpy.data.meshes if t == 'MESH' else bpy.data.cameras).remove(me)
    c = bpy.data.collections.get(COLN)
    if c: bpy.data.collections.remove(c)
    print('UG REVERTED')

revert()
if REV:
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

def backup(o):
    """keep original mesh with fake user; object gets an editable copy."""
    orig = o.data; nm = orig.name
    cp = orig.copy(); o.data = cp
    orig.name = 'UG_bak_' + nm[:50]; orig.use_fake_user = True
    orig['ug_bak_of'] = o.name; orig['ug_orig_name'] = nm
    cp.name = nm
    return cp

dg = bpy.context.evaluated_depsgraph_get()
def caster(n):
    o = bpy.data.objects[n]; e = o.evaluated_get(dg); mw = o.matrix_world; iw = mw.inverted()
    d = (iw.to_3x3() @ Vector((0, 0, -1))).normalized()
    def f(x, y):
        r = e.ray_cast(iw @ Vector((x, y, 400)), d)
        return ((mw @ r[1]).z, r[3]) if r[0] else (None, None)
    return f
T = caster('Terrain_LiDAR_DTM_1m'); S = caster('SA_ground_lower_patch_UNVERIFIED'); K = caster('Context_skirt_3DEP_ortho_4km')
def trusted(x, y):
    z = T(x, y)[0]
    return z if z is not None else S(x, y)[0]
FP = [tuple(p) for p in json.load(open(D + 'data/tx/nursing_geom.json'))['footprint']]
def inside(x, y):
    c = False; n = len(FP)
    for i in range(n):
        x1, y1 = FP[i]; x2, y2 = FP[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c
Y0, Y1 = 246.5, 258.0
# x extent of the seam: scan at y=249.5
xs = [x for x in range(-130, 60) if T(x + 0.5, 249.5)[0] is None and S(x + 0.5, 249.5)[0] is None and not inside(x + 0.5, 249.5)]
# keep the contiguous run that touches Partridge E face (x>-70)
run = [x for x in xs if -70 <= x <= -37]  # validated by ug_probe3 grid; east of -37 left for later
xa = min(run); xb = max(run) + 1
print('UG seam x run', xa, xb, 'n', len(run))
xa = max(xa, -67.2)
ROW = {}
for k in range(int((xa - 2) * 4), int((xb + 2) * 4) + 1):
    ROW[k] = (trusted(k / 4, Y0), trusted(k / 4, Y1))
def interp(x, y):
    k = int(round(x * 4))
    if k not in ROW: return None
    z0, z1 = ROW[k]
    if z0 is None or z1 is None: return None
    t = min(1, max(0, (y - Y0) / (Y1 - Y0)))
    return z0 * (1 - t) + z1 * t
# ---------- A) patch ----------
step = 0.5
nx = int(math.ceil((xb - xa) / step)); ny = int(math.ceil((Y1 - Y0) / step))
bm = bmesh.new(); V = {}
need = {}
for i in range(nx + 1):
    for j in range(ny + 1):
        x = xa + i * step; y = Y0 + j * step
        zi = interp(x, y)
        if zi is None: continue
        zt = trusted(x, y)
        need[(i, j)] = (zt is None)  # nodata seam only; SA dip handled by lifting SA verts
        V[(i, j)] = (x, y, zi + 0.03)
verts = {}
def gv(k):
    if k not in verts: verts[k] = bm.verts.new(V[k])
    return verts[k]
nf = 0
for i in range(nx):
    for j in range(ny):
        ks = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
        if not all(k in V for k in ks): continue
        if not any(need[k] for k in ks): continue
        cx = sum(V[k][0] for k in ks) / 4; cy = sum(V[k][1] for k in ks) / 4
        if inside(cx, cy): continue
        bm.faces.new([gv(k) for k in ks]); nf += 1
# material + UV fit from SA_ground_lower_patch (ortho UV -> NAIP skirt image; DTM ortho2020 ends at the seam)
sao = bpy.data.objects['SA_ground_lower_patch_UNVERIFIED']; sme = sao.data; smw = sao.matrix_world
suv = sme.uv_layers['ortho']
import numpy as np
A = []; U = []
for poly in sme.polygons:
    c = smw @ poly.center
    if xa - 3 < c.x < xb + 3 and 251 < c.y < 260:
        for li in poly.loop_indices:
            p = smw @ sme.vertices[sme.loops[li].vertex_index].co
            A.append([p.x, p.y, 1]); U.append(list(suv.data[li].uv))
A = np.array(A); U = np.array(U)
coef, res, *_ = np.linalg.lstsq(A, U, rcond=None)
mat = sao.material_slots[0].material
print('UG patch faces', nf, 'mat', mat.name, 'uvfit n', len(A), 'res', res)
uv = bm.loops.layers.uv.new('ortho')
for f in bm.faces:
    for l in f.loops:
        p = l.vert.co; l[uv].uv = (coef[0][0] * p.x + coef[1][0] * p.y + coef[2][0], coef[0][1] * p.x + coef[1][1] * p.y + coef[2][1])
me = bpy.data.meshes.new('UG_Partridge_E_seam_fill_lawn_UNVERIFIED')
bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth = True
me.materials.append(mat)
col = bpy.data.collections.new(COLN); bpy.context.scene.collection.children.link(col)
op = bpy.data.objects.new('UG_Partridge_E_seam_fill_lawn_UNVERIFIED', me); col.objects.link(op)
op['ug_obj'] = 1; op['UNVERIFIED'] = 'linear interpolation across 3DEP/NJ DTM nodata seam between rows y=246.5 and y=258 (ug)'
# ---------- B) lift sagged objects ----------
log = {}
def lift_obj(name, mode):
    o = bpy.data.objects.get(name)
    if not o: return
    mw = o.matrix_world; imw = mw.inverted()
    cand = []
    for v in o.data.vertices:
        p = mw @ v.co
        if xa - 0.5 < p.x < xb + 0.5 and Y0 < p.y < Y1:
            cand.append(v.index)
    if not cand: return
    me2 = backup(o); n = 0
    # column tops for walk-type meshes
    cols = {}
    for vi in cand:
        p = mw @ me2.vertices[vi].co
        k = (round(p.x / 0.03), round(p.y / 0.03)); cols[k] = max(cols.get(k, -1e9), p.z)
    for vi in cand:
        v = me2.vertices[vi]; p = mw @ v.co
        zi = interp(p.x, p.y)
        if zi is None: continue
        if mode == 'ground':
            if p.z < zi - 0.02:
                p.z = zi; v.co = imw @ p; n += 1
        else:  # surface: keep thickness, raise column top to zi + off
            top = cols[(round(p.x / 0.03), round(p.y / 0.03))]
            dz = (zi + 0.04) - top
            if dz > 0.02:
                p.z += dz; v.co = imw @ p; n += 1
    me2.update(); log[name] = n
lift_obj('SA_ground_lower_patch_UNVERIFIED', 'ground')
for nm in ('QXP_pedestrian_area_313024781_paving_UNVERIFIED', 'QY_plaza_rim_band_313024781_UNVERIFIED', 'Footpaths_OSM',
           'TY_footway_313026406_to_Partridge_UNVERIFIED', 'TY_footway_313026407_to_Partridge_UNVERIFIED',
           'TY_footway_313026405_to_Partridge_UNVERIFIED'):
    lift_obj(nm, 'surface')
print('UG lifted', log)
# ---------- C) W walk 404 trim ----------
w = bpy.data.objects['TY_footway_313026404_to_Partridge_UNVERIFIED']
me4 = backup(w); mw = w.matrix_world; imw = mw.inverted()
XCUT = -102.15; ZG = 138.59
bm = bmesh.new(); bm.from_mesh(me4)
kill = [f for f in bm.faces if (mw @ f.calc_center_median()).x > XCUT + 0.05]
bmesh.ops.delete(bm, geom=kill, context='FACES')
cols = {}
for v in bm.verts:
    p = mw @ v.co; k = (round(p.x / 0.03), round(p.y / 0.03)); cols[k] = max(cols.get(k, -1e9), p.z)
nmv = 0
for v in bm.verts:
    p = mw @ v.co
    if p.x > -105.5:
        top = cols[(round(p.x / 0.03), round(p.y / 0.03))]
        is_top = abs(p.z - top) < 1e-4
        t = min(1, max(0, (p.x + 105.5) / 3.0))
        zt = top * (1 - t) + (ZG + 0.05) * t if top > ZG + 0.05 else top
        p.z = zt if is_top else zt - 0.28
        if p.x > XCUT: p.x = XCUT
        v.co = imw @ p; nmv += 1
bm.to_mesh(me4); bm.free(); me4.update()
print('UG walk404 deleted faces', len(kill), 'moved', nmv)
# ---------- D) E door 407 false flight -> flat landing ----------
L = bpy.data.objects['TY Partridge entrance steps+landings (UNVERIFIED)']
meL = backup(L); mw = L.matrix_world; imw = mw.inverted(); n7 = 0
for v in meL.vertices:
    p = mw @ v.co
    if -69.95 < p.x < -65.0 and 253.8 < p.y < 257.8 and p.z < 140.03:
        p.z = 140.08 if p.z >= 139.55 else 139.80
        v.co = imw @ p; n7 += 1
meL.update(); print('UG 407 verts', n7)
# ---------- cams ----------
def cam(name, loc, tgt, lens):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 6000
    o = bpy.data.objects.new(name, cd); col.objects.link(o); o['ug_obj'] = 1
    o.location = loc; o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
cam('UG_CAM_oblique_Partridge_E_seam_from_SE', (-20, 195, 178), (-62, 252, 140), 35)
cam('UG_CAM_eye_Partridge_E_face_from_E', (-50, 252.5, 141.8), (-68, 253.5, 141.2), 28)
cam('UG_CAM_eye_Partridge_W_steps_from_W', (-116, 246.5, 141.0), (-99, 250.5, 139.6), 30)
cam('UG_CAM_closeup_Partridge_E_seam_fill', (-56, 244, 142.6), (-64, 251, 139.8), 30)
json.dump(dict(xa=xa, xb=xb, patch_faces=nf, lifted=log, mat=mat.name), open(D + 'data/ug/ug_main.json', 'w'), indent=1)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

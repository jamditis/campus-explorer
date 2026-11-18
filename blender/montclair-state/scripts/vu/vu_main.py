# vu (Nov 7 2026 ~7:40 AM ET, MAIN, day 11 east dorms). ALL UNVERIFIED, reversible (REVERT=1).
# Priority A: Blanton first-floor spandrel band runs continuously through S/W door glass
# (TN_Blanton_spandrel_bands lowest islands straddle door 0 and door 2 at z~137.23–137.53).
# Fix: cut those bands out of each TJ door span (bisect + delete + fill), matching 1981 slide 1053
# where door openings interrupt the horizontal masonry/spandrel line. tu already cut block_base;
# this finishes the residual. Original spandrel mesh kept with fake user for revert.
import bpy, bmesh, os, json
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
DRY = os.environ.get('DRY') == '1'

def revert():
    # remove vu-tagged NEW objects (cams etc.); never delete mesh-swap targets
    for o in [o for o in bpy.data.objects if 'vu_obj' in o and 'vu_orig_mesh' not in o]:
        me = o.data
        bpy.data.objects.remove(o)
        if me and me.users == 0:
            if hasattr(me, 'vertices'):
                bpy.data.meshes.remove(me)
            elif hasattr(me, 'lens'):
                bpy.data.cameras.remove(me)
    for m in [m for m in bpy.data.materials if 'vu_mat' in m]:
        if m.users == 0:
            bpy.data.materials.remove(m)
    # restore spandrel mesh
    sp = bpy.data.objects.get('TN_Blanton_spandrel_bands_UNVERIFIED')
    if sp and 'vu_orig_mesh' in sp:
        new = sp.data
        sp.data = bpy.data.meshes[sp['vu_orig_mesh']]
        sp.data.use_fake_user = False
        del sp['vu_orig_mesh']
        if new.users == 0:
            bpy.data.meshes.remove(new)
    # restore block_base mesh if we also cut it
    bb = bpy.data.objects.get('TN_Blanton_block_base_UNVERIFIED')
    if bb and 'vu_orig_mesh' in bb:
        new = bb.data
        bb.data = bpy.data.meshes[bb['vu_orig_mesh']]
        bb.data.use_fake_user = False
        del bb['vu_orig_mesh']
        if new.users == 0:
            bpy.data.meshes.remove(new)
    c = bpy.data.collections.get('VU_Blanton_door_band_cut_UNVERIFIED')
    if c:
        bpy.data.collections.remove(c)
    print('VU reverted')

# Always clear any prior vu first (idempotent)
revert()
if REV:
    if SAVE:
        bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

def door_basis(k):
    G = bpy.data.objects['TJ_Blanton_entrance_%d_glass_UNVERIFIED' % k]
    gv = [G.matrix_world @ v.co for v in G.data.vertices]
    gc = sum(gv, Vector()) / len(gv)
    best = None
    for i in range(len(gv)):
        for j in range(i + 1, len(gv)):
            d = gv[j] - gv[i]; d.z = 0
            if best is None or d.length > best.length:
                best = d
    u = best.normalized(); n = Vector((-u.y, u.x, 0))
    BC = Vector((141.6, 450.4, 0))
    if (gc - BC).to_2d().dot(n.to_2d()) < 0:
        n = -n
    half_w = max(abs((v - gc).dot(u)) for v in gv)
    zlo = min(v.z for v in gv); zhi = max(v.z for v in gv)
    return gc, u, n, half_w, zlo, zhi

sc = bpy.context.scene
col = bpy.data.collections.new('VU_Blanton_door_band_cut_UNVERIFIED')
sc.collection.children.link(col)

SP = bpy.data.objects['TN_Blanton_spandrel_bands_UNVERIFIED']
orig = SP.data
nb = orig.copy(); nb.name = 'VU_Blanton_spandrel_bands_doorcut_UNVERIFIED'
orig.use_fake_user = True
SP['vu_orig_mesh'] = orig.name
SP.data = nb

bm = bmesh.new(); bm.from_mesh(nb)
bmi = SP.matrix_world.inverted()
mw = SP.matrix_world

log = {'doors': [], 'faces_deleted': 0, 'bisects': 0}

# Cut margin: door half-width + frame thickness (~0.12) + small pad
# Only cut bands that intersect the door glass z-range (first-floor spandrel ~137.2–137.5;
# also any band whose z overlaps glass — defensive).
for k in range(3):
    gc, u, n, half_w, zlo, zhi = door_basis(k)
    # opening half-width: glass + frame cheek
    half = half_w + 0.18
    # bisect planes at door jambs
    for sgn in (-1, 1):
        p = bmi @ (gc + u * half * sgn)
        no = (bmi.to_3x3() @ u).normalized()
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=p, plane_no=no, dist=1e-5)
        log['bisects'] += 1
    bm.faces.ensure_lookup_table()
    dl = []
    for f in bm.faces:
        c = mw @ f.calc_center_median()
        d = c - gc; d2 = Vector((d.x, d.y, 0))
        # inside door span horizontally, near wall plane, and overlapping door glass height
        # (lowest spandrel sits ~0.3–0.7 m above glass bottom)
        if abs(d2.dot(u)) < half and abs(d2.dot(n)) < 0.6 and (zlo - 0.15) <= c.z <= (zhi + 0.35):
            dl.append(f)
    n_del = len(dl)
    if dl:
        bmesh.ops.delete(bm, geom=dl, context='FACES')
    # fill boundary holes created by the cut
    edges = [e for e in bm.edges if e.is_boundary]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    log['doors'].append(dict(k=k, half=round(half, 3), z=[round(zlo, 3), round(zhi, 3)],
                             deleted=n_del, gc=[round(x, 2) for x in gc]))
    log['faces_deleted'] += n_del
    print('VU door', k, 'deleted', n_del, 'half', round(half, 3))

bm.to_mesh(nb); bm.free(); nb.update()
SP.data = nb

# Verify: no straddling lowest-band islands at door centers
bm2 = bmesh.new(); bm2.from_mesh(nb); bm2.verts.ensure_lookup_table()
seen = set(); remain_straddle = []
islands = []
for v in bm2.verts:
    if v.index in seen: continue
    st = [v]; isl = []; seen.add(v.index)
    while st:
        a = st.pop(); isl.append(a)
        for e in a.link_edges:
            b = e.other_vert(a)
            if b.index not in seen:
                seen.add(b.index); st.append(b)
    ws = [mw @ x.co for x in isl]
    z0 = min(p.z for p in ws); z1 = max(p.z for p in ws)
    islands.append((ws, z0, z1))
for k in range(3):
    gc, u, n, half_w, zlo, zhi = door_basis(k)
    for ws, z0, z1 in islands:
        if z1 > 139.5:  # only care about bands that can cross glass
            continue
        if z0 > zhi + 0.2:
            continue
        dus = [(p - gc).dot(u) for p in ws]
        dns = [(p - gc).dot(n) for p in ws]
        if min(dus) < -0.05 and max(dus) > 0.05 and abs(sum(dns) / len(dns)) < 1.5:
            remain_straddle.append(dict(k=k, z=[round(z0, 2), round(z1, 2)],
                                        du=[round(min(dus), 2), round(max(dus), 2)]))
bm2.free()
log['remain_straddle'] = remain_straddle
print('VU remain_straddle', remain_straddle)

# Cameras for WIP: reuse TU closeup + W eye + oblique east dorms + new detail cam on door 0 band cut
def ensure_cam(name, loc, target, lens=32):
    existing = bpy.data.objects.get(name)
    if existing:
        return existing
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 30000
    co = bpy.data.objects.new(name, cd); col.objects.link(co)
    co['vu_obj'] = 1; co['UNVERIFIED'] = 'vu WIP camera'
    co.location = loc
    d = target - loc
    co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return co

# door 0 close-up slightly lower to show band cut at lower third of glass
gc0, u0, n0, hw0, zlo0, zhi0 = door_basis(0)
# ground hit approx
loc = gc0 + n0 * 11 + u0 * (-3.5); loc.z = zlo0 + 1.35
ensure_cam('VU_CAM_closeup_Blanton_S_door_bandcut', loc, gc0 + Vector((0, 0, 1.1)), lens=35)
# door 2 (W) eye
gc2, u2, n2, hw2, zlo2, zhi2 = door_basis(2)
loc2 = gc2 + n2 * 14 + u2 * (-5); loc2.z = zlo2 + 1.55
ensure_cam('VU_CAM_eye_Blanton_W_door_bandcut', loc2, gc2 + Vector((0, 0, 1.6)), lens=28)

# mark spandrel
SP['UNVERIFIED'] = (SP.get('UNVERIFIED') or '') + ' | vu: first-floor spandrel cut at S/W door spans so door interrupts band (slide 1053)'

json.dump(log, open('/workspace/nj-scenes/montclair-state/data/vu/apply_log.json', 'w'), indent=1)
print('VU log', json.dumps(log))

if DRY:
    print('DRY — not saving')
else:
    if SAVE:
        bpy.ops.wm.save_mainfile(); print('SAVED')

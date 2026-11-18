# vw (Nov 7 2026, MAIN, day 11): Bohn Hall W-face punched recessed eggcrate windows
# from Digital Commons slides 1251 (1971) + 1519 (1975). ALL UNVERIFIED.
# Proud eggcrate overlay (piers/bands outward; glass near wall face) — solid TL/TK masses
# cannot host true interior cuts without boolean. Glass opaque-reflective (Joe Nov 6).
# REVERT=1 strips vw objs; vw_revert_all.sh restores pre-vw backup (REVERT_EXACT).
import bpy, bmesh, os, json, math
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
ROOT = '/workspace/nj-scenes/montclair-state'
OUT = ROOT + '/data/vw'
os.makedirs(OUT, exist_ok=True)
CN = 'VW_Bohn_W_face_windows_UNVERIFIED'
NOTE = ('Bohn W-face recessed eggcrate after MSU Digital Commons slides 1251/1519; '
        'column counts/pier/window/recess widths UNVERIFIED; opaque-reflective glass; '
        'proud overlay on solid massing (no boolean cut)')

BAY = 2.95
PIER_W = 0.48
BAND_H = 0.42
DEPTH = 0.40          # pier outer face proud of wall (= recess depth read)
GLASS_T = 0.04
GLASS_OFF = 0.015     # glass just outside wall face (not inside solid)
FLOOR = 2.75
MARGIN_Z = 0.12
MARGIN_T = 0.10

def remove_obj(o):
    me = o.data; t = o.type
    bpy.data.objects.remove(o, do_unlink=True)
    if me and me.users == 0:
        if t == 'MESH': bpy.data.meshes.remove(me)
        elif t == 'CAMERA': bpy.data.cameras.remove(me)

def revert():
    for o in [o for o in list(bpy.data.objects) if o.get('vw_obj')]:
        remove_obj(o)
    for m in [m for m in list(bpy.data.materials) if m.get('vw_mat')]:
        bpy.data.materials.remove(m)
    c = bpy.data.collections.get(CN)
    if c: bpy.data.collections.remove(c)
    print('VW REVERTED')

if REV:
    revert()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

revert()

def mat(name, rgb, rough=0.85, metal=0.0, spec=0.4, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vw_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    try: b.inputs['Specular IOR Level'].default_value = spec
    except Exception: pass
    try:
        b.inputs['Coat Weight'].default_value = coat
        b.inputs['Coat Roughness'].default_value = 0.08
    except Exception: pass
    try: b.inputs['Alpha'].default_value = 1.0
    except Exception: pass
    try: b.inputs['Transmission Weight'].default_value = 0.0
    except Exception: pass
    return m

M_CONC = mat('VW_Bohn_W_concrete_UNVERIFIED', (0.46, 0.42, 0.36), rough=0.88, spec=0.22)
M_GLASS = mat('VW_Bohn_W_glass_opaque_reflective_UNVERIFIED', (0.05, 0.07, 0.09),
              rough=0.05, metal=0.28, spec=1.05, coat=1.0)
M_REVEAL = mat('VW_Bohn_W_reveal_UNVERIFIED', (0.10, 0.09, 0.08), rough=0.75, spec=0.18)

sc = bpy.context.scene
col = bpy.data.collections.new(CN); sc.collection.children.link(col); col['vw_obj'] = 1

class MB:
    def __init__(s, name, mats):
        s.bm = bmesh.new(); s.name = name; s.mats = mats
    def box2(s, c, u, n, w, d0, d1, z0, z1, mi=0):
        u = Vector((u.x, u.y, 0)).normalized()
        n = Vector((n.x, n.y, 0)).normalized()
        cxy = Vector((c.x, c.y, 0))
        corners = []
        for z in (z0, z1):
            for a, dd in ((-1, d0), (1, d0), (1, d1), (-1, d1)):
                p = cxy + u * (a * w / 2) + n * dd
                corners.append(s.bm.verts.new((p.x, p.y, z)))
        faces = ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                 (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7))
        for f in faces:
            try: s.bm.faces.new([corners[i] for i in f]).material_index = mi
            except ValueError: pass
    def done(s):
        bmesh.ops.recalc_face_normals(s.bm, faces=s.bm.faces)
        me = bpy.data.meshes.new(s.name); s.bm.to_mesh(me); s.bm.free()
        for m in s.mats: me.materials.append(m)
        o = bpy.data.objects.new(s.name, me); col.objects.link(o)
        o['vw_obj'] = 1; o['UNVERIFIED'] = NOTE
        for p in me.polygons: p.use_smooth = False
        return o

targets = []
for o in bpy.data.objects:
    if o.type != 'MESH' or o.hide_render: continue
    if not (o.name.startswith('TL_Bohn_Hall_') or o.name == 'TK_Bohn_Hall_232853538_base_UNVERIFIED'):
        continue
    if 'PH' in o.name: continue
    me = o.data; mw = o.matrix_world
    if 'ti_dir' not in me.attributes: continue
    z0g = me.attributes['ti_z0'].data[0].value
    for pi, p in enumerate(me.polygons):
        n = (mw.to_3x3() @ p.normal).normalized()
        if abs(n.z) > 0.5 or n.x > -0.70: continue
        z1a = me.attributes['ti_z1'].data[pi].value
        if abs(z1a - z0g) < 1.0: continue  # blank-end / stair return
        d = me.attributes['ti_dir'].data[pi].vector
        U = Vector((d.x, d.y, 0)).normalized()
        N = Vector((n.x, n.y, 0)).normalized()
        if abs(U.dot(N)) > 0.3:
            U = Vector((-N.y, N.x, 0)).normalized()
        if U.y < 0: U = -U
        verts = [mw @ me.vertices[i].co for i in p.vertices]
        ts = [v.x * U.x + v.y * U.y for v in verts]
        zs = [v.z for v in verts]
        t0, t1 = min(ts), max(ts)
        width = t1 - t0
        if width < 5.5: continue
        z0v, z1v = min(zs), max(zs)
        if z1v - z0v < 2.0: continue
        cx = sum(v.x for v in verts) / len(verts)
        cy = sum(v.y for v in verts) / len(verts)
        if abs(cx - 204.7) < 6 and abs(cy - 384.4) < 8:
            ncols, tag = 4, 'west_tower'
        elif width >= 18:
            ncols, tag = max(2, int(round(width / BAY))), 'mid_step'
        else:
            ncols, tag = max(2, int(round(width / BAY))), ('wide' if width >= 10 else 'narrow')
        targets.append(dict(
            mesh=o.name, cx=cx, cy=cy, n=N.copy(), u=U.copy(),
            t0=t0, t1=t1, width=width, z0=z0v, z1=z1v, ncols=ncols, tag=tag,
            face_c=Vector((cx, cy, (z0v + z1v) / 2))
        ))

targets = sorted(targets, key=lambda t: (-t['width'], t['cx'], t['cy']))
kept = []
for t in targets:
    if any(abs(t['cx'] - k['cx']) < 1.0 and abs(t['cy'] - k['cy']) < 1.0
           and abs(t['z0'] - k['z0']) < 1.0 for k in kept):
        continue
    kept.append(t)
targets = kept

log = {'session': 'vw', 'n_targets': len(targets), 'targets': [], 'n_bays': 0, 'n_floors_cells': 0,
       'approach': 'proud_eggcrate_overlay'}

mb_pier = MB('VW_Bohn_W_piers_bands_UNVERIFIED', [M_CONC])
mb_rev = MB('VW_Bohn_W_reveals_UNVERIFIED', [M_REVEAL])
mb_gl = MB('VW_Bohn_W_glass_UNVERIFIED', [M_GLASS])

for t in targets:
    U, N = t['u'], t['n']
    t0, t1 = t['t0'] + MARGIN_T, t['t1'] - MARGIN_T
    width = t1 - t0
    ncols = t['ncols']
    bay = width / ncols
    z_lo = t['z0'] + MARGIN_Z
    z_hi = t['z1'] - MARGIN_Z
    n_storeys = max(1, int(round((z_hi - z_lo) / FLOOR)))
    t_ref = t['face_c'].x * U.x + t['face_c'].y * U.y
    def at(tt):
        return Vector((t['face_c'].x, t['face_c'].y, 0)) + U * (tt - t_ref)

    # Vertical piers (outer face at +DEPTH)
    for i in range(ncols + 1):
        tt = t0 + i * bay
        c = at(tt)
        mb_pier.box2(c, U, N, PIER_W, -0.01, DEPTH, z_lo, z_hi, 0)

    # Horizontal bands
    storey_h = (z_hi - z_lo) / n_storeys
    for s_i in range(n_storeys + 1):
        if s_i == 0:
            z0b, z1b = z_lo, z_lo + BAND_H
        elif s_i == n_storeys:
            z0b, z1b = z_hi - BAND_H, z_hi
        else:
            zc = z_lo + s_i * storey_h
            z0b, z1b = zc - BAND_H / 2, zc + BAND_H / 2
        c = at((t0 + t1) / 2)
        mb_pier.box2(c, U, N, width + PIER_W * 0.5, -0.01, DEPTH, z0b, z1b, 0)

    cells = 0
    for i in range(ncols):
        tt = t0 + (i + 0.5) * bay
        c = at(tt)
        win_w = bay - PIER_W - 0.06
        if win_w < 0.55: continue
        for s_i in range(n_storeys):
            z0s = z_lo + s_i * storey_h
            z1s = z_lo + (s_i + 1) * storey_h
            z0w = z0s + BAND_H + 0.03
            z1w = z1s - BAND_H - 0.03
            if z1w - z0w < 0.75: continue
            # dark reveal tray: from near-wall to pier outer (sides of the eggcrate cell)
            mb_rev.box2(c, U, N, win_w + 0.05, GLASS_OFF, DEPTH - 0.01, z0w - 0.02, z1w + 0.02, 0)
            # opaque-reflective glass near wall face (visible, appears deep in cell)
            mb_gl.box2(c, U, N, win_w, GLASS_OFF, GLASS_OFF + GLASS_T, z0w, z1w, 0)
            cells += 1
    log['targets'].append(dict(
        mesh=t['mesh'], tag=t['tag'], cx=round(t['cx'], 2), cy=round(t['cy'], 2),
        width=round(t['width'], 2), z0=round(t['z0'], 2), z1=round(t['z1'], 2),
        ncols=ncols, bay=round(bay, 3), n_storeys=n_storeys, cells=cells
    ))
    log['n_bays'] += ncols
    log['n_floors_cells'] += cells

o1 = mb_pier.done(); o2 = mb_rev.done(); o3 = mb_gl.done()
print('VW piers/bands', len(o1.data.polygons), 'reveals', len(o2.data.polygons), 'glass', len(o3.data.polygons))

def place_cam(name, loc, tgt, lens=28):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 30000
    o = bpy.data.objects.new(name, cd); col.objects.link(o); o['vw_obj'] = 1
    o.location = loc
    d = Vector(tgt) - Vector(loc)
    o.rotation_euler = (math.pi / 2 + math.atan2(d.z, math.hypot(d.x, d.y)), 0,
                        math.atan2(d.y, d.x) - math.pi / 2)
    return o

def gz(x, y):
    dg = bpy.context.evaluated_depsgraph_get()
    for gn in ('Terrain_LiDAR_DTM_1m', 'Context_skirt_3DEP_ortho_4km'):
        go = bpy.data.objects.get(gn)
        if not go: continue
        e = go.evaluated_get(dg); iw = go.matrix_world.inverted()
        r = e.ray_cast(iw @ Vector((x, y, 400)), (iw.to_3x3() @ Vector((0, 0, -1))).normalized())
        if r[0]: return (go.matrix_world @ r[1]).z
    return 130.0

ge = gz(165, 395)
place_cam('VW_CAM_eye_Bohn_W_face', (168, 392, ge + 1.7), (204.7, 384.4, ge + 18), 24)
gc = gz(185, 378)
place_cam('VW_CAM_closeup_Bohn_W_grid', (190, 378, gc + 10), (204.7, 384.4, gc + 18), 35)
gs = gz(175, 350)
place_cam('VW_CAM_eye_Bohn_from_SW', (178, 348, gs + 4), (215, 375, gs + 22), 28)

log['n_objs_after'] = len(bpy.data.objects)
json.dump(log, open(OUT + '/apply.json', 'w'), indent=2)
print('VW targets', len(targets), 'cells', log['n_floors_cells'], 'objs', log['n_objs_after'])
for t in log['targets']:
    print(' ', t)

if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')

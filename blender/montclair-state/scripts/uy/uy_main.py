"""Session uy (Nov 6 2026 ~10:30–~11:12 AM ET, MAIN, day-10 Freeman continue).

Fixes + extensions on uv/uw Freeman Hall overlays (UNVERIFIED):
  A) Lettering: restore GRACE H. FREEMAN HALL (uw M was wrong; photo 1096 + uv intent = H)
  B) Orange bay: rebuild as THREE tall terracotta panels under upper 2×3 clear glass
     (not uw's 2×3 six orange panels)
  C) Cream brick: thin proud overlays on blank W/S shell (+ N wing remainder) so mass
     does not read white stucco next to photo overlays; do NOT destroy ub/uc walls
  D) West recessed vertical windows (OSM edge 1, pitch ~3.6 m UNVERIFIED from 1114);
     light S-face rhythm (edge 3) without inventing doors
  E) Optional: 1–3 roof RTU boxes on LiDAR roof (UNVERIFIED)
  F) UY cams for W face + lettering/orange close-up

REVERT=1 removes uy_obj / uy_mat / UY_* collections and restores lettering body/name
from uy_letter_orig_* if set. Mesh replacements of the orange bay: uy restores by
deleting uy-tagged bay and re-running is NOT automatic — uy_revert_all.sh strips uy
then leaves uw/uv chain for caller. For orange bay uy replaces in place under same
object name tagged uy_obj+uv_obj; REVERT removes uy bay so caller should re-run
uw_revert_all (which re-applies uv) OR uy stores uw bay SIG note.

Safer approach: on apply, hide (not delete) prior bay mesh under uy_hid_prev; on
REVERT unhide and remove uy replacements.

Tag uy_obj / uy_mat; collections UY_*_UNVERIFIED.
SAVE=1 saves mainfile.
"""
import bpy, bmesh, os, json, math
from mathutils import Vector, Matrix

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/uy'
os.makedirs(DATA, exist_ok=True)
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
TOPZ = 147.05
ROOFZ = 147.023
OUT = 0.08

COL_SHELL = 'UY_Freeman_cream_shell_UNVERIFIED'
COL_SIDE = 'UY_Freeman_W_S_windows_1114_UNVERIFIED'
COL_ROOF = 'UY_Freeman_roof_RTU_UNVERIFIED'
COL_CAM = 'UY_Freeman_cams'
COL_ENT = 'UV_Freeman_entrance_1096_UNVERIFIED'

def ensure_coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

def remove_obj(o):
    if o is None: return
    me = o.data; t = o.type
    bpy.data.objects.remove(o, do_unlink=True)
    if me is not None and me.users == 0:
        if t == 'MESH': bpy.data.meshes.remove(me)
        elif t == 'CAMERA': bpy.data.cameras.remove(me)
        elif t in ('FONT', 'CURVE'):
            try: bpy.data.curves.remove(me)
            except Exception: pass

def revert():
    # unhide prior objects hidden by uy
    for o in bpy.data.objects:
        if o.get('uy_hid_prev'):
            o.hide_set(False); o.hide_render = False
            del o['uy_hid_prev']
    for o in [o for o in list(bpy.data.objects) if o.get('uy_obj')]:
        remove_obj(o)
    for m in [m for m in list(bpy.data.materials) if m.get('uy_mat')]:
        bpy.data.materials.remove(m)
    # restore lettering if we stashed
    for o in bpy.data.objects:
        if o.type == 'FONT' and o.get('uy_letter_orig_body') is not None:
            o.data.body = o['uy_letter_orig_body']
            if o.get('uy_letter_orig_name'):
                try: o.name = o['uy_letter_orig_name']
                except Exception: pass
            del o['uy_letter_orig_body']
            if 'uy_letter_orig_name' in o: del o['uy_letter_orig_name']
    for c in (COL_SHELL, COL_SIDE, COL_ROOF, COL_CAM):
        col = bpy.data.collections.get(c)
        if col: bpy.data.collections.remove(col)
    print('UY REVERTED')

if REV:
    revert()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# clear any prior uy apply (idempotent)
revert()

log = {'session': 'uy', 'fixes': [], 'GR': GR}

def mat(name, rgb, rough=0.85, metal=0.0, spec=0.5, alpha=1.0, noise=0.0, brick=False, brick_mortar=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['uy_mat'] = 1
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    try: b.inputs['Specular IOR Level'].default_value = spec
    except Exception: pass
    if alpha < 1.0:
        m.blend_method = 'HASHED'
        try: b.inputs['Alpha'].default_value = alpha
        except Exception: pass
    if brick:
        t = nt.nodes.new('ShaderNodeTexBrick')
        t.inputs['Color1'].default_value = (*rgb, 1)
        t.inputs['Color2'].default_value = (rgb[0]*0.88, rgb[1]*0.86, rgb[2]*0.82, 1)
        mort = brick_mortar or (0.50, 0.46, 0.40)
        t.inputs['Mortar'].default_value = (*mort, 1)
        t.inputs['Brick Width'].default_value = 0.21
        t.inputs['Row Height'].default_value = 0.065
        t.inputs['Mortar Size'].default_value = 0.009
        t.inputs['Scale'].default_value = 1.0
        tc = nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(tc.outputs['Object'], t.inputs['Vector'])
        nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    elif noise:
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 2.2; n.inputs['Detail'].default_value = 6
        r = nt.nodes.new('ShaderNodeValToRGB')
        r.color_ramp.elements[0].color = (rgb[0]*(1-noise), rgb[1]*(1-noise), rgb[2]*(1-noise), 1)
        r.color_ramp.elements[1].color = (*rgb, 1)
        nt.links.new(n.outputs['Fac'], r.inputs['Fac']); nt.links.new(r.outputs['Color'], b.inputs['Base Color'])
    else:
        b.inputs['Base Color'].default_value = (*rgb, 1)
    return m

def find_mat(substr, fallback_rgb, uy=False):
    for m in bpy.data.materials:
        if substr in m.name and (m.get('uv_mat') or m.get('uy_mat') or m.get('uw_mat')):
            return m
    return mat('UY_tmp_' + substr, fallback_rgb)

M = dict(
    brick=mat('UY_Freeman_cream_brick_shell_UNVERIFIED', (0.72, 0.66, 0.54), 0.9, brick=True, brick_mortar=(0.50, 0.46, 0.40)),
    terracotta=mat('UY_Freeman_terracotta_panel_UNVERIFIED', (0.70, 0.30, 0.12), 0.62, 0.05, noise=0.08),
    glass=find_mat('curtain_glass', (0.55, 0.62, 0.68)) or mat('UY_Freeman_glass_UNVERIFIED', (0.55, 0.62, 0.68), 0.05, alpha=0.35),
    white=find_mat('white_frame', (0.92, 0.92, 0.90)) or mat('UY_Freeman_white_UNVERIFIED', (0.92, 0.92, 0.90), 0.45, 0.15),
    dark=find_mat('window_frame_darkred', (0.28, 0.10, 0.07)) or mat('UY_Freeman_darkframe_UNVERIFIED', (0.22, 0.10, 0.08), 0.5, 0.2),
    spandrel=mat('UY_Freeman_spandrel_reddish_UNVERIFIED', (0.55, 0.22, 0.14), 0.7, 0.05),
    rtu=mat('UY_Freeman_RTU_metal_UNVERIFIED', (0.45, 0.45, 0.43), 0.55, 0.35, noise=0.1),
    letter=find_mat('lettering_dark', (0.05, 0.05, 0.05)),
)

class MB:
    def __init__(s, name, mats, coll):
        s.bm = bmesh.new(); s.name = name; s.mats = mats; s.coll = coll
    def box(s, c, u, n, w, dep, z0, z1, mi=0):
        u = Vector((u[0], u[1], 0)).normalized()
        n = Vector((n[0], n[1], 0)).normalized()
        c = Vector((c[0], c[1], 0))
        vs = []
        for z in (z0, z1):
            for a, b_ in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                p = c + u * (a * w / 2) + n * (b_ * dep / 2)
                vs.append(s.bm.verts.new((p.x, p.y, z)))
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            try: s.bm.faces.new([vs[i] for i in f]).material_index = mi
            except ValueError: pass
    def done(s, tag='uy'):
        bmesh.ops.recalc_face_normals(s.bm, faces=s.bm.faces)
        me = bpy.data.meshes.new(s.name); s.bm.to_mesh(me); s.bm.free()
        for m in s.mats: me.materials.append(m)
        o = bpy.data.objects.new(s.name, me); s.coll.objects.link(o)
        o['uy_obj'] = 1
        o['UNVERIFIED'] = 'uy Freeman Hall day-10; sizes UNVERIFIED; photo 1096/1114'
        for p in me.polygons: p.use_smooth = False
        return o

# ---------- A) Lettering H restore ----------
let = None
for o in bpy.data.objects:
    if o.type == 'FONT' and ('FREEMAN' in o.name.upper() or (hasattr(o.data, 'body') and 'FREEMAN' in (o.data.body or '').upper())):
        let = o; break
if let:
    # stash current (wrong M) so REVERT can put M back if needed — actually we WANT H permanently
    # overwriting uw mistake; still stash for REVERT to prior body
    let['uy_letter_orig_body'] = let.data.body
    let['uy_letter_orig_name'] = let.name
    let.data.body = 'GRACE H. FREEMAN HALL'
    try:
        let.name = 'UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED'
    except Exception:
        pass
    # clear uw backup so uw REVERT won't re-force M later incorrectly after uy
    if 'uw_letter_orig_body' in let:
        del let['uw_letter_orig_body']
    if 'uw_letter_orig_name' in let:
        del let['uw_letter_orig_name']
    if let.data.size < 0.45:
        let.data.size = 0.48
    log['fixes'].append('lettering_M_to_H')
    log['lettering'] = let.data.body
else:
    log['fixes'].append('lettering_MISSING')

# ---------- B) Orange bay → 3 terracotta + upper 2×3 glass ----------
e6 = [e for e in OSM['edges'] if e['i'] == 6][0]
U = Vector((e6['u'][0], e6['u'][1], 0)).normalized()
N = Vector((e6['n'][0], e6['n'][1], 0)).normalized()
A = Vector((e6['a'][0], e6['a'][1], 0))
FACE_LEN = e6['len']
T_WIN0, T_WIN1 = 3.35, 6.55
# prefer measured span from existing bay
ob_win = bpy.data.objects.get('UV_Freeman_N_orange_panel_window_bay_UNVERIFIED')
def span_of(obj, origin, uvec):
    if not obj or obj.type != 'MESH' or not obj.data.vertices: return None
    ts = sorted((obj.matrix_world @ Vector(v.co) - origin).dot(uvec) for v in obj.data.vertices)
    return ts[0], ts[-1]
sp = span_of(ob_win, A, U)
if sp:
    T_WIN0, T_WIN1 = sp
log['win_span'] = [T_WIN0, T_WIN1]

col_ent = bpy.data.collections.get(COL_ENT) or ensure_coll(COL_ENT)
if ob_win:
    ob_win.hide_set(True); ob_win.hide_render = True
    ob_win['uy_hid_prev'] = 1
    log['fixes'].append('hid_uw_orange_bay')

ww = T_WIN1 - T_WIN0
wc = A + U * ((T_WIN0 + T_WIN1) / 2)
# mats: 0 white, 1 glass, 2 terracotta, 3 brick
mw = MB('UY_Freeman_N_terracotta_3panel_window_bay_UNVERIFIED',
        [M['white'], M['glass'], M['terracotta'], M['brick']], col_ent)
mw.box(wc + N * (OUT + 0.10), U, N, ww, 0.28, GR - 0.05, TOPZ - 0.15, 3)
n_cols = 3
pane_w = (ww - 0.25) / n_cols
# lower: THREE solid terracotta panels (tall ~1×3 proportion under glass)
terr_z0, terr_z1 = GR + 0.45, GR + 4.50
# upper glass: 2 rows × 3 cols
glass_mid = GR + 4.65
glass_top = TOPZ - 0.6
glass_split = (glass_mid + glass_top) / 2
for i in range(n_cols):
    pc = A + U * (T_WIN0 + 0.12 + pane_w * (i + 0.5))
    # terracotta panel
    mw.box(pc + N * (OUT + 0.18), U, N, pane_w - 0.08, 0.08, terr_z0, terr_z1, 2)
    # upper glass row 0 + row 1
    mw.box(pc + N * (OUT + 0.18), U, N, pane_w - 0.08, 0.06, glass_mid, glass_split - 0.04, 1)
    mw.box(pc + N * (OUT + 0.18), U, N, pane_w - 0.08, 0.06, glass_split + 0.04, glass_top, 1)
    if i < n_cols - 1:
        mc = A + U * (T_WIN0 + 0.12 + pane_w * (i + 1))
        mw.box(mc + N * (OUT + 0.20), U, N, 0.08, 0.10, GR + 0.35, TOPZ - 0.55, 0)
# frame rails
mw.box(wc + N * (OUT + 0.22), U, N, ww - 0.15, 0.05, GR + 0.35, GR + 0.50, 0)
mw.box(wc + N * (OUT + 0.22), U, N, ww - 0.15, 0.05, terr_z1, glass_mid, 0)
mw.box(wc + N * (OUT + 0.22), U, N, ww - 0.15, 0.05, glass_split - 0.04, glass_split + 0.04, 0)
mw.box(wc + N * (OUT + 0.22), U, N, ww - 0.15, 0.05, TOPZ - 0.70, TOPZ - 0.55, 0)
ob_new = mw.done()
# also keep in uv revert chain? No — uy-only; hid prev restores on uy revert
log['fixes'].append('orange_bay_3_terracotta_plus_2x3_glass')

# ---------- C) Cream brick shell overlays (W edge1, S edge3, N remainder hints) ----------
col_shell = ensure_coll(COL_SHELL)
shell_built = 0
for ei, label in ((1, 'W'), (3, 'S'), (6, 'N_remainder')):
    e = [ed for ed in OSM['edges'] if ed['i'] == ei][0]
    Ue = Vector((e['u'][0], e['u'][1], 0)).normalized()
    Ne = Vector((e['n'][0], e['n'][1], 0)).normalized()
    Ae = Vector((e['a'][0], e['a'][1], 0))
    Le = e['len']
    # skip University Hall side — UH is east of Freeman; W is edge1 (away from UH). OK.
    # For N face: only cover zones NOT already under lettering/window/entrance/screen
    #   i.e. thin strips near ends only, or skip heavy N (entrance overlays cover)
    if ei == 6:
        # thin filler strips at extreme east tip only if any gap — skip full N to avoid clash
        continue
    # proud thin brick skin full face height
    dep = 0.06
    # leave small margins at ends so corners don't double-stack
    margin = 0.35
    usable = Le - 2 * margin
    if usable < 2.0:
        continue
    # one continuous panel (reads as cream brick mass)
    mid = Ae + Ue * (Le / 2)
    mb = MB(f'UY_Freeman_{label}_cream_brick_skin_UNVERIFIED', [M['brick']], col_shell)
    mb.box(mid + Ne * (OUT + 0.04), Ue, Ne, usable, dep, GR - 0.02, TOPZ - 0.12, 0)
    mb.done()
    shell_built += 1
log['cream_shell_faces'] = shell_built
log['fixes'].append('cream_brick_W_S_skins')

# ---------- D) West recessed vertical windows (edge 1) + light S (edge 3) ----------
col_side = ensure_coll(COL_SIDE)
pitch = 3.6  # UNVERIFIED from 1114
built_w = 0
e1 = [ed for ed in OSM['edges'] if ed['i'] == 1][0]
U1 = Vector((e1['u'][0], e1['u'][1], 0)).normalized()
N1 = Vector((e1['n'][0], e1['n'][1], 0)).normalized()
A1 = Vector((e1['a'][0], e1['a'][1], 0))
L1 = e1['len']
msw = MB('UY_Freeman_W_recessed_vertical_windows_UNVERIFIED',
         [M['dark'], M['glass'], M['spandrel'], M['brick']], col_side)
n_bays = max(1, int((L1 - 4.0) / pitch))
for i in range(n_bays):
    t = 2.0 + pitch * (i + 0.5)
    if t > L1 - 2.0: break
    c = A1 + U1 * t
    # recessed dark frame strip
    msw.box(c + N1 * (OUT - 0.12), U1, N1, 1.15, 0.30, GR + 0.8, TOPZ - 0.4, 0)
    # stacked glass + reddish spandrels alternating
    bands = [
        (GR+1.0, GR+3.4, 1), (GR+3.4, GR+3.85, 2),
        (GR+3.85, GR+6.25, 1), (GR+6.25, GR+6.7, 2),
        (GR+6.7, GR+9.1, 1), (GR+9.1, GR+9.55, 2),
        (GR+9.55, GR+11.95, 1), (GR+11.95, GR+12.4, 2),
        (GR+12.4, TOPZ-0.55, 1),
    ]
    for z0, z1, mi in bands:
        if z1 <= z0: continue
        msw.box(c + N1 * (OUT - 0.05), U1, N1, 0.95, 0.06, z0, z1, mi)
    built_w += 1
msw.done()
log['west_window_bays'] = built_w
log['fixes'].append('W_recessed_windows_edge1')

# South face short rhythm (edge 3) — windows only, no doors
built_s = 0
e3 = [ed for ed in OSM['edges'] if ed['i'] == 3][0]
U3 = Vector((e3['u'][0], e3['u'][1], 0)).normalized()
N3 = Vector((e3['n'][0], e3['n'][1], 0)).normalized()
A3 = Vector((e3['a'][0], e3['a'][1], 0))
L3 = e3['len']
mss = MB('UY_Freeman_S_recessed_vertical_windows_UNVERIFIED',
         [M['dark'], M['glass'], M['spandrel']], col_side)
# fewer bays on short S face
for i, t in enumerate([3.5, 7.5, 11.5]):
    if t > L3 - 1.5: break
    c = A3 + U3 * t
    mss.box(c + N3 * (OUT - 0.12), U3, N3, 1.10, 0.28, GR + 0.8, TOPZ - 0.4, 0)
    for z0, z1, mi in [(GR+1.0, GR+4.0, 1), (GR+4.0, GR+4.5, 2), (GR+4.5, GR+8.0, 1),
                       (GR+8.0, GR+8.5, 2), (GR+8.5, TOPZ-0.6, 1)]:
        mss.box(c + N3 * (OUT - 0.05), U3, N3, 0.90, 0.06, z0, z1, mi)
    built_s += 1
mss.done()
log['south_window_bays'] = built_s
log['fixes'].append('S_recessed_windows_edge3')

# ---------- E) Optional roof RTUs (1–3) ----------
col_roof = ensure_coll(COL_ROOF)
roof = bpy.data.objects.get('Freeman Hall roof (LiDAR)')
rtu_n = 0
if roof:
    # place 3 boxes along roof centerline roughly mid-mass (UNVERIFIED from aerial language)
    # roof footprint mid ~ (-91.7, -196.4)
    mids = [
        Vector((-88.0, -185.0, ROOFZ)),
        Vector((-92.0, -198.0, ROOFZ)),
        Vector((-96.0, -210.0, ROOFZ)),
    ]
    mr = MB('UY_Freeman_roof_RTU_boxes_UNVERIFIED', [M['rtu']], col_roof)
    for i, c in enumerate(mids):
        # local axes: along building long = edge1 u roughly south
        u = Vector((-0.23, -0.97, 0)).normalized()
        n = Vector((-0.97, 0.23, 0)).normalized()
        h = 1.1 + 0.15 * i
        mr.box(c, u, n, 2.4, 1.6, ROOFZ + 0.02, ROOFZ + 0.02 + h, 0)
        rtu_n += 1
    mr.done()
    log['fixes'].append(f'roof_RTU_x{rtu_n}')
log['rtu_count'] = rtu_n

# ---------- F) Cameras ----------
cc = ensure_coll(COL_CAM)
def add_cam(name, loc, target, lens=32):
    existing = bpy.data.objects.get(name)
    if existing and existing.get('uy_obj'):
        remove_obj(existing)
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 5000
    o = bpy.data.objects.new(name, cd); cc.objects.link(o); o['uy_obj'] = 1
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return o

MID = A + U * (FACE_LEN / 2)
# reuse UV oblique + eye N as overview / eye1; add UY W eye + lettering/bay closeup
add_cam('UY_CAM_oblique_Freeman_from_NW',
        (MID.x - 38, MID.y + 32, GR + 26),
        (MID.x - 8, MID.y - 20, GR + 8), 28)
add_cam('UY_CAM_eye_Freeman_W_side',
        (A1.x + N1.x * 20 + U1.x * L1 * 0.40,
         A1.y + N1.y * 20 + U1.y * L1 * 0.40, GR + 1.7),
        (A1.x + U1.x * L1 * 0.40, A1.y + U1.y * L1 * 0.40, GR + 8), 30)
# lettering + terracotta bay close-up (from N lawn, slightly east of doors)
bay_c = A + U * ((T_WIN0 + T_WIN1) / 2)
add_cam('UY_CAM_closeup_Freeman_N_lettering_terracotta',
        (bay_c.x + N.x * 7.5 - U.x * 1.2, bay_c.y + N.y * 7.5 - U.y * 1.2, GR + 2.2),
        (bay_c.x, bay_c.y, GR + 6.5), 40)
# keep UV N entrance eye as second eye-level
log['cams'] = [o.name for o in cc.objects]

log['n_objects'] = len(bpy.data.objects)
log['n_uy_obj'] = sum(1 for o in bpy.data.objects if o.get('uy_obj'))
log['n_uv_obj'] = sum(1 for o in bpy.data.objects if o.get('uv_obj'))
log['n_uw_obj'] = sum(1 for o in bpy.data.objects if o.get('uw_obj'))
json.dump(log, open(DATA + '/uy_main.json', 'w'), indent=2)
print('UY MAIN', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')

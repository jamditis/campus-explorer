"""2026-10-14 ~8:20 PM ET, tag 20261014aa.
One-pass CCOM polish: east lounge exterior readability + equipment entrance tone match.
Maps eye notes (data/ccom_equip_entry/maps_eye_20261014aa.txt): pin at Life/Morehead, no SV —
cannot confirm doors/platform; keep Joe facts (1 roll-up + personnel right, small platform).
RERUNNABLE. --save to write."""
import bpy, bmesh, math, sys, shutil, os
from mathutils import Vector

SAVE = '--save' in sys.argv
TAG = '20261014aa'
# reuse world frame from jf
P0 = Vector((26.30, -13.53, 0)); D = Vector((0.2442, 0.9697, 0)); N = Vector((0.9697, -0.2442, 0))
def W(t, s, z):
    return Vector((P0.x + D.x * t + N.x * s, P0.y + D.y * t + N.y * s, z))
def ts(p):
    q = Vector((p.x, p.y, 0)) - P0; return q.dot(D), q.dot(N)

LNG_T = (-11.6, -5.4)
LNG_Z0, LNG_Z1 = 134.85, 142.62
WALL = -13.8
DOCK = 137.55

def mat(name, rgba, rough=0.5, alpha=1.0, trans=0.0, emit=0.0, ior=1.45, spec=0.5):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = rgba
    b.inputs['Roughness'].default_value = rough
    b.inputs['Alpha'].default_value = alpha
    b.inputs['Transmission Weight'].default_value = trans
    b.inputs['IOR'].default_value = ior
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = spec
    elif 'Specular' in b.inputs:
        b.inputs['Specular'].default_value = spec
    if emit:
        b.inputs['Emission Color'].default_value = rgba
        b.inputs['Emission Strength'].default_value = emit
    nt.links.new(b.outputs[0], o.inputs[0])
    m.blend_method = 'HASHED'
    return m

def box(name, col, m, t0, t1, s0, s1, z0, z1):
    # replace if exists
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    vs = [bm.verts.new(W(t, s, z)) for z in (z0, z1) for (t, s) in ((t0, s0), (t1, s0), (t1, s1), (t0, s1))]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[i] for i in f])
    bm.normal_update(); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(name, me); col.objects.link(o); return o

def cam(name, loc, tgt, lens=24):
    o = bpy.data.objects.get(name)
    if not o:
        o = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    o.data.lens = lens; o.data.clip_start = 0.05; o.data.clip_end = 60000
    return o

# --------------------------------------------------------------------------
# 0) ensure west atrium lounge stays hidden
# --------------------------------------------------------------------------
wc = bpy.data.collections.get('CCOM_lounge_20261014z')
if wc:
    wc.hide_render = True; wc.hide_viewport = True
    print('west lounge hidden')

# --------------------------------------------------------------------------
# 1) Lounge exterior readability — clear thin glass + deeper mullions
# --------------------------------------------------------------------------
# Thin architectural glass: low IOR + low specular → less milky interior bounce
m_glass = mat('CCOM_clear_glass_20261014jf', (0.92, 0.95, 0.97, 1),
              rough=0.01, alpha=0.04, trans=1.0, ior=1.05, spec=0.15)
# also retune z lounge glass if anything still refs it
mat('CCOM_lounge_glass_20261014z', (0.92, 0.95, 0.97, 1),
    rough=0.01, alpha=0.04, trans=1.0, ior=1.05, spec=0.15)
print('glass retuned thin IOR=1.05 alpha=0.04')

# Deepen lounge mullions / sill / head / rows (exterior projection)
gcol = bpy.data.collections.get('CCOM_east_glazing_20261014jf')
m_mar = bpy.data.materials.get('CCOM_maroon_frame_20261014jf') or mat('CCOM_maroon_frame_20261014jf', (0.30, 0.06, 0.07, 1), rough=0.35)
t0, t1 = LNG_T
# remove old lounge frame pieces from glazing col, rebuild deeper
prefix = 'CCOM_lounge_east_'
for o in list(gcol.objects if gcol else []):
    if o.name.startswith(prefix) and any(k in o.name for k in ('mull', 'sill', 'head', 'row', 'glass')):
        bpy.data.objects.remove(o, do_unlink=True)
# glass pane (slightly thicker for visibility as opening, still thin)
box(prefix + 'glass_20261014jf', gcol, m_glass, t0, t1, -0.02, 0.02, LNG_Z0, LNG_Z1)
bay = 1.4
n = max(1, round((t1 - t0) / bay))
for i in range(n + 1):
    t = t0 + (t1 - t0) * i / n
    # deeper mullion: s -0.14 (interior) to +0.18 (exterior) so exterior reads framed
    box(f'{prefix}mull{i}_20261014jf', gcol, m_mar, t - 0.04, t + 0.04, -0.14, 0.18, LNG_Z0, LNG_Z1)
box(prefix + 'sill_20261014jf', gcol, m_mar, t0, t1, -0.14, 0.20, LNG_Z0, LNG_Z0 + 0.09)
box(prefix + 'head_20261014jf', gcol, m_mar, t0, t1, -0.14, 0.20, LNG_Z1 - 0.09, LNG_Z1)
for j, z in enumerate((136.75, 138.65, 140.55, 141.95)):
    box(f'{prefix}row{j}_20261014jf', gcol, m_mar, t0, t1, -0.10, 0.14, z - 0.035, z + 0.035)
print('lounge mullions deepened n=', n)

# Dim lounge floor specular bounce into glass (keep people-free furniture)
m_floor = bpy.data.materials.get('CCOM_lounge_terrazzo_20261014z') or bpy.data.materials.get('CCOM_terrazzo_20261014jf')
if m_floor and m_floor.use_nodes:
    for nd in m_floor.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            # slightly warmer/darker + rougher so less blown reflection in glass
            nd.inputs['Base Color'].default_value = (0.78, 0.77, 0.74, 1)
            nd.inputs['Roughness'].default_value = 0.45
            print('terrazzo darkened')

# Soften lounge wall albedo slightly (less milky bounce)
m_w = bpy.data.materials.get('CCOM_lounge_wall_20261014jf')
if m_w and m_w.use_nodes:
    for nd in m_w.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            nd.inputs['Base Color'].default_value = (0.86, 0.86, 0.84, 1)
            nd.inputs['Roughness'].default_value = 0.7
            print('lounge wall toned')

# Ensure lounge collection visible, west hidden
lc = bpy.data.collections.get('CCOM_lounge_east_20261014jf')
if lc:
    lc.hide_render = False; lc.hide_viewport = False

# Hide any leftover exterior wall faces that still fill lounge opening:
# if School of Communication walls still block, carve again lightly
def carve(ob, t0_, t1_, s0_, s1_, z0_, z1_):
    mw = ob.matrix_world; inv = mw.inverted()
    bm = bmesh.new(); bm.from_mesh(ob.data)
    planes = [(W(t0_, 0, 0), D), (W(t1_, 0, 0), D), (W(0, s0_, 0), N), (W(0, s1_, 0), N),
              (Vector((0, 0, z0_)), Vector((0, 0, 1))), (Vector((0, 0, z1_)), Vector((0, 0, 1)))]
    nm = inv.to_3x3().transposed()
    for co, no in planes:
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=inv @ co, plane_no=(nm @ no).normalized(), dist=1e-4)
    kill = []
    for f in bm.faces:
        c = mw @ f.calc_center_median(); tt, ss = ts(c)
        if t0_ < tt < t1_ and s0_ < ss < s1_ and z0_ < c.z < z1_:
            kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    bm.to_mesh(ob.data); bm.free(); ob.data.update(); return len(kill)

walls = bpy.data.objects.get('School of Communication and Media walls')
if walls and walls.data.users == 1:
    k = carve(walls, LNG_T[0] + 0.05, LNG_T[1] - 0.05, -0.5, 0.9, LNG_Z0 + 0.05, LNG_Z1 - 0.05)
    print('recarve walls lounge', k)

# --------------------------------------------------------------------------
# 2) Equipment entrance polish — stucco-match patches, no truck cues, tone
# --------------------------------------------------------------------------
dcol = bpy.data.collections.get('CCOM_loading_dock_20261014jf3')
# kill any leftover truck-dock cues by name
truck_keys = ('bumper', 'stripe', 'lane', 'dock_door_', 'truck')
removed = 0
for o in list(bpy.data.objects):
    low = o.name.lower()
    if any(k in low for k in truck_keys) and ('equip' in low or 'dock' in low or 'loading' in low):
        # keep CAM_eye_CCOM_loading_dock
        if o.type == 'CAMERA':
            continue
        bpy.data.objects.remove(o, do_unlink=True); removed += 1
print('removed truck cues', removed)

# Stucco-matched wall patch material (match Parapet_stucco / Stucco_band_white)
m_stuc = mat('CCOM_equip_stucco_patch_' + TAG, (0.80, 0.79, 0.75, 1), rough=0.82)
# also nudge pier mat used by patches toward same tone
m_pier = bpy.data.materials.get('CCOM_east_pier_20261014jf')
if m_pier and m_pier.use_nodes:
    for nd in m_pier.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            nd.inputs['Base Color'].default_value = (0.80, 0.79, 0.75, 1)
            nd.inputs['Roughness'].default_value = 0.82
            print('pier mat matched stucco')

# reassign wallpatch/wallhead/wallback mats
if dcol:
    for o in dcol.objects:
        if any(k in o.name for k in ('wallpatch', 'wallhead', 'wallback')):
            if o.data and o.material_slots:
                o.material_slots[0].material = m_stuc
            elif o.data:
                o.data.materials.clear(); o.data.materials.append(m_stuc)
    print('wall patches reassigned to stucco')

# Slight platform polish: add thin apron edge strip (colour only), ensure 1+1 doors remain
# Confirm door count
n_roll = sum(1 for o in (dcol.objects if dcol else []) if 'rolldoor_20261014jf3' in o.name and 'slat' not in o.name and 'hood' not in o.name and 'jamb' not in o.name)
n_pers = sum(1 for o in (dcol.objects if dcol else []) if o.name.startswith('CCOM_equip_persdoor_20261014jf3'))
print('doors roll=', n_roll, 'pers=', n_pers)

# Darken apron a touch (less glare next to pale patches)
m_asph = bpy.data.materials.get('CCOM_dock_asphalt_20261014jf3')
if m_asph and m_asph.use_nodes:
    for nd in m_asph.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            nd.inputs['Base Color'].default_value = (0.14, 0.14, 0.14, 1)
            nd.inputs['Roughness'].default_value = 0.9

# Concrete platform slightly warmer/less chalky
m_conc = bpy.data.materials.get('CCOM_dock_concrete_20261014jf3')
if m_conc and m_conc.use_nodes:
    for nd in m_conc.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            nd.inputs['Base Color'].default_value = (0.55, 0.54, 0.51, 1)
            nd.inputs['Roughness'].default_value = 0.88
            print('platform concrete toned')

# --------------------------------------------------------------------------
# 3) Quick wins — box top less glaring white
# --------------------------------------------------------------------------
m_grade = bpy.data.materials.get('CCOM_grade_concrete_20261014jf')
if m_grade and m_grade.use_nodes:
    for nd in m_grade.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            nd.inputs['Base Color'].default_value = (0.52, 0.51, 0.48, 1)  # was 0.70 chalky
            nd.inputs['Roughness'].default_value = 0.9
            print('raised-box / grade concrete darkened')

# Close-up cams for WIP
cam('CAM_closeup_CCOM_lounge_glass_aa', W(-8.5, -3.5, LNG_Z0 + 2.2), W(-8.5, 5.0, LNG_Z0 + 3.5), 28)
cam('CAM_closeup_CCOM_equip_entry_aa', W(-24.5, -15.5, DOCK + 1.4), W(WALL, -16.5, DOCK + 1.5), 32)
# nudge lounge eye cam slightly higher / toward glass mid for clearer exterior read
cam('CAM_eye_CCOM_lounge_east', W(-8.5, -6.8, LNG_Z0 + 1.65), W(-8.5, 25, LNG_Z0 + 4.0), 20)

print('TAG', TAG, 'polish done')
if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED')
else:
    print('dry-run (pass --save)')

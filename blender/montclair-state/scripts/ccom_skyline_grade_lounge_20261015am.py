"""2026-10-15 ~8:24 AM ET (tag 20261015am). CCOM open items:
1) Lab skyline faint through glass / at distance — BD_* skyline mats mix to grey haze emission by
   view-distance; at ~22 km that washout matches the cloudy HDRI so Manhattan disappears. Make those
   mats local (asset file untouched) and soften haze + cool/darken massing so the silhouette reads
   like refs/joe_ccom_20261014/old_office_window_view_city.jpg (bearing/distance unchanged).
2) Grade/terrace top too bright — darken concrete + drop specular (paver values).
3) Lounge: retarget horizontal curtain-wall rows to photo short/tall/short (refs/ccom_x/02);
   bump ceiling-panel emission so fixtures read; chair fabric/chrome polish (still UNVERIFIED forms).
Glass IOR already thin (1.02 / alpha 0.025) — leave it.
Run: /opt/blender/blender -b montclair_state.blend --python scripts/ccom_skyline_grade_lounge_20261015am.py -- --save
"""
import bpy, sys, math
from mathutils import Vector, Matrix

ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
TAG = '20261015am'
SAVE = '--save' in ARGV

def bsdf(m):
    if not m or not m.use_nodes:
        return None
    for n in m.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            return n
    return None

def make_local(name):
    m = bpy.data.materials.get(name)
    if m is None:
        print('MISSING mat', name); return None
    if m.library:
        m = m.make_local()
        print('LOCALIZED', name, '->', m.name, 'lib', m.library)
    else:
        print('ALREADY_LOCAL', name)
    return m

# --------------------------------------------------------------------------
# 1) Skyline readability — soften distance haze on BD building mats (LOCAL copies)
# --------------------------------------------------------------------------
# Haze graph (per BD_* tower mats): ViewDistance / D -> exp -> (1-x) -> clamp -> mix BSDF|Emission(0.62,0.64,0.66)
# At ~22 km with D=-40000 haze fac ~0.4 already washes the silhouette into the cloudy sky.
# Changes (UNVERIFIED artistic; keep true bearing/distance of geometry):
#   - DIVIDE denominator -40000 -> -90000 (haze slower with distance)
#   - Clamp max 1.0 -> 0.45 (never fully replace the building colour)
#   - Haze emission cooler/darker + slightly weaker so residual haze still reads as atmosphere
#   - BSDF bases: fill darker, glass cooler, stone slightly cooler — silhouette against bright sky

BD_NAMES = ('BD_fill_massing', 'BD_glass_tower', 'BD_stone_tower', 'BD_steel', 'BD_white_roof')
HAZE_COL = (0.42, 0.48, 0.58, 1.0)   # cooler blue-grey (photo skyline tone)
HAZE_STR = 0.55
DIV_DENOM = -90000.0
CLAMP_MAX = 0.45

BSDF_TWEAK = {
    'BD_fill_massing':  dict(base=(0.28, 0.30, 0.34, 1.0), rough=0.55),
    'BD_glass_tower':   dict(base=(0.22, 0.30, 0.40, 1.0), rough=0.22),
    'BD_stone_tower':   dict(base=(0.42, 0.40, 0.38, 1.0), rough=0.62),
    'BD_steel':         dict(base=(0.48, 0.50, 0.54, 1.0), rough=0.35),
    'BD_white_roof':    dict(base=(0.62, 0.63, 0.65, 1.0), rough=0.55),  # was 0.8 chalk
}

for name in BD_NAMES:
    m = make_local(name)
    if not m:
        continue
    nt = m.node_tree
    # find DIVIDE that uses Camera View Distance chain (first MATH DIVIDE with |default| large)
    for n in nt.nodes:
        if n.type == 'MATH' and n.operation == 'DIVIDE':
            # input[1] is the constant denominator when not linked
            if not n.inputs[1].is_linked:
                old = float(n.inputs[1].default_value)
                if abs(old) >= 1000:  # the distance scale
                    n.inputs[1].default_value = DIV_DENOM
                    print(name, 'DIVIDE denom', old, '->', DIV_DENOM)
        if n.type == 'CLAMP':
            # Blender 4: clamp inputs Min/Max
            if 'Max' in n.inputs:
                old = float(n.inputs['Max'].default_value)
                n.inputs['Max'].default_value = CLAMP_MAX
                print(name, 'CLAMP max', old, '->', CLAMP_MAX)
        if n.type == 'EMISSION':
            n.inputs['Color'].default_value = HAZE_COL
            n.inputs['Strength'].default_value = HAZE_STR
            print(name, 'HAZE emit', HAZE_COL, HAZE_STR)
    b = bsdf(m)
    tw = BSDF_TWEAK.get(name)
    if b and tw:
        b.inputs['Base Color'].default_value = tw['base']
        b.inputs['Roughness'].default_value = tw['rough']
        print(name, 'BSDF base', tw['base'], 'rough', tw['rough'])

# Soften farfield ortho haze Value lift slightly so horizon band isn't milky white
m_haze = make_local('BD_farfield_ortho_haze')
if m_haze:
    for n in m_haze.node_tree.nodes:
        if n.type == 'HUE_SAT':
            # was Value=0.5 (darkens); leave. Reduce mix-to-haze clamp if present.
            pass
        if n.type == 'MATH' and n.operation == 'DIVIDE' and not n.inputs[1].is_linked:
            old = float(n.inputs[1].default_value)
            if abs(old) >= 1000:
                n.inputs[1].default_value = -28000.0  # was -16000; slower haze on ground
                print('BD_farfield_ortho_haze DIVIDE', old, '->', -28000.0)
        if n.type == 'CLAMP' and 'Max' in n.inputs:
            n.inputs['Max'].default_value = 0.55
            print('BD_farfield_ortho_haze CLAMP max -> 0.55')
        if n.type == 'EMISSION':
            n.inputs['Color'].default_value = (0.50, 0.54, 0.60, 1.0)
            n.inputs['Strength'].default_value = 0.45

print('SKYLINE haze/massing retuned (local BD mats; asset file untouched)')

# --------------------------------------------------------------------------
# 2) Grade / raised-box terrace tone — concrete/paver, not chalk white
# --------------------------------------------------------------------------
def tone_concrete(name, rgba, rough=0.95, spec=0.12):
    m = bpy.data.materials.get(name)
    if not m:
        print('no mat', name); return
    b = bsdf(m)
    if not b:
        return
    old = tuple(round(float(x), 3) for x in b.inputs['Base Color'].default_value)
    b.inputs['Base Color'].default_value = rgba
    b.inputs['Roughness'].default_value = rough
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = spec
    print('TONE', name, old, '->', tuple(round(float(x), 3) for x in rgba), 'spec', spec)

# Warm mid-grey concrete/paver (photo terrace is dull grey, not white)
tone_concrete('CCOM_grade_concrete_20261014jf', (0.30, 0.29, 0.27, 1.0), 0.96, 0.10)
tone_concrete('CCOM_grade_strip_20261014jf', (0.22, 0.22, 0.22, 1.0), 0.92, 0.08)
tone_concrete('CCOM_lab_terrace_roof_20261014y', (0.34, 0.33, 0.31, 1.0), 0.90, 0.12)
tone_concrete('CCOM_lab_terrace_roof_20261014x', (0.34, 0.33, 0.31, 1.0), 0.90, 0.12)
tone_concrete('CCOM_dock_concrete_20261014jf3', (0.38, 0.37, 0.34, 1.0), 0.92, 0.12)

# Add subtle procedural noise to grade concrete if it has no texture yet (paver variation)
m = bpy.data.materials.get('CCOM_grade_concrete_20261014jf')
if m and m.use_nodes:
    nt = m.node_tree
    b = bsdf(m)
    # only add once
    if b and not any(n.name == 'AM_paver_noise' for n in nt.nodes):
        tc = nt.nodes.new('ShaderNodeTexCoord'); tc.name = 'AM_texco'; tc.location = (-800, 0)
        nse = nt.nodes.new('ShaderNodeTexNoise'); nse.name = 'AM_paver_noise'; nse.location = (-600, 0)
        nse.inputs['Scale'].default_value = 12.0
        nse.inputs['Detail'].default_value = 6.0
        nse.inputs['Roughness'].default_value = 0.55
        ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.name = 'AM_paver_ramp'; ramp.location = (-400, 0)
        ramp.color_ramp.elements[0].position = 0.35
        ramp.color_ramp.elements[0].color = (0.24, 0.23, 0.21, 1)
        ramp.color_ramp.elements[1].position = 0.75
        ramp.color_ramp.elements[1].color = (0.36, 0.35, 0.32, 1)
        nt.links.new(tc.outputs['Object'], nse.inputs['Vector'])
        nt.links.new(nse.outputs['Fac'], ramp.inputs['Fac'])
        nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
        print('grade concrete: procedural paver noise added')

# --------------------------------------------------------------------------
# 3a) Lounge curtain-wall horizontal rows — photo short / tall / short (3 pane rows)
# --------------------------------------------------------------------------
# Existing jf rows at z≈136.75 / 138.65 / 140.55 / 141.95 (4 bands). Photo wants 3 pane rows
# with proportions ~1:2:1 over glass z 134.85..142.62 (H=7.77).
Z0, Z1 = 134.85, 142.62
H = Z1 - Z0
# short : tall : short = 1 : 2 : 1
u = H / 4.0
z_transom_lo = Z0 + u          # ~136.79
z_transom_hi = Z0 + 3.0 * u    # ~140.74
print('LOUNGE rows target transoms z', round(z_transom_lo, 3), round(z_transom_hi, 3))

col_photo = bpy.data.collections.get('CCOM_lounge_photo_20261015al')
frame_mat = bpy.data.materials.get('CCOM_maroon_frame_20261014jf')

# Hide old 4 horizontal rows (keep head/sill)
old_rows = []
for o in bpy.data.objects:
    if o.name.startswith('CCOM_lounge_east_row') and o.name.endswith('_20261014jf'):
        o.hide_render = True
        o.hide_viewport = True
        old_rows.append(o)
        print('HIDE row', o.name)
print('hidden old rows', len(old_rows))

# Build 2 new horizontal mullions spanning the glass line, matching vertical mull depth
# Reuse geometry from an old row as template (same XY footprint)
template = old_rows[0] if old_rows else None
# Also hide any prior am rows for rerun
if col_photo:
    for o in list(col_photo.objects):
        if o.name.startswith('CCOM_lounge_row2_'):
            bpy.data.objects.remove(o, do_unlink=True)

def place_horiz_row(name, z_mid, template_ob):
    """Duplicate template mesh, recenter to z_mid, link to photo collection."""
    me = template_ob.data.copy()
    me.name = name
    # shift verts in object space so world z centers on z_mid
    # template world z centre:
    zs = [(template_ob.matrix_world @ v.co).z for v in template_ob.data.vertices]
    zc_old = 0.5 * (min(zs) + max(zs))
    dz = z_mid - zc_old
    # apply dz in world Z via object translation (template loc is 0,0,0 with baked verts)
    o = bpy.data.objects.new(name, me)
    # copy world matrix then translate
    o.matrix_world = template_ob.matrix_world.copy()
    o.location.z = template_ob.location.z + dz
    # Actually verts are in world-ish coords with loc 0 — shift mesh verts
    if abs(template_ob.location.length) < 1e-6:
        for v in me.vertices:
            v.co.z += dz
        o.location = template_ob.location.copy()
    if frame_mat and frame_mat.name not in [s.material.name if s.material else '' for s in o.material_slots]:
        me.materials.clear()
        me.materials.append(frame_mat)
    elif frame_mat and len(me.materials) == 0:
        me.materials.append(frame_mat)
    if col_photo and o.name not in [x.name for x in col_photo.objects]:
        col_photo.objects.link(o)
    # ensure not in scene collection twice awkwardly
    o.hide_render = False
    o.hide_viewport = False
    o['source'] = 'photo short/tall/short pane rows UNVERIFIED (ccom_skyline_grade_lounge_20261015am.py)'
    print('ROW', name, 'z_mid', round(z_mid, 3))
    return o

if template:
    place_horiz_row('CCOM_lounge_row2_lo_' + TAG, z_transom_lo, template)
    place_horiz_row('CCOM_lounge_row2_hi_' + TAG, z_transom_hi, template)
else:
    print('WARN no template row — skipped horizontal retarget')

# --------------------------------------------------------------------------
# 3b) Lounge ceiling lights — make recessed panels read in interior shots
# --------------------------------------------------------------------------
m_ceil = bpy.data.materials.get('CCOM_lounge_ceil_light_20261014jf')
if m_ceil:
    b = bsdf(m_ceil)
    if b:
        # was emit 6 — outdoor HDRI washes them out; bump + slightly warmer
        b.inputs['Emission Strength'].default_value = 14.0
        b.inputs['Emission Color'].default_value = (1.0, 0.96, 0.88, 1.0)
        b.inputs['Base Color'].default_value = (1.0, 0.96, 0.88, 1.0)
        print('ceil light emit -> 14')
m_fill = bpy.data.materials.get('CCOM_lounge_fill_light_20261014z')
if m_fill:
    b = bsdf(m_fill)
    if b:
        b.inputs['Emission Strength'].default_value = 8.0
        print('fill wash emit -> 8')

# Ensure east lounge light panels are visible (not hidden)
for o in bpy.data.objects:
    if o.name.startswith('CCOM_lounge_east_light') and o.name.endswith('_20261014jf'):
        o.hide_render = False
        o.hide_viewport = False
        print('unhide', o.name)

# --------------------------------------------------------------------------
# 3c) Chair polish — less toy-like: fabric roughness up, chrome shinier, slight dark crease tint
# --------------------------------------------------------------------------
m_blue = bpy.data.materials.get('CCOM_lounge_swivel_blue_20261015al')
if m_blue:
    b = bsdf(m_blue)
    if b:
        # deeper saturated blue, higher roughness (fabric), low spec
        b.inputs['Base Color'].default_value = (0.012, 0.10, 0.42, 1.0)
        b.inputs['Roughness'].default_value = 0.72
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 0.18
        if 'Sheen Weight' in b.inputs:
            b.inputs['Sheen Weight'].default_value = 0.35
            if 'Sheen Roughness' in b.inputs:
                b.inputs['Sheen Roughness'].default_value = 0.4
            if 'Sheen Tint' in b.inputs:
                try:
                    b.inputs['Sheen Tint'].default_value = (0.4, 0.55, 0.9, 1.0)
                except Exception:
                    pass
        print('swivel blue fabric polished')

# Chrome: was likely high-rough plastic look
for mn in ('CCOM_lounge_chrome_20261014z',):
    m = bpy.data.materials.get(mn)
    if not m:
        continue
    b = bsdf(m)
    if not b:
        continue
    b.inputs['Base Color'].default_value = (0.75, 0.76, 0.78, 1.0)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Roughness'].default_value = 0.22
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.5
    print('chrome polished', mn)

# Slight seat darkening via existing seat objects' material is shared — OK.
# Thicken chrome stems a bit for scale (0.028 -> visually heavier via scale)
n_stem = 0
for o in bpy.data.objects:
    if 'swivel' in o.name and o.name.endswith('_stem_20261015al'):
        # scale XY up ~20%
        o.scale.x = 1.25
        o.scale.y = 1.25
        n_stem += 1
print('stem scale bump', n_stem)

print('TAG', TAG, 'done')
if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)
else:
    print('dry-run (pass --save)')

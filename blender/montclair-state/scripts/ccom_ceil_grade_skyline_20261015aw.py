"""2026-10-15 ~6:25 PM ET (tag 20261015aw). CCOM open items on main blend:
1) Lounge ceiling recessed fixtures — shallow frame/reveal + lay-in panel grid so lights
   read as framed panels (not flat emission slabs). Match refs/ccom_x/02 as well as possible
   (people-free). Collection CCOM_lounge_ceil_frames_20261015aw.
2) Eye-level grade/terrace tone — further darken/despecularize raised-box / grade / hatch
   mats so CAM_eye_CCOM_grade_lab does not blow out. UNVERIFIED artistic.
3) Lab skyline readability — nudge local BD_* haze clamp / massing contrast further
   (asset already at pass2; local copies only here unless still library-linked).
4) Optional: small lounge swivel chair polish (less toy-like; forms stay photo-backed).

Run:
  /workspace/nj-scenes/tools/blender_slot.sh -b montclair-state/montclair_state.blend \\
    --python montclair-state/scripts/ccom_ceil_grade_skyline_20261015aw.py -- --save
"""
import bpy, sys, math
from mathutils import Vector, Matrix

ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
TAG = '20261015aw'
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
        print('LOCALIZED', name, '->', m.name)
    else:
        print('ALREADY_LOCAL', name)
    return m

def mat(name, rgba, rough=0.6, emit=0.0, metallic=0.0, spec=0.2):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    b = bsdf(m)
    if b:
        b.inputs['Base Color'].default_value = rgba
        b.inputs['Roughness'].default_value = rough
        b.inputs['Metallic'].default_value = metallic
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = spec
        if emit > 0:
            b.inputs['Emission Color'].default_value = rgba
            b.inputs['Emission Strength'].default_value = emit
        else:
            b.inputs['Emission Strength'].default_value = 0.0
    return m

def colnew(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    # clear prior aw objects for rerun
    for o in list(c.objects):
        if TAG in o.name:
            bpy.data.objects.remove(o, do_unlink=True)
    return c

def world_bounds(o):
    corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
    xs = [v.x for v in corners]; ys = [v.y for v in corners]; zs = [v.z for v in corners]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)

def box_world(name, col, material, x0, x1, y0, y1, z0, z1):
    """Axis-aligned box in world XYZ (CCOM east lounge is nearly axis-aligned in world)."""
    me = bpy.data.meshes.new(name)
    # 8 verts
    verts = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0),
    ]
    me.from_pydata(verts, [], faces)
    me.update()
    if material:
        me.materials.append(material)
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    o['source'] = f'recessed ceil frame UNVERIFIED ({TAG})'
    o['tag'] = TAG
    return o

# --------------------------------------------------------------------------
# 1) Lounge ceiling recessed fixtures — frame + reveal + lay-in grid
# --------------------------------------------------------------------------
col = colnew(f'CCOM_lounge_ceil_frames_{TAG}')
m_frame = mat(f'CCOM_lounge_ceil_frame_{TAG}', (0.78, 0.78, 0.76, 1.0), rough=0.55, spec=0.15)
m_reveal = mat(f'CCOM_lounge_ceil_reveal_{TAG}', (0.45, 0.45, 0.44, 1.0), rough=0.7, spec=0.08)
m_tee = mat(f'CCOM_lounge_ceil_tee_{TAG}', (0.62, 0.62, 0.60, 1.0), rough=0.4, metallic=0.15, spec=0.35)
m_glow = bpy.data.materials.get('CCOM_lounge_ceil_light_20261014jf')

# Keep emit readable against framed pocket (am bumped to 14; nudge slightly warmer/stronger)
if m_glow:
    b = bsdf(m_glow)
    if b:
        b.inputs['Emission Strength'].default_value = 16.0
        b.inputs['Emission Color'].default_value = (1.0, 0.97, 0.90, 1.0)
        b.inputs['Base Color'].default_value = (1.0, 0.97, 0.90, 1.0)
        print('ceil light emit -> 16')

lights = [o for o in bpy.data.objects
          if o.name.startswith('CCOM_lounge_east_light') and o.name.endswith('_20261014jf')]
lights = sorted(lights, key=lambda o: o.name)
print('lights found', len(lights), [o.name for o in lights])

FRAME_W = 0.045          # outer frame lip width
REVEAL_D = 0.055         # how far light sits below ceiling plane
TEE_W = 0.018            # lay-in tee width
N_DIV_X = 2              # cross tees along X (→ 3 panels)
N_DIV_Y = 1              # cross tees along Y (→ 2 panels)

for i, light in enumerate(lights):
    x0, x1, y0, y1, z0, z1 = world_bounds(light)
    # Ensure ordered
    if x0 > x1: x0, x1 = x1, x0
    if y0 > y1: y0, y1 = y1, y0
    if z0 > z1: z0, z1 = z1, z0
    z_ceil = max(z0, z1)  # top of thin light slab ≈ underside of ceiling
    # Recess: move light mesh down so it sits in a pocket
    # Light verts are baked in world-ish coords with loc ~0 — shift object location.z
    light.location.z = light.location.z - REVEAL_D
    # Shrink light slightly so frame lip is visible around it
    # (scale toward centre in XY)
    cx = 0.5 * (x0 + x1); cy = 0.5 * (y0 + y1)
    inset = FRAME_W * 0.85
    # Rebuild light as slightly inset thinner panel at recessed Z (keep old mesh, just frame around)
    # Frame outer ring at ceiling plane, spanning original light footprint + small overhang
    ox0, ox1 = x0 - 0.01, x1 + 0.01
    oy0, oy1 = y0 - 0.01, y1 + 0.01
    z_top = z_ceil + 0.002
    z_lip = z_ceil - 0.012
    z_pocket = z_ceil - REVEAL_D - 0.005
    # Outer frame bars (4 sides) — white ceiling trim
    box_world(f'CCOM_lounge_ceil_frame{i}_N_{TAG}', col, m_frame,
              ox0, ox1, oy1 - FRAME_W, oy1, z_lip, z_top)
    box_world(f'CCOM_lounge_ceil_frame{i}_S_{TAG}', col, m_frame,
              ox0, ox1, oy0, oy0 + FRAME_W, z_lip, z_top)
    box_world(f'CCOM_lounge_ceil_frame{i}_W_{TAG}', col, m_frame,
              ox0, ox0 + FRAME_W, oy0 + FRAME_W, oy1 - FRAME_W, z_lip, z_top)
    box_world(f'CCOM_lounge_ceil_frame{i}_E_{TAG}', col, m_frame,
              ox1 - FRAME_W, ox1, oy0 + FRAME_W, oy1 - FRAME_W, z_lip, z_top)
    # Reveal well walls (darker) from ceiling down to light plane
    ix0, ix1 = ox0 + FRAME_W, ox1 - FRAME_W
    iy0, iy1 = oy0 + FRAME_W, oy1 - FRAME_W
    box_world(f'CCOM_lounge_ceil_reveal{i}_N_{TAG}', col, m_reveal,
              ix0, ix1, iy1 - 0.008, iy1, z_pocket, z_lip)
    box_world(f'CCOM_lounge_ceil_reveal{i}_S_{TAG}', col, m_reveal,
              ix0, ix1, iy0, iy0 + 0.008, z_pocket, z_lip)
    box_world(f'CCOM_lounge_ceil_reveal{i}_W_{TAG}', col, m_reveal,
              ix0, ix0 + 0.008, iy0, iy1, z_pocket, z_lip)
    box_world(f'CCOM_lounge_ceil_reveal{i}_E_{TAG}', col, m_reveal,
              ix1 - 0.008, ix1, iy0, iy1, z_pocket, z_lip)
    # Lay-in tee grid over the light face (at light top after recess)
    z_tee0 = z_ceil - REVEAL_D - 0.002
    z_tee1 = z_tee0 + 0.008
    # X-span tees (parallel to Y) — divide along X
    for d in range(1, N_DIV_X + 1):
        t = d / (N_DIV_X + 1)
        xx = ix0 + t * (ix1 - ix0)
        box_world(f'CCOM_lounge_ceil_tee{i}_x{d}_{TAG}', col, m_tee,
                  xx - TEE_W * 0.5, xx + TEE_W * 0.5, iy0, iy1, z_tee0, z_tee1)
    # Y-span tees (parallel to X)
    for d in range(1, N_DIV_Y + 1):
        t = d / (N_DIV_Y + 1)
        yy = iy0 + t * (iy1 - iy0)
        box_world(f'CCOM_lounge_ceil_tee{i}_y{d}_{TAG}', col, m_tee,
                  ix0, ix1, yy - TEE_W * 0.5, yy + TEE_W * 0.5, z_tee0, z_tee1)
    light.hide_render = False
    light.hide_viewport = False
    print(f'framed light{i}', light.name, 'footprint',
          round(x1 - x0, 3), 'x', round(y1 - y0, 3), 'recess', REVEAL_D)

# Close-up cam looking up at middle light panel (for WIP detail)
lights_sorted = lights
if lights_sorted:
    mid = lights_sorted[1] if len(lights_sorted) > 1 else lights_sorted[0]
    x0, x1, y0, y1, z0, z1 = world_bounds(mid)
    # after recess, light is lower; aim at panel centre from below/inward
    cx = 0.5 * (x0 + x1); cy = 0.5 * (y0 + y1)
    zc = max(z0, z1) - REVEAL_D
    # stand near floor-ish looking up — actually eye-level looking up from lounge
    # Place cam under the panel looking nearly straight up with slight bias to show frame depth
    cam_name = f'CAM_closeup_CCOM_lounge_ceil_{TAG}'
    o = bpy.data.objects.get(cam_name)
    if o is None:
        o = bpy.data.objects.new(cam_name, bpy.data.cameras.new(cam_name))
        bpy.context.scene.collection.objects.link(o)
    # From slightly south of panel, z ~1.7 m above lounge floor (~134.85+1.7)
    loc = Vector((cx, cy - 1.8, 136.55))
    tgt = Vector((cx, cy, zc))
    o.location = loc
    o.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
    o.data.lens = 35
    o.data.clip_start = 0.05
    o.data.clip_end = 60000
    print('CAM', cam_name, 'loc', tuple(round(v, 3) for v in loc), 'tgt', tuple(round(v, 3) for v in tgt))

print('CEIL frames collection', col.name, 'objects', len(col.objects))

# --------------------------------------------------------------------------
# 2) Grade / terrace tone — further darken for eye-level sun
# --------------------------------------------------------------------------
def tone(name, rgba=None, rough=None, spec=None):
    m = bpy.data.materials.get(name)
    if not m:
        print('no mat', name); return
    b = bsdf(m)
    if not b:
        return
    old = tuple(round(float(x), 3) for x in b.inputs['Base Color'].default_value)
    if rgba is not None:
        b.inputs['Base Color'].default_value = rgba
    if rough is not None:
        b.inputs['Roughness'].default_value = rough
    if spec is not None and 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = spec
    print('TONE', name, old, '->',
          tuple(round(float(x), 3) for x in b.inputs['Base Color'].default_value),
          'r', round(float(b.inputs['Roughness'].default_value), 3),
          's', round(float(b.inputs['Specular IOR Level'].default_value), 3) if 'Specular IOR Level' in b.inputs else None)

# Darker warm concrete / asphalt / hatch (UNVERIFIED artistic; photo terrace is dull grey)
tone('CCOM_grade_concrete_20261014jf', (0.18, 0.17, 0.16, 1.0), 0.98, 0.04)
tone('CCOM_grade_strip_20261014jf', (0.08, 0.08, 0.08, 1.0), 0.95, 0.04)
tone('CCOM_hatch_20261014jf', (0.09, 0.09, 0.085, 1.0), 0.85, 0.04)
tone('CCOM_lab_terrace_roof_20261014y', (0.22, 0.21, 0.20, 1.0), 0.94, 0.06)
tone('CCOM_lab_terrace_roof_20261014x', (0.22, 0.21, 0.20, 1.0), 0.94, 0.06)
tone('CCOM_dock_concrete_20261014jf3', (0.26, 0.25, 0.23, 1.0), 0.94, 0.06)

# Darken existing AM_paver_ramp if present (overrides Base Color)
m = bpy.data.materials.get('CCOM_grade_concrete_20261014jf')
if m and m.use_nodes:
    for n in m.node_tree.nodes:
        if n.name == 'AM_paver_ramp' and n.type == 'VALTORGB':
            n.color_ramp.elements[0].color = (0.12, 0.115, 0.105, 1)
            n.color_ramp.elements[1].color = (0.22, 0.21, 0.195, 1)
            print('AM_paver_ramp darkened -> 0.12..0.22')
        # Also add AW multiply darken once if not present
    if not any(n.name == 'AW_grade_mul' for n in m.node_tree.nodes):
        b = bsdf(m)
        # Find what feeds Base Color
        if b and b.inputs['Base Color'].is_linked:
            link = b.inputs['Base Color'].links[0]
            from_s = link.from_socket
            nt = m.node_tree
            mul = nt.nodes.new('ShaderNodeMixRGB')
            mul.name = 'AW_grade_mul'
            mul.blend_type = 'MULTIPLY'
            mul.inputs['Fac'].default_value = 1.0
            mul.inputs['Color2'].default_value = (0.72, 0.72, 0.70, 1.0)  # ~28% darker
            mul.location = (from_s.node.location.x + 180, from_s.node.location.y)
            nt.links.new(from_s, mul.inputs['Color1'])
            nt.links.new(mul.outputs['Color'], b.inputs['Base Color'])
            print('AW_grade_mul ×0.72 added')

print('GRADE tone darkened (UNVERIFIED artistic)')

# --------------------------------------------------------------------------
# 3) Lab skyline — further local haze / massing nudge
# --------------------------------------------------------------------------
# Current (am pass2 / asset): DIV -120000, CLAMP 0.28, haze str 0.40
# Nudge: slower haze, lower clamp, slightly darker cooler massing (geometry bearing unchanged)
BD_NAMES = ('BD_fill_massing', 'BD_glass_tower', 'BD_stone_tower', 'BD_steel', 'BD_white_roof')
HAZE_COL = (0.28, 0.34, 0.44, 1.0)
HAZE_STR = 0.32
DIV_DENOM = -160000.0
CLAMP_MAX = 0.20

BSDF_TWEAK = {
    'BD_fill_massing':  dict(base=(0.14, 0.16, 0.20, 1.0), rough=0.58),
    'BD_glass_tower':   dict(base=(0.16, 0.22, 0.32, 1.0), rough=0.20),
    'BD_stone_tower':   dict(base=(0.34, 0.32, 0.30, 1.0), rough=0.65),
    'BD_steel':         dict(base=(0.38, 0.40, 0.44, 1.0), rough=0.32),
    'BD_white_roof':    dict(base=(0.50, 0.51, 0.53, 1.0), rough=0.55),
}

for name in BD_NAMES:
    m = make_local(name)
    if not m:
        continue
    nt = m.node_tree
    for n in nt.nodes:
        if n.type == 'MATH' and n.operation == 'DIVIDE':
            if not n.inputs[1].is_linked:
                old = float(n.inputs[1].default_value)
                if abs(old) >= 1000:
                    n.inputs[1].default_value = DIV_DENOM
                    print(name, 'DIVIDE', old, '->', DIV_DENOM)
        if n.type == 'CLAMP' and 'Max' in n.inputs:
            old = float(n.inputs['Max'].default_value)
            n.inputs['Max'].default_value = CLAMP_MAX
            print(name, 'CLAMP max', old, '->', CLAMP_MAX)
        if n.type == 'EMISSION':
            n.inputs['Color'].default_value = HAZE_COL
            n.inputs['Strength'].default_value = HAZE_STR
            print(name, 'HAZE', HAZE_COL, HAZE_STR)
    b = bsdf(m)
    tw = BSDF_TWEAK.get(name)
    if b and tw:
        b.inputs['Base Color'].default_value = tw['base']
        b.inputs['Roughness'].default_value = tw['rough']
        print(name, 'BSDF', tw['base'])

m_haze = make_local('BD_farfield_ortho_haze')
if m_haze:
    for n in m_haze.node_tree.nodes:
        if n.type == 'MATH' and n.operation == 'DIVIDE' and not n.inputs[1].is_linked:
            old = float(n.inputs[1].default_value)
            if abs(old) >= 1000:
                n.inputs[1].default_value = -36000.0
                print('BD_farfield_ortho_haze DIVIDE', old, '->', -36000.0)
        if n.type == 'CLAMP' and 'Max' in n.inputs:
            n.inputs['Max'].default_value = 0.42
            print('BD_farfield_ortho_haze CLAMP max -> 0.42')
        if n.type == 'EMISSION':
            n.inputs['Color'].default_value = (0.44, 0.48, 0.55, 1.0)
            n.inputs['Strength'].default_value = 0.38

print('SKYLINE local haze nudged (bearing/distance unchanged; UNVERIFIED artistic)')

# --------------------------------------------------------------------------
# 4) Optional chair polish — fabric micro-variation + less toy chrome
# --------------------------------------------------------------------------
m_blue = bpy.data.materials.get('CCOM_lounge_swivel_blue_20261015al')
if m_blue and m_blue.use_nodes:
    b = bsdf(m_blue)
    nt = m_blue.node_tree
    if b and not any(n.name == 'AW_fabric_noise' for n in nt.nodes):
        tc = nt.nodes.new('ShaderNodeTexCoord'); tc.name = 'AW_fab_texco'; tc.location = (-900, 200)
        nse = nt.nodes.new('ShaderNodeTexNoise'); nse.name = 'AW_fabric_noise'; nse.location = (-700, 200)
        nse.inputs['Scale'].default_value = 85.0
        nse.inputs['Detail'].default_value = 8.0
        nse.inputs['Roughness'].default_value = 0.65
        ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.name = 'AW_fabric_ramp'; ramp.location = (-480, 200)
        ramp.color_ramp.elements[0].position = 0.35
        ramp.color_ramp.elements[0].color = (0.008, 0.07, 0.32, 1)
        ramp.color_ramp.elements[1].position = 0.70
        ramp.color_ramp.elements[1].color = (0.018, 0.13, 0.50, 1)
        nt.links.new(tc.outputs['Object'], nse.inputs['Vector'])
        nt.links.new(nse.outputs['Fac'], ramp.inputs['Fac'])
        nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
        b.inputs['Roughness'].default_value = 0.78
        if 'Sheen Weight' in b.inputs:
            b.inputs['Sheen Weight'].default_value = 0.42
        print('swivel blue: fabric noise + sheen')
    elif b:
        b.inputs['Roughness'].default_value = 0.78
        print('swivel blue: roughness bump (noise already present)')

m_chrome = bpy.data.materials.get('CCOM_lounge_chrome_20261014z')
if m_chrome:
    b = bsdf(m_chrome)
    if b:
        b.inputs['Base Color'].default_value = (0.70, 0.71, 0.73, 1.0)
        b.inputs['Metallic'].default_value = 1.0
        b.inputs['Roughness'].default_value = 0.18
        print('chrome: slightly darker mirror')

# Soften wing tips: slight Z flatten on wing pieces so back reads less blocky
n_wing = 0
for o in bpy.data.objects:
    if 'swivel' in o.name and '_wing' in o.name and o.name.endswith('_20261015al'):
        o.scale.z = 0.92
        o.scale.x = 1.04
        n_wing += 1
print('wing scale polish', n_wing)

print('TAG', TAG, 'done')
if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)
else:
    print('dry-run (pass --save)')

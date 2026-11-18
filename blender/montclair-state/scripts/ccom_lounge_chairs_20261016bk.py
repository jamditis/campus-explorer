"""2026-10-16 ~8:25 AM ET (tag 20261016bk). CCOM lounge swivel chairs polish on main blend.

Photo: refs/ccom_x/02_20241009_SCM_study_spot.jpg — cerulean fabric high-back swivels on
polished-but-not-mirror chrome 4-star pedestals; low seat, tapered back, integrated arms.
Prior al/aw forms kept; this pass only mats + mild proportion scale (no new furniture).

UNVERIFIED artistic (eye-scale from photo). Soft-light / ba eave untouched.

Run:
  /workspace/nj-scenes/tools/blender_slot.sh -b montclair-state/montclair_state.blend \\
    --python montclair-state/scripts/ccom_lounge_chairs_20261016bk.py -- --save
"""
import bpy, sys
from mathutils import Vector

ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
TAG = '20261016bk'
SAVE = '--save' in ARGV
FLAG = 'bk_lounge_chairs'


def bsdf(m):
    if not m or not m.use_nodes:
        return None
    for n in m.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            return n
    return None


# --------------------------------------------------------------------------
# 1) Fabric — less toy plastic: higher roughness, woven micro-noise, soft sheen
# --------------------------------------------------------------------------
m_blue = bpy.data.materials.get('CCOM_lounge_swivel_blue_20261015al')
if m_blue and m_blue.use_nodes:
    b = bsdf(m_blue)
    nt = m_blue.node_tree
    if b:
        # Prefer object-space fine weave over aw's coarser noise if present
        nse = nt.nodes.get('AW_fabric_noise') or nt.nodes.get('BK_fabric_noise')
        ramp = nt.nodes.get('AW_fabric_ramp') or nt.nodes.get('BK_fabric_ramp')
        if nse is None:
            tc = nt.nodes.new('ShaderNodeTexCoord')
            tc.name = 'BK_fab_texco'
            tc.location = (-920, 220)
            nse = nt.nodes.new('ShaderNodeTexNoise')
            nse.name = 'BK_fabric_noise'
            nse.location = (-720, 220)
            ramp = nt.nodes.new('ShaderNodeValToRGB')
            ramp.name = 'BK_fabric_ramp'
            ramp.location = (-500, 220)
            nt.links.new(tc.outputs['Object'], nse.inputs['Vector'])
            nt.links.new(nse.outputs['Fac'], ramp.inputs['Fac'])
            nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
            print('fabric: BK noise graph created')
        # Photo cerulean: deep blue, not electric; subtle value variation
        nse.inputs['Scale'].default_value = 140.0
        nse.inputs['Detail'].default_value = 12.0
        nse.inputs['Roughness'].default_value = 0.72
        if ramp and ramp.type == 'VALTORGB':
            ramp.color_ramp.elements[0].position = 0.28
            ramp.color_ramp.elements[0].color = (0.006, 0.055, 0.28, 1)
            ramp.color_ramp.elements[1].position = 0.72
            ramp.color_ramp.elements[1].color = (0.014, 0.11, 0.46, 1)
        b.inputs['Roughness'].default_value = 0.88
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 0.12
        if 'Sheen Weight' in b.inputs:
            b.inputs['Sheen Weight'].default_value = 0.55
        if 'Sheen Roughness' in b.inputs:
            b.inputs['Sheen Roughness'].default_value = 0.45
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.0
        m_blue[FLAG] = True
        print('fabric: rough 0.88, sheen 0.55, weave scale 140 (UNVERIFIED)')
else:
    print('MISSING CCOM_lounge_swivel_blue_20261015al')

# --------------------------------------------------------------------------
# 2) Chrome — subtler, brushed (photo is polished metal, not mirror ball)
# --------------------------------------------------------------------------
m_chrome = bpy.data.materials.get('CCOM_lounge_chrome_20261014z')
if m_chrome and m_chrome.use_nodes:
    b = bsdf(m_chrome)
    nt = m_chrome.node_tree
    if b:
        b.inputs['Base Color'].default_value = (0.55, 0.56, 0.58, 1.0)
        b.inputs['Metallic'].default_value = 1.0
        b.inputs['Roughness'].default_value = 0.32
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 0.5
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.08
            if 'Coat Roughness' in b.inputs:
                b.inputs['Coat Roughness'].default_value = 0.25
        # Light anisotropic-ish micro-scratch via noise → roughness if not already
        if not any(n.name == 'BK_chrome_rough' for n in nt.nodes):
            tc = nt.nodes.new('ShaderNodeTexCoord')
            tc.name = 'BK_chr_texco'
            tc.location = (-800, -80)
            nse = nt.nodes.new('ShaderNodeTexNoise')
            nse.name = 'BK_chrome_rough'
            nse.location = (-600, -80)
            nse.inputs['Scale'].default_value = 55.0
            nse.inputs['Detail'].default_value = 6.0
            nse.inputs['Roughness'].default_value = 0.55
            # Map noise Fac 0.22..0.42 into Roughness
            mapr = nt.nodes.new('ShaderNodeMapRange')
            mapr.name = 'BK_chrome_map'
            mapr.location = (-380, -80)
            mapr.inputs['From Min'].default_value = 0.0
            mapr.inputs['From Max'].default_value = 1.0
            mapr.inputs['To Min'].default_value = 0.22
            mapr.inputs['To Max'].default_value = 0.42
            nt.links.new(tc.outputs['Object'], nse.inputs['Vector'])
            nt.links.new(nse.outputs['Fac'], mapr.inputs['Value'])
            nt.links.new(mapr.outputs['Result'], b.inputs['Roughness'])
            print('chrome: BK roughness noise 0.22..0.42')
        m_chrome[FLAG] = True
        print('chrome: darker brushed metal (UNVERIFIED artistic)')
else:
    print('MISSING CCOM_lounge_chrome_20261014z')

# --------------------------------------------------------------------------
# 3) Seat proportions — milder toy block: thinner cushion, slightly lower seat,
#    thinner wings, slightly taller/flatter back shell. Keep xy footprints.
# --------------------------------------------------------------------------
n_seat = n_back = n_wing = n_stem = n_star = 0
for o in bpy.data.objects:
    if not o.name.startswith('CCOM_lounge_swivel') or not o.name.endswith('_20261015al'):
        continue
    # Idempotent: only apply once (flag on object)
    if o.get(FLAG):
        continue
    n = o.name
    if '_seat_' in n:
        # Was 0.10 thick @ z=FLOOR+0.43 centre → thin to ~0.07, drop 2 cm
        o.scale.z = float(o.scale.z) * 0.72
        o.location.z = float(o.location.z) - 0.02
        o.scale.x = float(o.scale.x) * 1.02
        o.scale.y = float(o.scale.y) * 0.96
        n_seat += 1
    elif '_back_' in n:
        # Slightly taller / thinner shell (photo high taper)
        o.scale.z = float(o.scale.z) * 1.06
        o.scale.y = float(o.scale.y) * 0.88  # thickness of shell
        o.scale.x = float(o.scale.x) * 1.04
        o.location.z = float(o.location.z) - 0.015
        n_back += 1
    elif '_wing' in n:
        # Arms less blocky — thinner + slightly lower
        o.scale.x = float(o.scale.x) * 0.78
        o.scale.z = float(o.scale.z) * 0.85
        o.scale.y = float(o.scale.y) * 0.95
        o.location.z = float(o.location.z) - 0.025
        n_wing += 1
    elif '_stem_' in n:
        o.scale.x = float(o.scale.x) * 0.85
        o.scale.y = float(o.scale.y) * 0.85
        n_stem += 1
    elif '_star' in n:
        # Star legs slightly thinner / longer reach reads less chunky
        o.scale.y = float(o.scale.y) * 0.82  # thickness of arm bar
        o.scale.z = float(o.scale.z) * 0.90
        n_star += 1
    elif '_foot' in n:
        o.scale.x = float(o.scale.x) * 0.90
        o.scale.y = float(o.scale.y) * 0.90
    o[FLAG] = True
    o['source'] = f'lounge swivel polish UNVERIFIED ({TAG})'

print('proportion polish seats', n_seat, 'backs', n_back, 'wings', n_wing,
      'stems', n_stem, 'stars', n_star)

# Scene flag
bpy.context.scene[FLAG] = True
bpy.context.scene['bk_lounge_chairs_script'] = TAG

print('TAG', TAG, 'done')
if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)
else:
    print('dry-run (pass --save)')

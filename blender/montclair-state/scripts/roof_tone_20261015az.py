"""2026-10-15 az: oblique roof hotness under the ax/ay soft light (UNVERIFIED artistic tone, not a light change).
Global sun/world/look recipe is NOT touched. Idempotent (node names AZ_roof_* / material flag az_roof_tone).
- Roof_tile_or_membrane (LiDAR roofs, membrane + tile): compress only bright albedo (v1 luminance 0.42->0.90 ->
  multiplier 1.00->0.74; v2 below), so red tile / dark roofs are unchanged and white membrane drops ~20-25%.
  Roughness floor 0.72 (single-ply membrane is matte), Specular IOR Level 0.5 -> 0.30.
- CCOM_east_wall_plug_z2_20261014z (up-facing junction fill reading as a hot white slab in the oblique): 0.88 -> 0.70 albedo, rough 0.7.
- v2 9:30 PM: luminance 0.35->0.85 -> x1.00->x0.60; v3 9:31 PM: 0.18->0.45 -> x1.00->x0.62 (re-runs retune the existing AZ nodes in place).
- Roof_penthouse_precast / CCOM_east_flat_roof*: specular 0.30, roughness floor 0.72 if unlinked.
Args after --: [--save]
"""
import bpy, sys
argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
SAVE = '--save' in argv

def principled(m):
    for n in m.node_tree.nodes:
        if n.bl_idname == 'ShaderNodeBsdfPrincipled':
            return n

LO, HI, MUL_HI = 0.18, 0.45, 0.50   # v4 (9:32 PM; v3 had 0.62): v1 0.42/0.90/0.74 and v2 0.35/0.85/0.60 barely moved the oblique (membrane albedo is mid-grey, lit hot) — red tile lum ~0.18 stays x1.0
def retune(m):
    nt = m.node_tree; mr = nt.nodes.get('AZ_roof_range')
    if mr:
        mr.inputs['From Min'].default_value = LO; mr.inputs['From Max'].default_value = HI; mr.inputs['To Max'].default_value = MUL_HI
        return 'retuned'
    return 'flagged'
def tone_bright(m, lo=LO, hi=HI, mul_hi=MUL_HI, rough_floor=0.72, spec=0.30):
    if not (m and m.use_nodes): return 'skip'
    if m.get('az_roof_tone'): return retune(m)
    nt = m.node_tree; p = principled(m)
    if p is None: return 'nobsdf'
    bc = p.inputs['Base Color']
    if bc.is_linked:
        src = bc.links[0].from_socket
        bw = nt.nodes.new('ShaderNodeRGBToBW'); bw.name = 'AZ_roof_bw'
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.name = 'AZ_roof_range'; mr.clamp = True
        mr.inputs['From Min'].default_value = lo; mr.inputs['From Max'].default_value = hi
        mr.inputs['To Min'].default_value = 1.0; mr.inputs['To Max'].default_value = mul_hi
        mx = nt.nodes.new('ShaderNodeMix'); mx.name = 'AZ_roof_tone_mul'; mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
        mx.inputs['Factor'].default_value = 1.0
        nt.links.new(src, bw.inputs['Color']); nt.links.new(bw.outputs['Val'], mr.inputs['Value'])
        nt.links.new(src, mx.inputs[6]); nt.links.new(mr.outputs['Result'], mx.inputs[7])
        nt.links.new(mx.outputs[2], bc)
        for k, n in enumerate((bw, mr, mx)):
            n.location = (p.location.x - 600 + 180 * k, p.location.y + 400)
    else:
        c = list(bc.default_value); lum = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
        t = min(1, max(0, (lum - lo) / (hi - lo))); f = 1 + (mul_hi - 1) * t
        bc.default_value = (c[0] * f, c[1] * f, c[2] * f, c[3])
    r = p.inputs['Roughness']
    if r.is_linked:
        mx2 = nt.nodes.new('ShaderNodeMath'); mx2.name = 'AZ_roof_rough_floor'; mx2.operation = 'MAXIMUM'
        mx2.inputs[1].default_value = rough_floor
        nt.links.new(r.links[0].from_socket, mx2.inputs[0]); nt.links.new(mx2.outputs[0], r)
        mx2.location = (p.location.x - 200, p.location.y - 300)
    else:
        r.default_value = max(r.default_value, rough_floor)
    p.inputs['Specular IOR Level'].default_value = min(p.inputs['Specular IOR Level'].default_value, spec)
    m['az_roof_tone'] = 1
    return 'ok'

res = {}
for mn in ('Roof_tile_or_membrane', 'Roof_penthouse_precast', 'CCOM_east_flat_roof_20261014y', 'CCOM_east_flat_roof_z_20261014z',
           'HouseProxy_FlatRoof_membrane_20261014ad'):
    m = bpy.data.materials.get(mn)
    if m and not m.library: res[mn] = tone_bright(m)
m = bpy.data.materials.get('CCOM_east_wall_plug_z2_20261014z')
if m and not m.library:
    p = principled(m); p.inputs['Base Color'].default_value = (0.70, 0.685, 0.645, 1.0)
    p.inputs['Roughness'].default_value = 0.70; p.inputs['Specular IOR Level'].default_value = 0.35
    m['az_roof_tone'] = 1; res[m.name] = 'ok'
print('AZ_ROOF_TONE', res)
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED', bpy.data.filepath)
# v4: per-camera exposure delta (like ay's ay_exposure_delta) on the high oblique where roofs fill the top third; AgX compresses
# highlights so the material change alone moves the roofs only ~4% in display values. Render scripts read az_exposure_delta.
for cn, dv in (('CAM_oblique_CCOM_east_jf', -0.2),):
    c = bpy.data.objects.get(cn)
    if c: c['az_exposure_delta'] = dv; print('EXPO_DELTA', cn, dv)
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED2', bpy.data.filepath)

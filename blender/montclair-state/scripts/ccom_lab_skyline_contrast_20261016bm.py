"""2026-10-16 bm: CCOM lab-window NYC skyline readability (LOCAL to montclair_state.blend).

Finding: the NJ/NY backdrop is a collection instance (`NJ_NY_backdrop_instance`) of the linked
`assets/nj_ny_backdrop.blend`; its BD_* materials are library data, so the earlier local nudges
(am/aw make_local) created orphan copies that were dropped on save -> asset values still active
(DIV -120000, CLAMP 0.28, dark blue emission haze = 'haze' that darkened instead of fading).

This script (idempotent, rerunnable):
 1. builds a LOCAL realised copy of the backdrop in collection `NJ_NY_backdrop_local_bm`
    (object/mesh copies at the IDENTICAL world matrix: instance_matrix @ T(-offset) @ obj matrix;
    bearings/distances/heights unchanged = MEASURED as built) with local `<mat>_bm` materials;
 2. hides the linked instance empty (hide_render/hide_viewport; asset file untouched);
 3. tower mats: more diffuse (sun/shadow face split instead of a uniform sky reflection),
    aerial perspective = mix(BSDF, Transparent) so far faces fade TOWARD THE SKY behind them,
    with a height term (bases hazier than tops). UNVERIFIED artistic tuning vs Joe's photo;
 4. adds `CAM_closeup_CCOM_lab_skyline_bm` (same eye point as CAM_eye_CCOM_lab_skyline, longer lens
    ~ Joe's zoomed old_office_window_view_city.jpg framing).
Global soft-light recipe (sun 3.5 deg / energy / world strength / AgX - Base Contrast) NOT touched.
Env: SAVE=1 to save. Tunables via env: HZ_D, HZ_MAX, HZ_TOPK.
"""
import bpy, os, math
from mathutils import Matrix

FLAG = 'bm_lab_skyline_contrast'
COLN = 'NJ_NY_backdrop_local_bm'
HZ_D = float(os.environ.get('HZ_D', '60000'))      # e-folding distance (m)
HZ_MAX = float(os.environ.get('HZ_MAX', '0.50'))    # max transparency toward sky
HZ_TOPK = float(os.environ.get('HZ_TOPK', '0.60'))  # haze multiplier at tower tops (z>=HZ_ZTOP)
HZ_ZTOP = 420.0
SUN_LO = float(os.environ.get('SUN_LO', '0.80'))   # albedo mult on faces turned away from the sun
SUN_HI = float(os.environ.get('SUN_HI', '1.35'))   # albedo mult on sun-facing faces

TWEAK = {  # base, rough, spec(IOR level)
    'BD_glass_tower':  ((0.16, 0.21, 0.31, 1), 0.45, 0.32),
    'BD_stone_tower':  ((0.50, 0.46, 0.40, 1), 0.72, 0.30),
    'BD_fill_massing': ((0.36, 0.36, 0.37, 1), 0.78, 0.25),
    'BD_steel':        ((0.44, 0.46, 0.50, 1), 0.45, 0.40),
    'BD_white_roof':   ((0.58, 0.58, 0.57, 1), 0.70, 0.30),
}

sc = bpy.context.scene
inst = bpy.data.objects.get('NJ_NY_backdrop_instance')
assert inst and inst.instance_collection, 'backdrop instance missing'
src = inst.instance_collection

# ---- 1. clean previous run
old = bpy.data.collections.get(COLN)
if old:
    for o in list(old.all_objects):
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users == 0:
            bpy.data.meshes.remove(me)
    bpy.data.collections.remove(old)
for m in list(bpy.data.materials):
    if m.name.endswith('_bm') and m.name.startswith('BD_') and m.users == 0:
        bpy.data.materials.remove(m)

col = bpy.data.collections.new(COLN)
sc.collection.children.link(col)
base_m = inst.matrix_world @ Matrix.Translation(-src.instance_offset)

matmap = {}
def local_mat(m):
    if m is None:
        return None
    if m.name not in matmap:
        lm = bpy.data.materials.get(m.name + '_bm')
        if lm is None or lm.library is not None:
            lm = m.copy(); lm.name = m.name + '_bm'
        matmap[m.name] = lm
    return matmap[m.name]

n = 0
for o in src.all_objects:
    if o.type != 'MESH':
        continue
    mw = base_m @ o.matrix_world
    no = o.copy()
    no.data = o.data.copy()
    no.parent = None
    no.matrix_world = mw
    for i, m in enumerate(no.data.materials):
        no.data.materials[i] = local_mat(m)
    no['bm_src'] = o.name
    col.objects.link(no)
    n += 1
print('LOCAL COPY', n, 'objects; mats', sorted(matmap))

# ---- 2. hide linked instance (asset untouched)
inst.hide_render = True
inst.hide_viewport = True
inst['bm_hidden_by'] = COLN

# ---- 3. materials
def find(nt, typ):
    return [x for x in nt.nodes if x.type == typ]

_sun = [o for o in bpy.data.objects if o.type == 'LIGHT' and o.data.type == 'SUN'][0]
SUN_DIR = tuple((_sun.matrix_world.to_quaternion() @ __import__('mathutils').Vector((0, 0, 1))).normalized())
print('SUN_DIR (toward sun)', [round(v, 3) for v in SUN_DIR])

for name, lm in matmap.items():
    nt = lm.node_tree
    def get(nm, typ, nt=nt):
        x = nt.nodes.get(nm)
        if x is None:
            x = nt.nodes.new(typ); x.name = nm
        return x
    b = find(nt, 'BSDF_PRINCIPLED')[0]
    if name == 'BD_ground_fan':
        continue  # ground plane = Joe's open question; keep asset look
    if name == 'BD_farfield_ortho_haze':
        continue
    tw = TWEAK.get(name)
    if tw:
        b.inputs['Base Color'].default_value = tw[0]
        b.inputs['Roughness'].default_value = tw[1]
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = tw[2]
    if tw:
        # sun-facing albedo split (local stand-in for the face contrast in Joe's photo; UNVERIFIED)
        rgb = get('bm_base', 'ShaderNodeRGB'); rgb.outputs[0].default_value = tw[0]
        dot = get('bm_sundot', 'ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'
        dot.inputs[1].default_value = SUN_DIR
        smr = get('bm_sunmap', 'ShaderNodeMapRange'); smr.clamp = True
        smr.inputs['From Min'].default_value = -0.2; smr.inputs['From Max'].default_value = 0.8
        smr.inputs['To Min'].default_value = SUN_LO; smr.inputs['To Max'].default_value = SUN_HI
        sm = get('bm_sunmul', 'ShaderNodeVectorMath'); sm.operation = 'SCALE'
        g0 = get('bm_geo', 'ShaderNodeNewGeometry')
        nt.links.new(g0.outputs['Normal'], dot.inputs[0])
        nt.links.new(dot.outputs['Value'], smr.inputs['Value'])
        nt.links.new(rgb.outputs[0], sm.inputs[0])
        nt.links.new(smr.outputs['Result'], sm.inputs['Scale'])
        nt.links.new(sm.outputs['Vector'], b.inputs['Base Color'])
    mix = find(nt, 'MIX_SHADER')[0]
    clamp = find(nt, 'CLAMP')[0]
    for x in nt.nodes:
        if x.type == 'MATH' and x.operation == 'DIVIDE' and not x.inputs[1].is_linked:
            x.inputs[1].default_value = -HZ_D
    clamp.inputs['Max'].default_value = 1.0
    # height term: fac * maprange(z, 0..ZTOP -> 1..TOPK), then clamp to HZ_MAX
    geo = get('bm_geo', 'ShaderNodeNewGeometry')
    sep = get('bm_sepz', 'ShaderNodeSeparateXYZ')
    mr = get('bm_zmap', 'ShaderNodeMapRange')
    mul = get('bm_mul', 'ShaderNodeMath'); mul.operation = 'MULTIPLY'
    mn = get('bm_min', 'ShaderNodeMath'); mn.operation = 'MINIMUM'
    tr = get('bm_transp', 'ShaderNodeBsdfTransparent')
    mr.inputs['From Min'].default_value = 0.0
    mr.inputs['From Max'].default_value = HZ_ZTOP
    mr.inputs['To Min'].default_value = 1.0
    mr.inputs['To Max'].default_value = HZ_TOPK
    mr.clamp = True
    mn.inputs[1].default_value = HZ_MAX
    L = nt.links
    L.new(geo.outputs['Position'], sep.inputs[0])
    L.new(sep.outputs['Z'], mr.inputs['Value'])
    L.new(clamp.outputs['Result'], mul.inputs[0])
    L.new(mr.outputs['Result'], mul.inputs[1])
    L.new(mul.outputs[0], mn.inputs[0])
    L.new(mn.outputs[0], mix.inputs['Fac'])
    L.new(b.outputs['BSDF'], mix.inputs[1])
    L.new(tr.outputs['BSDF'], mix.inputs[2])
    lm[FLAG] = f'D{HZ_D:.0f}_max{HZ_MAX}_top{HZ_TOPK}_sun{SUN_LO}-{SUN_HI}'
    print('MAT', lm.name, 'tweak', tw, 'haze->transparent D', HZ_D, 'max', HZ_MAX, 'topk', HZ_TOPK)

# ---- 4. tighter skyline close-up cam (same eye point)
c0 = bpy.data.objects['CAM_eye_CCOM_lab_skyline']
cn = bpy.data.objects.get('CAM_closeup_CCOM_lab_skyline_bm')
if cn is None:
    cn = c0.copy(); cn.data = c0.data.copy(); cn.name = 'CAM_closeup_CCOM_lab_skyline_bm'
    cn.data.name = cn.name
    for cc in c0.users_collection:
        cc.objects.link(cn)
cn.matrix_world = c0.matrix_world.copy()
cn.data.lens = 115.0
cn.data.clip_end = max(c0.data.clip_end, 60000.0)
cn['bm_note'] = 'same eye point as CAM_eye_CCOM_lab_skyline; lens 115 ~ Joe zoomed photo framing'

sc[FLAG] = f'v2 sun{SUN_LO}-{SUN_HI} local backdrop {n} objs; D{HZ_D:.0f} max{HZ_MAX} top{HZ_TOPK}'

# ---- read-only soft-light check
sun = [o for o in bpy.data.objects if o.type == 'LIGHT' and o.data.type == 'SUN']
print('SOFTLIGHT', [(s.name, round(s.data.energy, 4), round(math.degrees(s.data.angle), 2)) for s in sun],
      [round(x.inputs['Strength'].default_value, 4) for x in sc.world.node_tree.nodes if x.type == 'BACKGROUND'],
      sc.view_settings.view_transform, sc.view_settings.look)

if os.environ.get('SAVE') == '1':
    bpy.ops.wm.save_mainfile()
    print('SAVED')
print('BM DONE')

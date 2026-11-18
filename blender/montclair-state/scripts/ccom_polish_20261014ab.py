"""2026-10-14 ~9:20 PM ET, tag 20261014ab.
One-pass CCOM polish: wall-patch tone match at equipment entrance + small diffusion polish
(lab shade hem variation, raised-box concrete darken). No new architecture / furniture.
RERUNNABLE. --save to write."""
import bpy, bmesh, math, sys, os
from mathutils import Vector

SAVE = '--save' in sys.argv
TAG = '20261014ab'
# world frame from jf
P0 = Vector((26.30, -13.53, 0)); D = Vector((0.2442, 0.9697, 0)); N = Vector((0.9697, -0.2442, 0))
def W(t, s, z):
    return Vector((P0.x + D.x * t + N.x * s, P0.y + D.y * t + N.y * s, z))
def ts(p):
    q = Vector((p.x, p.y, 0)) - P0; return q.dot(D), q.dot(N)

WALL = -13.8
DOCK = 137.55
FLOOR = 139.067
CEIL = 142.62
# lab bay from jf2
LAB_T0, LAB_T1 = 9.8, 18.6
LAB_S = 3.33  # recessed bay wall offset used in glazing local frames — shades use relative s

def mat_plain(name, rgba, rough=0.5, alpha=1.0, trans=0.0, emit=0.0, ior=1.45, spec=0.5):
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

def mat_stucco_noise(name, base_rgb, rough=0.85):
    """Slightly darker stucco with procedural noise → bump for patch tone match."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (600, 0)
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location = (350, 0)
    texc = nt.nodes.new('ShaderNodeTexCoord'); texc.location = (-600, 0)
    mapn = nt.nodes.new('ShaderNodeMapping'); mapn.location = (-400, 0)
    mapn.inputs['Scale'].default_value = (2.4, 2.4, 2.4)
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.location = (-200, 80)
    noise.inputs['Scale'].default_value = 18.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.55
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.location = (0, 120)
    # base slightly darker than aa (0.80,0.79,0.75); noise modulates ±~0.04
    c0 = (base_rgb[0] - 0.04, base_rgb[1] - 0.04, base_rgb[2] - 0.035, 1)
    c1 = (base_rgb[0] + 0.02, base_rgb[1] + 0.02, base_rgb[2] + 0.015, 1)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = c0
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = c1
    bump = nt.nodes.new('ShaderNodeBump'); bump.location = (150, -80)
    bump.inputs['Strength'].default_value = 0.12
    bump.inputs['Distance'].default_value = 0.02
    nt.links.new(texc.outputs['Object'], mapn.inputs['Vector'])
    nt.links.new(mapn.outputs['Vector'], noise.inputs['Vector'])
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = rough
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.25
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    m.blend_method = 'OPAQUE'
    return m

def box(name, col, m, t0, t1, s0, s1, z0, z1):
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

def sample_neighbor_stucco():
    """Prefer real facade stucco albedo if present; else fall back."""
    candidates = [
        'Parapet_stucco', 'Stucco_band_white', 'CCOM_stucco', 'Building_stucco',
        'CCOM_east_pier_20261014jf', 'CCOM_equip_stucco_patch_20261014aa',
    ]
    found = []
    for nm in candidates:
        m = bpy.data.materials.get(nm)
        if not m or not m.use_nodes:
            continue
        for nd in m.node_tree.nodes:
            if nd.type == 'BSDF_PRINCIPLED':
                c = tuple(nd.inputs['Base Color'].default_value[:3])
                r = float(nd.inputs['Roughness'].default_value)
                found.append((nm, c, r))
                break
    # also scan any material with 'stucco' / 'plaster' in name used on CCOM walls
    for m in bpy.data.materials:
        low = m.name.lower()
        if 'stucco' in low or 'plaster' in low or 'parapet' in low:
            if any(f[0] == m.name for f in found):
                continue
            if m.use_nodes:
                for nd in m.node_tree.nodes:
                    if nd.type == 'BSDF_PRINCIPLED':
                        c = tuple(nd.inputs['Base Color'].default_value[:3])
                        r = float(nd.inputs['Roughness'].default_value)
                        found.append((m.name, c, r))
                        break
    print('STUCCO_CANDIDATES', found[:12])
    # Prefer mid-tone cream (~0.72-0.78) over bright whites
    best = None
    for nm, c, r in found:
        mean = sum(c) / 3
        if 0.55 <= mean <= 0.78:
            best = (nm, c, r)
            break
    if best is None and found:
        # take darkest among samples under 0.85 mean
        dark = [(nm, c, r) for nm, c, r in found if sum(c) / 3 < 0.85]
        best = min(dark, key=lambda x: sum(x[1]) / 3) if dark else found[0]
    return best

# --------------------------------------------------------------------------
# 0) west atrium lounge stays hidden
# --------------------------------------------------------------------------
wc = bpy.data.collections.get('CCOM_lounge_20261014z')
if wc:
    wc.hide_render = True; wc.hide_viewport = True
    print('west lounge hidden')

# --------------------------------------------------------------------------
# 1) MUST: wall-patch tone fix (equip entrance)
# NOTE: follow-up ccom_polish_20261014ab_patchfix.py assigns Wall_SCM_precast copy (renders showed noise-only still pale).
# --------------------------------------------------------------------------
neigh = sample_neighbor_stucco()
if neigh:
    nm, base_rgb, rough_n = neigh
    # go slightly darker than neighbor / than aa 0.80 if neighbor is pale
    mean = sum(base_rgb) / 3
    if mean > 0.78:
        base_rgb = (0.72, 0.71, 0.67)
        rough_n = 0.86
        print('neighbor pale; using darkened target', base_rgb)
    else:
        # nudge 3% darker than sampled neighbor so patches don't read as bright plates
        base_rgb = (base_rgb[0] * 0.97, base_rgb[1] * 0.97, base_rgb[2] * 0.97)
        rough_n = max(0.82, rough_n)
        print('using neighbor', nm, '→', base_rgb, 'rough', rough_n)
else:
    base_rgb = (0.72, 0.71, 0.67); rough_n = 0.86
    print('no neighbor; fallback', base_rgb)

m_stuc = mat_stucco_noise('CCOM_equip_stucco_patch_' + TAG, base_rgb, rough=rough_n)

# also tone pier mat (still used by some heads/backs) to same mean color (no noise on shared pier)
m_pier = bpy.data.materials.get('CCOM_east_pier_20261014jf')
if m_pier and m_pier.use_nodes:
    for nd in m_pier.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            nd.inputs['Base Color'].default_value = (*base_rgb, 1)
            nd.inputs['Roughness'].default_value = rough_n
            print('pier mat retuned', base_rgb)

# reassign wallpatch / wallhead / wallback
dcol = bpy.data.collections.get('CCOM_loading_dock_20261014jf3')
n_re = 0
if dcol:
    for o in dcol.objects:
        if any(k in o.name for k in ('wallpatch', 'wallhead', 'wallback')):
            if o.data and o.material_slots:
                o.material_slots[0].material = m_stuc
            elif o.data:
                o.data.materials.clear(); o.data.materials.append(m_stuc)
            n_re += 1
print('wall patches reassigned', n_re, 'to', m_stuc.name)
# Prefer real CCOM plaster (Wall_SCM_precast) so patches share texture with facade
src_wall = bpy.data.materials.get('Wall_SCM_precast')
if src_wall and dcol:
    m_match = bpy.data.materials.get('CCOM_equip_wall_match_' + TAG)
    if m_match is None:
        m_match = src_wall.copy(); m_match.name = 'CCOM_equip_wall_match_' + TAG
        nt = m_match.node_tree
        bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
        links = list(bsdf.inputs['Base Color'].links)
        hs = nt.nodes.get('AB_Darken') or nt.nodes.new('ShaderNodeHueSaturation')
        hs.name = 'AB_Darken'; hs.location = (-150, 200)
        hs.inputs['Value'].default_value = 0.90
        hs.inputs['Saturation'].default_value = 1.05
        if links:
            fr = links[0].from_socket; nt.links.remove(links[0])
            nt.links.new(fr, hs.inputs['Color'])
        else:
            hs.inputs['Color'].default_value = bsdf.inputs['Base Color'].default_value
        nt.links.new(hs.outputs['Color'], bsdf.inputs['Base Color'])
    n2 = 0
    for o in dcol.objects:
        if any(k in o.name for k in ('wallpatch', 'wallhead', 'wallback')):
            if o.data and o.material_slots:
                o.material_slots[0].material = m_match
            elif o.data:
                o.data.materials.clear(); o.data.materials.append(m_match)
            n2 += 1
    print('wall patches upgraded to Wall_SCM_precast copy', n2, m_match.name)


# confirm 1+1 doors unchanged
n_roll = sum(1 for o in (dcol.objects if dcol else [])
             if 'rolldoor_20261014jf3' in o.name and 'slat' not in o.name
             and 'hood' not in o.name and 'jamb' not in o.name)
n_pers = sum(1 for o in (dcol.objects if dcol else [])
             if o.name.startswith('CCOM_equip_persdoor_20261014jf3'))
print('doors roll=', n_roll, 'pers=', n_pers)

# --------------------------------------------------------------------------
# 2a) Lab shade hem height variation across panes
# --------------------------------------------------------------------------
# jf2 shifted P0 by +3.33 along N before building shades — mutate Z in place so XY stays correct.
gcol = bpy.data.collections.get('CCOM_east_glazing_20261014jf2')
prefix = 'CCOM_lab2_ftc_20261014jf2_'
HEM_OFFS = [0.00, 0.18, 0.08, 0.28, 0.05, 0.22, 0.12, 0.32]  # vs old alternate 0/0.12
shade_base = 141.05
z_top = CEIL - 0.05
shade_objs = sorted(
    [o for o in (gcol.objects if gcol else [])
     if o.name.startswith(prefix + 'shade') and o.type == 'MESH'],
    key=lambda o: o.name)
bar_by_i = {}
for o in (gcol.objects if gcol else []):
    if o.name.startswith(prefix + 'bar') and o.type == 'MESH':
        try:
            bar_by_i[int(o.name[len(prefix + 'bar'):])] = o
        except ValueError:
            pass
print('found lab2 shades', len(shade_objs), [o.name for o in shade_objs])

def set_z_span(ob, z_lo, z_hi):
    """Keep XY; remap mesh Z so min->z_lo, max->z_hi (object space = world for these boxes)."""
    zs = [v.co.z for v in ob.data.vertices]
    zmin, zmax = min(zs), max(zs)
    if abs(zmax - zmin) < 1e-6:
        return
    for v in ob.data.vertices:
        # bottom face cluster -> z_lo; top cluster -> z_hi
        t = 0.0 if abs(v.co.z - zmin) < abs(v.co.z - zmax) else 1.0
        v.co.z = z_lo + t * (z_hi - z_lo)
    ob.data.update()

for i, sh in enumerate(shade_objs):
    zb = shade_base + HEM_OFFS[i % len(HEM_OFFS)]
    set_z_span(sh, zb, z_top)
    bar = bar_by_i.get(i)
    if bar is None:
        # try match by index in name shadeN
        try:
            idx = int(sh.name.split('shade')[-1])
            bar = bar_by_i.get(idx)
        except ValueError:
            bar = None
    if bar:
        set_z_span(bar, zb - 0.03, zb)
    print('shade', sh.name, 'hem_z', round(zb, 3))
print('lab shade hems varied', [shade_base + HEM_OFFS[i % len(HEM_OFFS)] for i in range(len(shade_objs))])

# --------------------------------------------------------------------------
# 2b) Raised-box / grade concrete still slightly chalky — darken a touch
# --------------------------------------------------------------------------
m_grade = bpy.data.materials.get('CCOM_grade_concrete_20261014jf')
if m_grade and m_grade.use_nodes:
    for nd in m_grade.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            # was 0.52 after aa; nudge to ~0.46
            nd.inputs['Base Color'].default_value = (0.46, 0.45, 0.42, 1)
            nd.inputs['Roughness'].default_value = 0.92
            print('raised-box / grade concrete darkened further')

# optional: platform concrete one more notch if still pale
m_conc = bpy.data.materials.get('CCOM_dock_concrete_20261014jf3')
if m_conc and m_conc.use_nodes:
    for nd in m_conc.node_tree.nodes:
        if nd.type == 'BSDF_PRINCIPLED':
            nd.inputs['Base Color'].default_value = (0.50, 0.49, 0.46, 1)
            nd.inputs['Roughness'].default_value = 0.90
            print('platform concrete nudged')

# --------------------------------------------------------------------------
# Cams for WIP (equip patch close-up + keep aa cams)
# --------------------------------------------------------------------------
cam('CAM_closeup_CCOM_equip_patch_ab', W(-24.2, -16.8, DOCK + 1.55), W(WALL, -15.5, DOCK + 1.6), 35)
cam('CAM_closeup_CCOM_equip_entry_aa', W(-24.5, -15.5, DOCK + 1.4), W(WALL, -16.5, DOCK + 1.5), 32)
# keep lounge eye usable
cam('CAM_eye_CCOM_lounge_east', W(-8.5, -6.8, 134.85 + 1.65), W(-8.5, 25, 134.85 + 4.0), 20)

print('TAG', TAG, 'polish done')
if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED')
else:
    print('dry-run (pass --save)')

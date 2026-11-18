import os, sys
"""Assemble montclair_state.blend from data/geom.npz. Run: blender -b --factory-startup --python scripts/build_scene.py"""
import bpy, bmesh, json, math, os, random
import numpy as np
from mathutils import Vector, Matrix
ROOT = '/workspace/nj-scenes/montclair-state'
G = np.load(f'{ROOT}/data/geom.npz'); M = json.load(open(f'{ROOT}/data/geom_meta.json'))
H = M['half_m']; LAT, LON = 40.8600, -74.1972
bpy.ops.wm.read_homefile(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'; sc.unit_settings.length_unit = 'METERS'
sc['crs'] = 'EPSG:6527 NAD83(2011) / New Jersey (ftUS); Blender m = (ftUS - origin) * 1200/3937; Z = NAVD88 (Geoid18) m'
sc['origin_E_ftUS'] = M['E0_ftUS']; sc['origin_N_ftUS'] = M['N0_ftUS']; sc['origin_latlon'] = '40.8600, -74.1972 (approx)'
def coll(name):
    c = bpy.data.collections.new(name); sc.collection.children.link(c); return c
def mesh_obj(name, V, F, col, mat=None, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(map(float, v)) for v in V], [], [tuple(map(int, f)) for f in F])
    me.validate(); me.update()
    if smooth: me.shade_smooth()
    o = bpy.data.objects.new(name, me); col.objects.link(o)
    if mat: me.materials.append(mat)
    return o
TEX = f'{ROOT}/textures'
def img(path, data=False):
    im = bpy.data.images.load(path, check_existing=True)
    if data: im.colorspace_settings.name = 'Non-Color'
    return im
def pbr(name, tid, scale, tint=None, rough_mul=1.0, box=True, bump=0.3):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    bsdf = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1/scale,)*3
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    def t(suffix, data):
        n = N.new('ShaderNodeTexImage'); n.image = img(f'{TEX}/{tid}/{tid}_1K-JPG_{suffix}.jpg', data)
        if box: n.projection = 'BOX'; n.projection_blend = 0.25
        L.new(mp.outputs['Vector'], n.inputs['Vector']); return n
    col = t('Color', False)
    if tint:
        mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1.0
        L.new(col.outputs['Color'], mx.inputs[6]); mx.inputs[7].default_value = (*tint, 1)
        L.new(mx.outputs[2], bsdf.inputs['Base Color'])
    else: L.new(col.outputs['Color'], bsdf.inputs['Base Color'])
    r = t('Roughness', True)
    mm = N.new('ShaderNodeMath'); mm.operation = 'MULTIPLY'; mm.inputs[1].default_value = rough_mul
    L.new(r.outputs['Color'], mm.inputs[0]); L.new(mm.outputs[0], bsdf.inputs['Roughness'])
    nm = t('NormalGL', True); nn = N.new('ShaderNodeNormalMap'); nn.inputs['Strength'].default_value = bump
    L.new(nm.outputs['Color'], nn.inputs['Color']); L.new(nn.outputs['Normal'], bsdf.inputs['Normal'])
    return m, nt, bsdf, mp
def rgb(name, c, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*c, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    return m
# ---------- terrain
c_ter = coll('Terrain')
Zt = G['terrain_z']; n = Zt.shape[0]; xs = -H + 0.5 + np.arange(n)
step = 1
idx = np.arange(0, n, step); m_ = len(idx)
gx, gy = np.meshgrid(xs[idx], xs[idx]); V = np.c_[gx.ravel(), gy.ravel(), Zt[np.ix_(idx, idx)].ravel()]
ii = np.arange(m_*m_).reshape(m_, m_)
F = np.c_[ii[:-1,:-1].ravel(), ii[:-1,1:].ravel(), ii[1:,1:].ravel(), ii[1:,:-1].ravel()]
me = bpy.data.meshes.new('terrain'); me.vertices.add(len(V)); me.vertices.foreach_set('co', V.astype(np.float32).ravel())
me.loops.add(F.size); me.loops.foreach_set('vertex_index', F.astype(np.int32).ravel())
me.polygons.add(len(F)); me.polygons.foreach_set('loop_start', np.arange(0, F.size, 4, dtype=np.int32))
me.update(); me.shade_smooth()
uv = me.uv_layers.new(name='ortho'); lv = F.ravel()
uvc = np.c_[(V[lv,0]+H)/(2*H), (V[lv,1]+H)/(2*H)].astype(np.float32); uv.data.foreach_set('uv', uvc.ravel())
ter = bpy.data.objects.new('Terrain_LiDAR_DTM_1m', me); c_ter.objects.link(ter)
mt, nt, bsdf, mp = pbr('Ground_ortho_grass', 'Grass004', 2.5, box=False, bump=0.6)
N = nt.nodes; L = nt.links
oi = N.new('ShaderNodeTexImage'); oi.image = img(f'{ROOT}/data/ortho2020.png'); oi.interpolation = 'Cubic'
uvn = N.new('ShaderNodeUVMap'); uvn.uv_map = 'ortho'; L.new(uvn.outputs['UV'], oi.inputs['Vector'])
grass_col = [l.from_node for l in bsdf.inputs['Base Color'].links][0]
sepc = N.new('ShaderNodeSeparateColor'); L.new(oi.outputs['Color'], sepc.inputs[0])
mxrb = N.new('ShaderNodeMath'); mxrb.operation = 'MAXIMUM'; L.new(sepc.outputs[0], mxrb.inputs[0]); L.new(sepc.outputs[2], mxrb.inputs[1])
gm = N.new('ShaderNodeMath'); gm.operation = 'SUBTRACT'; L.new(sepc.outputs[1], gm.inputs[0]); L.new(mxrb.outputs[0], gm.inputs[1])
gmr = N.new('ShaderNodeMapRange'); gmr.inputs[1].default_value = -0.005; gmr.inputs[2].default_value = 0.03; gmr.inputs[4].default_value = 0.75
L.new(gm.outputs[0], gmr.inputs[0])
hsv = N.new('ShaderNodeHueSaturation'); hsv.inputs['Value'].default_value = 0.8; hsv.inputs['Saturation'].default_value = 0.9
L.new(grass_col.outputs['Color'], hsv.inputs['Color'])
mul = N.new('ShaderNodeMix'); mul.data_type = 'RGBA'; L.new(gmr.outputs[0], mul.inputs[0])
L.new(oi.outputs['Color'], mul.inputs[6]); L.new(hsv.outputs['Color'], mul.inputs[7])
det = N.new('ShaderNodeMix'); det.data_type = 'RGBA'; det.blend_type = 'SOFT_LIGHT'; det.inputs[0].default_value = 0.5
L.new(mul.outputs[2], det.inputs[6]); L.new(grass_col.outputs['Color'], det.inputs[7]); L.new(det.outputs[2], bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value = 0.9
for l in list(bsdf.inputs['Roughness'].links): L.remove(l)
me.materials.append(mt)
# low-res skirt beyond the 500 m tile: 4 km x 4 km, USGS 3DEP 10 m DEM sampled every 40 m + NJ 2020 ortho at ~2 m/px (only seen from aerials)
_sk = f'{ROOT}/data/skirt_dem_10m.npy'
if os.path.exists(_sk):
    D = np.load(_sk); st = 4; Ds = D[st//2::st, st//2::st]; nr, nc_ = Ds.shape; S_ = 4000.0 / D.shape[0]
    xs_ = -2000 + (np.arange(nc_) * st + st/2 + 0.5) * S_; ys_ = 2000 - (np.arange(nr) * st + st/2 + 0.5) * S_
    gxs, gys = np.meshgrid(xs_, ys_); Zs = Ds.copy()
    Zs[(np.abs(gxs) < 262) & (np.abs(gys) < 262)] -= 1.5        # tuck the overlap under the 1 m tile
    Vs = np.c_[gxs.ravel(), gys.ravel(), Zs.ravel()]; ii_ = np.arange(nr * nc_).reshape(nr, nc_)
    Fs = np.c_[ii_[:-1, :-1].ravel(), ii_[1:, :-1].ravel(), ii_[1:, 1:].ravel(), ii_[:-1, 1:].ravel()]
    fc = Vs[Fs].mean(1); Fs = Fs[~((np.abs(fc[:, 0]) < 232) & (np.abs(fc[:, 1]) < 232))]
    sko = mesh_obj('Context_skirt_3DEP_ortho_4km', Vs, Fs, c_ter, smooth=True)
    uvs = sko.data.uv_layers.new(name='ortho'); lv_ = np.array([v for p in sko.data.polygons for v in p.vertices])
    uvs.data.foreach_set('uv', np.c_[(Vs[lv_, 0] + 2000) / 4000, (Vs[lv_, 1] + 2000) / 4000].astype(np.float32).ravel())
    msk = bpy.data.materials.new('Context_skirt_ortho'); msk.use_nodes = True; _n = msk.node_tree.nodes; _l = msk.node_tree.links
    _ti = _n.new('ShaderNodeTexImage'); _ti.image = img(f'{ROOT}/data/skirt_ortho_1k.jpg'); _uv = _n.new('ShaderNodeUVMap'); _uv.uv_map = 'ortho'
    _l.new(_uv.outputs['UV'], _ti.inputs['Vector']); _hs = _n.new('ShaderNodeHueSaturation'); _hs.inputs['Value'].default_value = 0.85
    _l.new(_ti.outputs['Color'], _hs.inputs['Color']); _l.new(_hs.outputs['Color'], _n['Principled BSDF'].inputs['Base Color']); _n['Principled BSDF'].inputs['Roughness'].default_value = 0.95
    sko.data.materials.append(msk); zmin_ctx = float(D.min()) - 5
    print('skirt faces', len(Fs))
else:
    zmin_ctx = Zt.min() - 3
gp = mesh_obj('Context_ground_beyond_data', [(-6000, -6000, zmin_ctx), (6000, -6000, zmin_ctx), (6000, 6000, zmin_ctx), (-6000, 6000, zmin_ctx)], [(0, 1, 2, 3)], c_ter,
             rgb('Context_ground', (0.06, 0.075, 0.04), 0.95))
# ---------- paths
c_path = coll('Paths_Roads_OSM')
m_pav, nt_p, bsdf_p, mp_p = pbr('Paving_concrete', 'Concrete034', 3.0, tint=(0.92, 0.9, 0.86), box=False, bump=0.4)
# 3h: campus walk polish — control joints every ~1.5 m, expansion joints, faint stains / leaf debris, slight edge wear
_Np = nt_p.nodes; _Lp = nt_p.links
_tc_p = [n for n in _Np if n.type == 'TEX_COORD'][0]
_sx_p = _Np.new('ShaderNodeSeparateXYZ'); _Lp.new(_tc_p.outputs['Object'], _sx_p.inputs[0])
def _pm(op, a, c=None):
    n_ = _Np.new('ShaderNodeMath'); n_.operation = op
    for i_, v_ in enumerate((a, c)):
        if v_ is None: continue
        if isinstance(v_, (int, float)): n_.inputs[i_].default_value = v_
        else: _Lp.new(v_, n_.inputs[i_])
    return n_.outputs[0]
# joints in object XY: control every 1.5 m (both axes), expansion every 6 m (wider, darker)
_jx = _pm('ABSOLUTE', _pm('SUBTRACT', _pm('FRACT', _pm('DIVIDE', _sx_p.outputs['X'], 1.5)), 0.5))
_jy = _pm('ABSOLUTE', _pm('SUBTRACT', _pm('FRACT', _pm('DIVIDE', _sx_p.outputs['Y'], 1.5)), 0.5))
_jxy = _pm('MINIMUM', _jx, _jy)
_ctrl = _pm('GREATER_THAN', _pm('SUBTRACT', 0.035, _jxy), 0.0)   # ~10 cm sawcut
_ex = _pm('ABSOLUTE', _pm('SUBTRACT', _pm('FRACT', _pm('DIVIDE', _sx_p.outputs['X'], 6.0)), 0.5))
_ey = _pm('ABSOLUTE', _pm('SUBTRACT', _pm('FRACT', _pm('DIVIDE', _sx_p.outputs['Y'], 6.0)), 0.5))
_exp = _pm('GREATER_THAN', _pm('SUBTRACT', 0.018, _pm('MINIMUM', _ex, _ey)), 0.0)
_joint = _pm('MULTIPLY', _pm('MAXIMUM', _ctrl, _exp), 0.0)   # 3h: off - axis-aligned shader joints crossed the walks diagonally; real grooves are meshes now
_jdark = _Np.new('ShaderNodeMix'); _jdark.data_type = 'RGBA'; _jdark.blend_type = 'MULTIPLY'; _jdark.inputs[0].default_value = 1.0
_jdark.inputs[7].default_value = (0.32, 0.30, 0.27, 1)   # control cut shade
_Lp.new(_joint, _jdark.inputs[0])
_base_p = [l.from_socket for l in bsdf_p.inputs['Base Color'].links][0]
_Lp.new(_base_p, _jdark.inputs[6])
# expansion joints a bit darker / wetter (second multiply when _exp)
_j2 = _Np.new('ShaderNodeMix'); _j2.data_type = 'RGBA'; _j2.blend_type = 'MULTIPLY'; _j2.inputs[0].default_value = 1.0
_j2.inputs[7].default_value = (0.42, 0.40, 0.37, 1)
_Lp.new(_joint, _j2.inputs[0]); _Lp.new(_jdark.outputs[2], _j2.inputs[6])
# faint organic stains + leaf-litter patches (large noise)
_nst = _Np.new('ShaderNodeTexNoise'); _nst.inputs['Scale'].default_value = 0.55; _nst.inputs['Detail'].default_value = 6; _nst.inputs['Roughness'].default_value = 0.65
_Lp.new(_tc_p.outputs['Object'], _nst.inputs['Vector'])
_stain_m = _pm('MULTIPLY', _pm('MAXIMUM', _pm('SUBTRACT', _nst.outputs['Fac'], 0.62), 0.0), 2.8)
_stain = _Np.new('ShaderNodeMix'); _stain.data_type = 'RGBA'; _stain.blend_type = 'MULTIPLY'; _stain.inputs[0].default_value = 1.0
_stain.inputs[7].default_value = (0.72, 0.68, 0.55, 1)   # tea / leaf tannin
_Lp.new(_stain_m, _stain.inputs[0]); _Lp.new(_j2.outputs[2], _stain.inputs[6])
_nlf = _Np.new('ShaderNodeTexNoise'); _nlf.inputs['Scale'].default_value = 2.4; _nlf.inputs['Detail'].default_value = 4
_Lp.new(_tc_p.outputs['Object'], _nlf.inputs['Vector'])
_leaf_m = _pm('MULTIPLY', _pm('MAXIMUM', _pm('SUBTRACT', _nlf.outputs['Fac'], 0.78), 0.0), 5.0)
_leaf = _Np.new('ShaderNodeMix'); _leaf.data_type = 'RGBA'; _leaf.blend_type = 'MIX'; _leaf.inputs[0].default_value = 1.0
_leaf.inputs[7].default_value = (0.38, 0.22, 0.06, 1)   # dried leaf flecks
_Lp.new(_leaf_m, _leaf.inputs[0]); _Lp.new(_stain.outputs[2], _leaf.inputs[6])
# slight edge wear: darken near paving boundary via AO (ambient occlusion node) — softens slab edges at contact
_ao_p = _Np.new('ShaderNodeAmbientOcclusion'); _ao_p.inputs['Distance'].default_value = 0.35
_ao_f = _pm('ADD', _pm('MULTIPLY', _pm('SUBTRACT', 1.0, _ao_p.outputs['AO']), 0.22), 0.78)
_wear = _Np.new('ShaderNodeMix'); _wear.data_type = 'RGBA'; _wear.blend_type = 'MULTIPLY'; _wear.inputs[0].default_value = 1.0
_wear.inputs[7].default_value = (0.85, 0.82, 0.78, 1)
_Lp.new(_ao_f, _wear.inputs[0]); _Lp.new(_leaf.outputs[2], _wear.inputs[6])
for l in list(bsdf_p.inputs['Base Color'].links): _Lp.remove(l)
_Lp.new(_wear.outputs[2], bsdf_p.inputs['Base Color'])
# deepen bump in the joint grooves
_nb = [n for n in _Np if n.type == 'NORMAL_MAP']
if _nb:
    _jbump = _pm('ADD', _nb[0].inputs['Strength'].default_value, _pm('MULTIPLY', _joint, 0.55))
    for l in list(_nb[0].inputs['Strength'].links): _Lp.remove(l)
    _Lp.new(_jbump, _nb[0].inputs['Strength'])
m_asp, *_ = pbr('Asphalt', 'Asphalt026B', 4.0, box=False, bump=0.5)
mesh_obj('Footpaths_OSM', G['paving_v'], G['paving_t'], c_path, m_pav)
mesh_obj('Roads_OSM', G['asphalt_v'], G['asphalt_t'], c_path, m_asp)
# ---------- building materials
m_roof, nt, bsdf, mp = pbr('Roof_tile_or_membrane', 'RoofingTiles006', 1.6, tint=(1.45, 0.60, 0.50), bump=0.9)  # terracotta, albedo matched to the Morehead Commons photo (RoofingTiles001 x tint read brown)
N = nt.nodes; L = nt.links
tile_col = [l.from_node for l in bsdf.inputs['Base Color'].links][0]
geo = N.new('ShaderNodeNewGeometry'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Normal'], sep.inputs[0])
mr = N.new('ShaderNodeMapRange'); mr.inputs[1].default_value = 0.93; mr.inputs[2].default_value = 0.97; L.new(sep.outputs['Z'], mr.inputs[0])
noise = N.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 0.4
memb = N.new('ShaderNodeMix'); memb.data_type = 'RGBA'; memb.inputs[6].default_value = (0.24, 0.235, 0.22, 1); memb.inputs[7].default_value = (0.32, 0.31, 0.29, 1)  # weathered membrane / gravel  # weathered membrane, not paper-white
L.new(noise.outputs['Fac'], memb.inputs[0])
rc = N.new('ShaderNodeAttribute'); rc.attribute_type = 'GEOMETRY'; rc.attribute_name = 'roofc'
inv = N.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; L.new(rc.outputs['Alpha'], inv.inputs[1])
fl = N.new('ShaderNodeMath'); fl.operation = 'MAXIMUM'; L.new(inv.outputs[0], fl.inputs[0]); L.new(mr.outputs[0], fl.inputs[1])
fl2 = N.new('ShaderNodeMath'); fl2.operation = 'LESS_THAN'; L.new(rc.outputs['Alpha'], fl2.inputs[0]); fl2.inputs[1].default_value = 0.02  # crisp tile/membrane edge (was a soft smear)
mcol = N.new('ShaderNodeMix'); mcol.data_type = 'RGBA'; mcol.blend_type = 'MULTIPLY'; mcol.inputs[0].default_value = 0.5
L.new(memb.outputs[2], mcol.inputs[6]); L.new(rc.outputs['Color'], mcol.inputs[7])  # membrane base, modulated by the ortho (was: ortho base -> too bright)
# white TPO where the ortho shows a bright membrane (CCOM, Life, Schmitt, CELS, ...): aged white sheets with seams, ponding stains, grime near units/parapets
def _m(op, a, c=None):
    n_ = N.new('ShaderNodeMath'); n_.operation = op
    for i_, v_ in enumerate((a, c)):
        if v_ is None: continue
        if isinstance(v_, (int, float)): n_.inputs[i_].default_value = v_
        else: L.new(v_, n_.inputs[i_])
    return n_.outputs[0]
_lum = N.new('ShaderNodeRGBToBW'); L.new(rc.outputs['Color'], _lum.inputs[0])
_wf = N.new('ShaderNodeAttribute'); _wf.attribute_type = 'OBJECT'; _wf.attribute_name = 'tpo'   # per roof: 0 dark membrane .. 1 white TPO (median ortho brightness of the membrane area; per-vertex gave blotches)
_tcw = N.new('ShaderNodeTexCoord'); _sxw = N.new('ShaderNodeSeparateXYZ'); L.new(_tcw.outputs['Object'], _sxw.inputs[0])
_ang = N.new('ShaderNodeAttribute'); _ang.attribute_type = 'OBJECT'; _ang.attribute_name = 'seam_angle'
_ua = _m('ADD', _m('MULTIPLY', _sxw.outputs['X'], _m('COSINE', _ang.outputs['Fac'])), _m('MULTIPLY', _sxw.outputs['Y'], _m('SINE', _ang.outputs['Fac'])))
_va = _m('SUBTRACT', _m('MULTIPLY', _sxw.outputs['Y'], _m('COSINE', _ang.outputs['Fac'])), _m('MULTIPLY', _sxw.outputs['X'], _m('SINE', _ang.outputs['Fac'])))
_seam = _m('GREATER_THAN', _m('ABSOLUTE', _m('SUBTRACT', _m('FRACT', _m('DIVIDE', _ua, 3.05)), 0.5)), 0.481)        # 10 ft rolls, ~12 cm welded laps (reads at aerial distance)
_seam2 = _m('GREATER_THAN', _m('ABSOLUTE', _m('SUBTRACT', _m('FRACT', _m('DIVIDE', _va, 30.5)), 0.5)), 0.4985)      # roll ends every 100 ft
_seams = _m('MAXIMUM', _seam, _seam2)
_pn = N.new('ShaderNodeTexNoise'); _pn.inputs['Scale'].default_value = 0.11; _pn.inputs['Detail'].default_value = 4; L.new(_tcw.outputs['Object'], _pn.inputs['Vector'])
_pond = N.new('ShaderNodeMapRange'); _pond.inputs[1].default_value = 0.57; _pond.inputs[2].default_value = 0.66; L.new(_pn.outputs['Fac'], _pond.inputs[0])
_rim = _m('MULTIPLY', _m('SUBTRACT', 1.0, _m('ABSOLUTE', _m('SUBTRACT', _m('MULTIPLY', _pond.outputs[0], 2.0), 1.0))), 0.6)   # darker tide line at the stain edge
_ao = N.new('ShaderNodeAmbientOcclusion'); _ao.inputs['Distance'].default_value = 2.5; _ao.samples = 8
_grime = _m('MINIMUM', _m('MULTIPLY', _m('SUBTRACT', 1.0, _ao.outputs['AO']), 2.2), 1.0)
_sn = N.new('ShaderNodeTexNoise'); _sn.inputs['Scale'].default_value = 1.6; _sn.inputs['Detail'].default_value = 6; L.new(_tcw.outputs['Object'], _sn.inputs['Vector'])
_wc = N.new('ShaderNodeMix'); _wc.data_type = 'RGBA'; L.new(_sn.outputs['Fac'], _wc.inputs[0]); _wc.inputs[6].default_value = (0.60, 0.60, 0.58, 1); _wc.inputs[7].default_value = (0.74, 0.74, 0.72, 1)   # aged white TPO
_c1 = N.new('ShaderNodeMix'); _c1.data_type = 'RGBA'; L.new(_m('MULTIPLY', _seams, 0.7), _c1.inputs[0]); L.new(_wc.outputs[2], _c1.inputs[6]); _c1.inputs[7].default_value = (0.42, 0.42, 0.40, 1)
_c2 = N.new('ShaderNodeMix'); _c2.data_type = 'RGBA'; L.new(_m('ADD', _m('MULTIPLY', _pond.outputs[0], 0.45), _rim), _c2.inputs[0]); L.new(_c1.outputs[2], _c2.inputs[6]); _c2.inputs[7].default_value = (0.40, 0.38, 0.33, 1)   # ponding stains
_c3 = N.new('ShaderNodeMix'); _c3.data_type = 'RGBA'; L.new(_grime, _c3.inputs[0]); L.new(_c2.outputs[2], _c3.inputs[6]); _c3.inputs[7].default_value = (0.30, 0.285, 0.25, 1)   # dirt near units, curbs, parapets
_mem = N.new('ShaderNodeMix'); _mem.data_type = 'RGBA'; _wv = N.new('ShaderNodeMapRange'); _wv.inputs[1].default_value = 0.12; _wv.inputs[2].default_value = 0.30; L.new(_lum.outputs[0], _wv.inputs[0])   # per-vertex: keeps dark sections (Sprague's south roof) dark
L.new(_m('MULTIPLY', _wf.outputs['Fac'], _wv.outputs[0]), _mem.inputs[0]); L.new(mcol.outputs[2], _mem.inputs[6]); L.new(_c3.outputs[2], _mem.inputs[7])
mcol = _mem   # downstream uses mcol.outputs[2]
flat_ = N.new('ShaderNodeMath'); flat_.operation = 'GREATER_THAN'; L.new(sep.outputs['Z'], flat_.inputs[0]); flat_.inputs[1].default_value = 0.985
fl3 = N.new('ShaderNodeMath'); fl3.operation = 'MAXIMUM'; L.new(fl2.outputs[0], fl3.inputs[0]); L.new(flat_.outputs[0], fl3.inputs[1])   # flat = membrane, sloped = tile
fin = N.new('ShaderNodeMix'); fin.data_type = 'RGBA'; L.new(fl3.outputs[0], fin.inputs[0]); L.new(tile_col.outputs[2], fin.inputs[6]); L.new(mcol.outputs[2], fin.inputs[7])
stp = N.new('ShaderNodeMath'); stp.operation = 'LESS_THAN'; L.new(sep.outputs['Z'], stp.inputs[0]); stp.inputs[1].default_value = 0.45
wfin = N.new('ShaderNodeMix'); wfin.data_type = 'RGBA'; L.new(stp.outputs[0], wfin.inputs[0]); L.new(fin.outputs[2], wfin.inputs[6]); wfin.inputs[7].default_value = (0.74, 0.73, 0.69, 1)
L.new(wfin.outputs[2], bsdf.inputs['Base Color'])   # near-vertical steps between roof levels are walls (stucco), not tile or membrane
m_eave = bpy.data.materials.new('Eave_tile_top_soffit_under'); m_eave.use_nodes = True
_N = m_eave.node_tree.nodes; _L = m_eave.node_tree.links; _b = _N['Principled BSDF']
_g = _N.new('ShaderNodeNewGeometry'); _s = _N.new('ShaderNodeSeparateXYZ'); _L.new(_g.outputs['Incoming'], _s.inputs[0])
_c = _N.new('ShaderNodeMath'); _c.operation = 'LESS_THAN'; _c.inputs[1].default_value = 0.0; _L.new(_s.outputs['Z'], _c.inputs[0])
_m = _N.new('ShaderNodeMix'); _m.data_type = 'RGBA'; _L.new(_c.outputs[0], _m.inputs[0])
_m.inputs[6].default_value = (0.42, 0.12, 0.06, 1); _m.inputs[7].default_value = (0.045, 0.024, 0.012, 1)  # dark brown soffit (Morehead photo)
_L.new(_m.outputs[2], _b.inputs['Base Color']); _b.inputs['Roughness'].default_value = 0.9; _b.inputs['Specular IOR Level'].default_value = 0.25
m_tile_course = rgb('Roof_barrel_tile_course', (0.42, 0.13, 0.07), 0.6)
_tn = m_tile_course.node_tree; _ta = _tn.nodes.new('ShaderNodeAttribute'); _ta.attribute_name = 'tcol'   # 3f: per-tile colour (weathered / replaced tiles)
_tn.links.new(_ta.outputs['Color'], _tn.nodes['Principled BSDF'].inputs['Base Color'])
# 3g: moss / dirt on the eave course and caps: patchy noise (world space), darker grey-green, ~15 % coverage
_tnz = _tn.nodes.new('ShaderNodeTexNoise'); _tnz.inputs['Scale'].default_value = 0.9; _tnz.inputs['Detail'].default_value = 6
_tnr = _tn.nodes.new('ShaderNodeMapRange'); _tnr.inputs['From Min'].default_value = 0.56; _tnr.inputs['From Max'].default_value = 0.7; _tnr.inputs['To Max'].default_value = 0.75
_tn.links.new(_tnz.outputs['Fac'], _tnr.inputs['Value'])
_tmx = _tn.nodes.new('ShaderNodeMix'); _tmx.data_type = 'RGBA'; _tmx.inputs[7].default_value = (0.055, 0.06, 0.03, 1)
_tn.links.new(_tnr.outputs['Result'], _tmx.inputs[0]); _tn.links.new(_ta.outputs['Color'], _tmx.inputs[6]); _tn.links.new(_tmx.outputs[2], _tn.nodes['Principled BSDF'].inputs['Base Color'])
CH = {}; EAVES = []
m_fascia = rgb('Eave_fascia_dark_wood', (0.05, 0.027, 0.014), 0.85); m_fascia.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value = 0.3
def wall_mat(name, tint, tid='Plaster001', frame=(0.05, 0.035, 0.025), frame_metal=0.0):
    m, nt, bsdf, mp = pbr(name, tid, 2.5, tint=tint, bump=0.35)
    N = nt.nodes; L = nt.links
    wall_col = [l.from_node for l in bsdf.inputs['Base Color'].links][0]
    uvn = N.new('ShaderNodeUVMap'); uvn.uv_map = 'facade'; sp = N.new('ShaderNodeSeparateXYZ'); L.new(uvn.outputs['UV'], sp.inputs[0])
    def attr(nm):
        a = N.new('ShaderNodeAttribute'); a.attribute_type = 'OBJECT'; a.attribute_name = nm; return a.outputs['Fac']
    def op(o, a, b=None):
        x = N.new('ShaderNodeMath'); x.operation = o
        for i, v in enumerate([a, b]):
            if v is None: continue
            if isinstance(v, (int, float)): x.inputs[i].default_value = v
            else: L.new(v, x.inputs[i])
        return x.outputs[0]
    def band(coord, period, width, shrink):
        f = op('FRACT', op('DIVIDE', coord, period))
        lo = op('DIVIDE', op('SUBTRACT', op('MULTIPLY', period, 0.5), op('SUBTRACT', op('MULTIPLY', width, 0.5), shrink)), period)
        hi = op('DIVIDE', op('ADD', op('MULTIPLY', period, 0.5), op('SUBTRACT', op('MULTIPLY', width, 0.5), shrink)), period)
        return op('MULTIPLY', op('GREATER_THAN', f, lo), op('LESS_THAN', f, hi))
    u = op('SUBTRACT', sp.outputs['X'], attr('win_u0')); v = sp.outputs['Y']
    pw, ww, fh, wh, wb, wt = attr('win_pitch'), attr('win_w'), attr('floor_h'), attr('win_h'), attr('win_bottom'), attr('win_top')
    vv = op('SUBTRACT', v, wb)
    inrange = op('MULTIPLY', op('GREATER_THAN', v, wb), op('LESS_THAN', v, wt))
    vrow = op('ADD', op('SUBTRACT', vv, op('MULTIPLY', wh, 0.5)), op('MULTIPLY', fh, 0.5))
    outer = op('MULTIPLY', op('MULTIPLY', band(u, pw, ww, 0.0), band(vrow, fh, wh, 0.0)), inrange)
    inner = op('MULTIPLY', op('MULTIPLY', band(u, pw, ww, 0.09), band(vrow, fh, wh, 0.09)), inrange)
    # mullion: vertical split in middle of window
    mull = op('LESS_THAN', op('ABSOLUTE', op('SUBTRACT', op('FRACT', op('DIVIDE', u, pw)), 0.5)), op('DIVIDE', attr('mull_w'), pw))
    mu = op('LESS_THAN', op('FRACT', op('DIVIDE', u, 0.27)), 0.09)
    mv = op('LESS_THAN', op('FRACT', op('DIVIDE', v, 0.31)), 0.08)
    munt = op('MULTIPLY', op('MAXIMUM', mu, mv), attr('muntin'))
    glass = op('MULTIPLY', op('MULTIPLY', inner, op('SUBTRACT', 1.0, mull)), op('SUBTRACT', 1.0, munt))
    gb = N.new('ShaderNodeBsdfPrincipled'); gb.inputs['Roughness'].default_value = 0.03
    gb.inputs['Specular IOR Level'].default_value = 1.0   # stronger sky reflection on the panes
    # per-window variation: a random value per window cell drives pane tint and part-drawn pale blinds (no two windows identical)
    cel = N.new('ShaderNodeCombineXYZ'); L.new(op('FLOOR', op('DIVIDE', u, pw)), cel.inputs[0]); L.new(op('FLOOR', op('DIVIDE', vrow, fh)), cel.inputs[1])
    wn_ = N.new('ShaderNodeTexWhiteNoise'); wn_.noise_dimensions = '3D'; L.new(cel.outputs[0], wn_.inputs['Vector'])
    rr = wn_.outputs['Value']; rc = N.new('ShaderNodeSeparateColor'); L.new(wn_.outputs['Color'], rc.inputs[0])
    tl = op('DIVIDE', op('SUBTRACT', op('MULTIPLY', op('FRACT', op('DIVIDE', vrow, fh)), fh), op('MULTIPLY', op('SUBTRACT', fh, wh), 0.5)), wh)   # 0..1 up the window
    cov = op('MULTIPLY', op('GREATER_THAN', rr, 0.45), op('ADD', 0.12, op('MULTIPLY', rc.outputs['Green'], 0.6)))
    blind = op('GREATER_THAN', tl, op('SUBTRACT', 1.0, cov))
    gmix = N.new('ShaderNodeMix'); gmix.data_type = 'RGBA'; L.new(blind, gmix.inputs['Factor'])
    dk = N.new('ShaderNodeMix'); dk.data_type = 'RGBA'; L.new(rc.outputs['Blue'], dk.inputs['Factor'])
    dk.inputs['A'].default_value = (0.022, 0.028, 0.034, 1); dk.inputs['B'].default_value = (0.045, 0.05, 0.05, 1)
    L.new(dk.outputs['Result'], gmix.inputs['A']); gmix.inputs['B'].default_value = (0.20, 0.19, 0.165, 1)
    L.new(gmix.outputs['Result'], gb.inputs['Base Color'])
    fr = N.new('ShaderNodeBsdfPrincipled'); fr.inputs['Base Color'].default_value = (*frame, 1); fr.inputs['Roughness'].default_value = 0.4; fr.inputs['Metallic'].default_value = frame_metal
    out = N['Material Output']
    m1 = N.new('ShaderNodeMixShader'); L.new(outer, m1.inputs[0]); L.new(bsdf.outputs[0], m1.inputs[1]); L.new(fr.outputs[0], m1.inputs[2])
    m2 = N.new('ShaderNodeMixShader'); L.new(glass, m2.inputs[0]); L.new(m1.outputs[0], m2.inputs[1]); L.new(gb.outputs[0], m2.inputs[2])
    L.new(m2.outputs[0], out.inputs['Surface'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Distance'].default_value = 0.08; bp.invert = True
    L.new(op('ADD', outer, inner), bp.inputs['Height']); L.new(bp.outputs['Normal'], gb.inputs['Normal']); L.new(bp.outputs['Normal'], fr.inputs['Normal'])
    return m
m_wall_stucco = wall_mat('Wall_stucco_mission', (0.93, 0.92, 0.88))
m_wall_scm = wall_mat('Wall_SCM_precast', (0.90, 0.87, 0.80), 'Plaster003', frame=(0.10, 0.10, 0.10), frame_metal=0.7)
# ---------- buildings
c_b = {k: coll(k) for k in ('Buildings_day1', 'Buildings_context')}
RV, RT, RB = G['roof_v'], G['roof_t'], G['roof_bid']; WV, WU, WB = G['wall_v'], G['wall_uv'], G['wall_bid']
cents = {}
sys.path.append('/workspace/nj-scenes/blender_pylib')
import shapely as _shp, json as _json
_SDF = {f['id']: f for f in _json.load(open(f'{ROOT}/data/scene_data.json'))['features']}
RA = G['roof_col'][:, 3].copy(); nflat = 0
EQ = {'pent': [], 'hvac': [], 'vent': [], 'parapet': [], 'coping': []}   # world-space boxes: (cx, cy, angle, sx, sy, z0, z1)
HIP_TARGET = 0.70   # tile pitch near the eave; the smoothed LiDAR DSM under-reads it (Morehead read 0.52, the Commons photo shows the tile above the soffit)
_rng_eq = random.Random(7)
def _signed_dist(poly, x, y):
    d = _shp.distance(poly.boundary, _shp.points(np.c_[x, y])); return np.where(_shp.contains_xy(poly, x, y), d, -d)
# Roof form per building, decided from the NJ 2020 ortho (footprint overlay /tmp/ortho_fp.jpg) and Commons photos; see LOG.md session 3d.
#   hip   = full red-tile hipped roof (no flat centre); strip = hip with a narrow flat strip along the ridge (half-width m); ring = tile ring + wide flat core
ROOF_FORM = {'312932811': ('hip', None),      # Susan A. Cole Hall: ortho all red tile (skylights only); Commons photos show full hipped tile roofs
             '312933183': ('lidar', None),    # Morehead Hall: LiDAR rises ~0.5/m to eave+3.3 m at 6.3 m in, then flat; ortho tile frac 0.6 in the first 4 m, 0.3 beyond 5 m -> wide tiled hip band + flat membrane core
             '313021866': ('ring', None),     # Life Hall: ortho tile ring around a wide white flat roof with HVAC
             '1188721159': ('ring', None),
             '312849089': ('split', None)}  # Kasser Theater: ortho = full tile hip over the auditorium/stage (E ~60 %), flat dark roof with skylights over the lobby (W)    # School of Communication and Media: ortho white flat roof, tile only at the edges
def clean_hip(vi, poly, eave_z, core_lv, form=None, z_pre=None):
    """Modelled tile roof: straight hip planes at HIP_TARGET pitch from the LiDAR eave, capped by the flat core level (or a ridge deck) - no LiDAR noise."""
    CH['last'] = None
    sd = _signed_dist(poly, RV[vi, 0], RV[vi, 1])
    if (sd < -1.5).mean() > 0.02:   # roof mesh covers more than this OSM outline (wings mapped separately): use the roof's own outline
        hull = _shp.concave_hull(_shp.MultiPoint(RV[vi, :2]), ratio=0.03).buffer(-0.6)
        if hull.geom_type == 'Polygon' and not hull.is_empty:
            poly = hull; sd = _signed_dist(poly, RV[vi, 0], RV[vi, 1]); print('CLEANHIP roof-outline fallback')
    sdm = float(sd.max())
    if form is not None and form[0] == 'split' and z_pre is not None:
        # tile part = hull of interior verts the ortho classifies as tile (3 m smoothed); hip on that part, flat at the LiDAR level elsewhere
        x_, y_ = RV[vi, 0], RV[vi, 1]; gk = (np.floor(x_ / 3).astype(np.int64) * 100000 + np.floor(y_ / 3).astype(np.int64))
        _, ginv = np.unique(gk, return_inverse=True); gs = np.bincount(ginv, RA[vi]); gc = np.bincount(ginv); ras = (gs / gc)[ginv]
        tpts = np.c_[x_, y_][(ras >= 0.5) & (sd > 2.0)]
        if len(tpts) < 30: print('SPLIT: too few tile points'); return core_lv
        hull = _shp.MultiPoint(tpts).convex_hull.buffer(1.0)
        fpart = poly.difference(hull).buffer(-2.5).buffer(2.5)            # flat part without the thin slivers along the outline
        pt_ = poly.difference(fpart).buffer(0)
        if pt_.geom_type != 'Polygon': pt_ = max(getattr(pt_, 'geoms', [pt_]), key=lambda g: g.area)
        pt_ = pt_.buffer(0.3).intersection(poly.buffer(1.5))
        if pt_.geom_type != 'Polygon': pt_ = max(getattr(pt_, 'geoms', [pt_]), key=lambda g: g.area)
        inside_t = _shp.contains_xy(pt_, x_, y_)
        # 3f: the hip only slopes down to the real outer walls; along the lobby side the tile part ends in a straight gable/step wall (no saw-tooth valley)
        _shared = pt_.exterior.intersection(fpart.buffer(0.8))
        _outer = pt_.exterior.difference(fpart.buffer(0.8))
        if _outer.is_empty: _outer = pt_.exterior
        sdt = _shp.distance(_outer, _shp.points(x_, y_)) * np.where(inside_t, 1.0, -1.0)
        if not _shared.is_empty:   # snap verts within 0.6 m of the step line onto it: the step becomes one straight vertical face
            _ds = _shp.distance(_shared, _shp.points(x_, y_)); _sn = np.nonzero((_ds < 0.6) & (sd > 0.5))[0]
            for _j in _sn:
                _pp = _shared.interpolate(_shared.project(_shp.Point(x_[_j], y_[_j]))); RV[vi[_j], 0] = _pp.x; RV[vi[_j], 1] = _pp.y
            print('SPLIT step snap', len(_sn))
        ridge = float(np.percentile(z_pre[inside_t & (sd > 0)], 98)); s_ = 0.6
        flat = float(np.median(z_pre[(~inside_t) & (sd > 2.0)])) if ((~inside_t) & (sd > 2.0)).sum() > 20 else eave_z + 3.0
        zt_ = np.minimum(eave_z + s_ * sdt, ridge)
        near_t = sdt > -0.8   # verts just outside the tile hull but inside the footprint belong to the flat part
        zf_ = np.where(inside_t, zt_, flat)
        key = np.round(RV[vi, 0] * 50).astype(np.int64) * 10_000_000 + np.round(RV[vi, 1] * 50).astype(np.int64)
        _, inv_ = np.unique(key, return_inverse=True); zmax = np.full(inv_.max() + 1, -1e9); np.maximum.at(zmax, inv_, RV[vi, 2])
        RV[vi, 2] = zf_ + (RV[vi, 2] - zmax[inv_]); RA[vi] = np.where(inside_t, 1.0, 0.0)
        print('ROOFFORM split: tile part', round(pt_.area), 'm2 of', round(poly.area), 'ridge', round(ridge - eave_z, 1), 'flat', round(flat - eave_z, 1))
        return flat
    if form is not None and form[0] in ('hip', 'strip', 'lidar') and z_pre is not None:
        if form[0] == 'lidar':   # slope and flat-core level both measured from the LiDAR profile
            selp = (sd >= 1) & (sd <= 5)
            # pitch floor 0.68: the Commons photo shows a tile band above the eave from the photo-match camera (needs > ~0.58) and the ortho tile/membrane edge sits ~4.5-5 m in (3.3 m rise / 4.85 m = 0.68); LiDAR's 0.52 is softened by DSM smoothing at the eave
            s_ = float(np.clip(np.median((z_pre[selp] - eave_z) / sd[selp]), 0.68, 0.8)); core_lv = float(np.median(z_pre[sd > 0.6 * sdm]))
            zf_ = np.where(sd >= 0, np.minimum(eave_z + s_ * sd, core_lv), eave_z + s_ * np.maximum(sd, -1.2))
            key = np.round(RV[vi, 0] * 50).astype(np.int64) * 10_000_000 + np.round(RV[vi, 1] * 50).astype(np.int64)
            _, inv_ = np.unique(key, return_inverse=True); zmax = np.full(inv_.max() + 1, -1e9); np.maximum.at(zmax, inv_, RV[vi, 2])
            RV[vi, 2] = zf_ + (RV[vi, 2] - zmax[inv_]); RA[vi] = 1.0
            print('ROOFFORM', form, 'eave', round(eave_z, 1), 'pitch', round(s_, 2), 'core', round(core_lv - eave_z, 2), 'band width m', round((core_lv - eave_z) / s_, 1))
            CH['last'] = (eave_z, s_, core_lv, poly, 'lidar')
            return core_lv
        ridge = float(np.percentile(z_pre[sd > 0], 98))                     # LiDAR ridge height
        print('ORTHO_TILE', [(s0, round(float((RA[vi][(sd >= s0) & (sd < s0 + 1)] >= 0.5).mean()), 2) if ((sd >= s0) & (sd < s0 + 1)).sum() > 5 else None) for s0 in range(-2, int(sdm) + 1)])
        print('PROFILE', [(s0, round(float(np.median(z_pre[(sd >= s0) & (sd < s0 + 1)]) - eave_z), 2) if ((sd >= s0) & (sd < s0 + 1)).sum() > 5 else None) for s0 in range(-2, int(sdm) + 1)])
        s_ = float(np.clip((ridge - eave_z) / max(sdm - (form[1] or 0.0), 1.0), 0.42, 0.75))
        core_lv = eave_z + s_ * (sdm - (form[1] or 0.0)) if form[0] == 'strip' else 1e9
        sdc = np.maximum(sd, -1.2)
        zf_ = np.where(sd >= 0, np.minimum(eave_z + s_ * sd, core_lv), eave_z + s_ * sdc)
        key = np.round(RV[vi, 0] * 50).astype(np.int64) * 10_000_000 + np.round(RV[vi, 1] * 50).astype(np.int64)
        _, inv_ = np.unique(key, return_inverse=True); zmax = np.full(inv_.max() + 1, -1e9); np.maximum.at(zmax, inv_, RV[vi, 2])
        RV[vi, 2] = zf_ + (RV[vi, 2] - zmax[inv_])
        RA[vi] = 1.0   # tile everywhere; the flat ridge strip gets membrane from the shader's flat-normal rule
        print('ROOFFORM', form, 'eave', round(eave_z, 1), 'ridge', round(ridge, 1), 'pitch', round(s_, 2), 'sdmax', round(sdm, 1), 'model ridge', round(min(eave_z + s_*sdm, core_lv), 1))
        CH['last'] = (eave_z, s_, min(eave_z + s_ * sdm, core_lv), poly, form[0])
        return None if form[0] == 'hip' else core_lv
    if core_lv is None:
        pl = (RA[vi] >= 0.5) & (sd > 2.5) & (sd < 6.0)
        if pl.sum() < 10: return
        core_lv = float(np.percentile(RV[vi[pl], 2], 60))
    ring = (RA[vi] >= 0.5) & (sd > 1.0) & (sd < 4.0)
    if ring.sum() >= 10:   # tile ring top from LiDAR; a lower flat core is lifted to it (no inner steps; core height may read up to ~1-2 m high)
        rt = float(np.percentile(RV[vi[ring], 2], 70)); core_lv = max(core_lv, min(rt, eave_z + HIP_TARGET * 4.0), eave_z + HIP_TARGET * 1.5)
    sdc = np.maximum(sd, -1.2)   # roof verts outside the OSM outline beyond the eave overhang: do not dive
    zf_ = np.where(sd >= 0, np.minimum(eave_z + HIP_TARGET * sd, core_lv), eave_z + HIP_TARGET * sdc)
    # keep vertical offsets of stacked verts (fascia bottom edges share xy with the eave edge)
    key = np.round(RV[vi, 0] * 50).astype(np.int64) * 10_000_000 + np.round(RV[vi, 1] * 50).astype(np.int64)
    _, inv_ = np.unique(key, return_inverse=True); zmax = np.full(inv_.max() + 1, -1e9); np.maximum.at(zmax, inv_, RV[vi, 2])
    RV[vi, 2] = zf_ + (RV[vi, 2] - zmax[inv_])
    CH['last'] = (eave_z, HIP_TARGET, core_lv, poly, 'ring')
    return core_lv
    print('CLEANHIP', round(eave_z, 2), 'core', round(core_lv, 2), 'sdmax', round(float(sd.max()), 1), 'memb frac', round(float((RA[vi] < 0.5).mean()), 2))
def _levels(zs):
    bins = np.arange(zs.min() - 0.25, zs.max() + 0.5, 0.25); h_, e_ = np.histogram(zs, bins)
    pk = [k for k in range(len(h_)) if h_[k] >= max(12, 0.08 * len(zs)) and h_[k] == h_[max(0, k-2):k+3].max()]
    if not pk: pk = [int(np.argmax(h_))]
    return np.array(sorted(np.median(zs[(zs >= e_[k] - 0.25) & (zs < e_[k+1] + 0.25)]) for k in pk))
def model_roof(vi, osm_id, hip, clean=False):
    """Clean modelled flat roof: snap to dominant levels, LiDAR lumps -> boxed penthouses / HVAC units, parapet + coping (flat buildings), small vents."""
    global nflat
    f = _SDF.get(osm_id)
    if f is None or len(f['pts']) < 4: return
    poly = _shp.Polygon(f['pts']).buffer(0)
    if poly.geom_type != 'Polygon': poly = max(poly.geoms, key=lambda g: g.area)
    x, y, z = RV[vi, 0], RV[vi, 1], RV[vi, 2]
    if hip:
        sel = (RA[vi] < 0.5) & _shp.contains_xy(poly.buffer(-1.2), x, y)
    else:
        sel = np.ones(len(vi), bool); RA[vi] = 0.0     # no tile on these (flat roofs in the ortho)
    if sel.sum() < 20: return
    zs = z[sel]; lv = _levels(zs)
    d = zs[:, None] - lv[None, :]; below = np.where(d > -0.6, d, 1e9); j = below.argmin(1)
    nob = below[np.arange(len(zs)), j] > 1e8; j[nob] = np.abs(d[nob]).argmin(1)
    up = zs - lv[j]; keep = (up < -1.0) if hip else np.zeros(len(zs), bool)   # hip: courtyards/lower wings keep LiDAR; flat: everything snaps (clean edge under the parapet)
    lump = up > 1.2
    z_orig = RV[vi, 2].copy()
    idx = vi[sel][~keep]; RV[idx, 2] = lv[j][~keep]; nflat += int((~keep).sum())
    main_lv = float(lv[np.bincount(j, minlength=len(lv)).argmax()])
    # lumps -> boxes (connected on a 1 m grid, 1-cell gap tolerance)
    lx, ly, lu, ll = x[sel][lump], y[sel][lump], up[lump], lv[j][lump]
    cells = {}
    for k_, (a, c) in enumerate(zip(np.round(lx).astype(int), np.round(ly).astype(int))): cells.setdefault((a, c), []).append(k_)
    seen = set()
    for c0 in list(cells):
        if c0 in seen: continue
        stack = [c0]; seen.add(c0); comp = []
        while stack:
            c = stack.pop(); comp += cells[c]
            for da in range(-2, 3):
                for db in range(-2, 3):
                    nb = (c[0] + da, c[1] + db)
                    if nb in cells and nb not in seen: seen.add(nb); stack.append(nb)
        if len(comp) < 3: continue
        comp = np.array(comp); rect = _shp.MultiPoint(np.c_[lx[comp], ly[comp]]).minimum_rotated_rectangle.buffer(0.5, join_style='mitre')
        rect = rect.intersection(poly.buffer(-0.8 if not hip else -1.0))
        if rect.is_empty or rect.area < 1.0: continue
        rr = rect.minimum_rotated_rectangle; cc = np.array(rr.exterior.coords)[:4]
        e1, e2 = cc[1] - cc[0], cc[2] - cc[1]; sx, sy = np.linalg.norm(e1), np.linalg.norm(e2); ang = math.atan2(e1[1], e1[0])
        h_raw = float(np.percentile(lu[comp], 75))
        if hip and (rect.area > 30 or h_raw > 3.0):   # on tile buildings big 'lumps' are real roof (ridges, upper wings): keep the LiDAR surface
            li = vi[sel][lump][comp]; RV[li, 2] = z_orig[np.searchsorted(vi, li)]; continue
        h = float(np.clip(h_raw, 1.0, 7.0)); z0 = float(np.median(ll[comp]))
        cx_, cy_ = cc.mean(0)
        if sx * sy > 30 and h > 2.2: EQ['pent'].append((cx_, cy_, ang, sx, sy, z0 - 0.2, z0 + h))
        else: EQ['hvac'].append((cx_, cy_, ang, min(sx, 6), min(sy, 6), z0 - 0.1, z0 + float(np.clip(h, 0.9, 2.0))))
    # small exhaust fans / vents at believable density (~1 per 150 m2 of flat roof), on the snapped surface
    inner = poly.buffer(-2.5) if not hip else poly.buffer(-2.5).intersection(_shp.MultiPoint(np.c_[x[sel], y[sel]]).convex_hull)
    if not inner.is_empty:
        n_v = int(inner.area / 150); mnx, mny, mxx, mxy = inner.bounds; tries = 0
        while n_v > 0 and tries < 400:
            tries += 1; px_, py_ = _rng_eq.uniform(mnx, mxx), _rng_eq.uniform(mny, mxy)
            if not inner.contains(_shp.Point(px_, py_)): continue
            k_ = int(np.argmin((x[sel] - px_)**2 + (y[sel] - py_)**2)); zz = float(lv[j][k_])
            s_ = _rng_eq.uniform(0.5, 0.9); EQ['vent'].append((px_, py_, _rng_eq.uniform(0, math.pi), s_, s_, zz - 0.05, zz + _rng_eq.uniform(0.35, 0.8))); n_v -= 1
    if not hip:   # parapet + coping along the footprint, at the snapped level of the nearest roof vertex
        cs = list(poly.exterior.coords); ccw = poly.exterior.is_ccw
        for a, c in zip(cs[:-1], cs[1:]):
            ex, ey = c[0] - a[0], c[1] - a[1]; L_ = math.hypot(ex, ey)
            if L_ < 0.3: continue
            tx_, ty_ = ex / L_, ey / L_; nx_, ny_ = (-ty_, tx_) if ccw else (ty_, -tx_)   # inward normal
            mx_, my_ = (a[0] + c[0]) / 2, (a[1] + c[1]) / 2
            k_ = int(np.argmin((RV[vi, 0] - mx_)**2 + (RV[vi, 1] - my_)**2)); zl = float(RV[vi[k_], 2])
            ox, oy = mx_ + nx_ * 0.13, my_ + ny_ * 0.13   # 0.34 m wall: outer face 0.04 m outside the facade
            ang = math.atan2(ty_, tx_)
            EQ['parapet'].append((ox, oy, ang, L_ + 0.3, 0.34, zl - 1.0, zl + 0.75))
            EQ['coping'].append((ox, oy, ang, L_ + 0.42, 0.46, zl + 0.75, zl + 0.83))
    return main_lv
_MR_RET = None
def _boxes_mesh(name, boxes, col, mat):
    if not boxes: return None
    V, F = [], []
    for (cx_, cy_, ang, sx, sy, z0, z1) in boxes:
        ca, sa = math.cos(ang), math.sin(ang); o_ = len(V)
        for zz in (z0, z1):
            for du, dv in ((-sx/2, -sy/2), (sx/2, -sy/2), (sx/2, sy/2), (-sx/2, sy/2)):
                V.append((cx_ + du*ca - dv*sa, cy_ + du*sa + dv*ca, zz))
        F += [(o_+0, o_+3, o_+2, o_+1), (o_+4, o_+5, o_+6, o_+7), (o_+0, o_+1, o_+5, o_+4), (o_+1, o_+2, o_+6, o_+5), (o_+2, o_+3, o_+7, o_+6), (o_+3, o_+0, o_+4, o_+7)]
    return mesh_obj(name, V, F, col, mat)
for b in M['buildings']:
    i = b['bid']; col = c_b['Buildings_day1' if b['target'] else 'Buildings_context']
    vi = np.nonzero(RB == i)[0]; v0 = vi[0]
    tri = RT[(RT[:,0] >= v0) & (RT[:,0] <= vi[-1])] - v0
    nm = (b['name'] or f"bldg_{b['osm_id']}").replace('/', '-')
    _hi = M.get('hip_info', {}).get(b['osm_id'])
    _clean = bool(_hi) and _hi[0] < 14.0 and b['osm_id'] in _SDF and _shp.Polygon(_SDF[b['osm_id']]['pts']).buffer(0).geom_type == 'Polygon'
    _n0 = {k: len(v) for k, v in EQ.items()}
    _zpre = RV[vi, 2].copy(); _form = ROOF_FORM.get(b['osm_id'])
    if _form is None and _clean:   # auto from the ortho tile/membrane classification
        _mf = float((RA[vi] < 0.5).mean()); _form = ('hip', None) if _mf < 0.3 else None
        print('ROOFFORM auto', b['name'], 'membrane frac', round(_mf, 2), '->', 'hip' if _form else 'ring')
    _core = model_roof(vi, b['osm_id'], bool(_hi), _clean)
    if _clean:   # low Mission-style tile blocks: modelled hip roof / strip / ring + flat core; this building's units sit on the final core
        _cf = clean_hip(vi, _shp.Polygon(_SDF[b['osm_id']]['pts']).buffer(0), b['ground_min'] + _hi[0], _core, _form, _zpre)
        if _form is not None and _form[0] == 'hip':
            for k in EQ: del EQ[k][_n0[k]:]          # no flat roof -> no units
        elif _form is not None and _form[0] == 'strip':
            for k in ('hvac', 'pent', 'parapet', 'coping'): del EQ[k][_n0[k]:]   # strip too narrow for units; keep a few vents
        if _cf is not None:
            for k in ('hvac', 'vent', 'pent'):
                EQ[k][_n0[k]:] = [(cx_, cy_, an_, sx_, sy_, _cf - 0.05, _cf - 0.05 + (z1_ - z0_)) for (cx_, cy_, an_, sx_, sy_, z0_, z1_) in EQ[k][_n0[k]:]]
    if _clean:   # boxed eave under the tile edge: soffit + fascia tucked just under the roof surface, exposed rafter tails, barrel-tile eave course (Morehead photo)
        _pg = _shp.Polygon(_SDF[b['osm_id']]['pts']).buffer(0).simplify(0.4)
        if _pg.geom_type == 'Polygon':
            from shapely.geometry.polygon import orient as _ori
            _cc = np.array(_ori(_pg, 1.0).exterior.coords)[:-1]; _nv = len(_cc); SV, SF = [], []; RVb = RV[vi]
            _skip = -1
            if b['osm_id'] == '312933183' and M.get('morehead_entrance'):   # the eave dies into the entrance pavilion (Commons photo): cut the outline at the pavilion sides
                _me = M['morehead_entrance']; _pc = np.array(_me['center']); _pt = np.array(_me['t']); _pn = np.array(_me['n'])
                _dk = [np.linalg.norm((_cc[k] + _cc[(k + 1) % _nv]) / 2 - _pc) for k in range(_nv)]; _kk = int(np.argmin(_dk))
                _a0, _c0 = _cc[_kk], _cc[(_kk + 1) % _nv]; _ed = (_c0 - _a0) / np.linalg.norm(_c0 - _a0)
                _ps = sorted([_a0 + _ed * float(((_pc + _pt * sg) - _a0) @ _ed) for sg in (-3.0, 3.0)], key=lambda q: float((q - _a0) @ _ed))
                _cc = np.insert(_cc, _kk + 1, np.array(_ps), axis=0); _nv = len(_cc); _skip = _kk + 1
                # roof overhang in front of the pavilion is pulled back inside the pavilion body
                _q = RV[vi, :2] - _pc; _u = _q @ _pt; _w = _q @ _pn; _mk = (np.abs(_u) < 2.95) & (_w > 0.3)
                RV[vi[_mk], 0:2] = _pc + np.outer(_u[_mk], _pt) + 0.3 * _pn; RVb = RV[vi]
            def _zr(q):   # roof surface z at xy q (nearest roof vertex of this building)
                d2 = (RVb[:, 0] - q[0])**2 + (RVb[:, 1] - q[1])**2; return float(RVb[int(np.argmin(d2)), 2])
            OUT_, NRM, ZF = [], [], []
            for _k in range(_nv):
                _p0, _p1, _p2 = _cc[_k - 1], _cc[_k], _cc[(_k + 1) % _nv]
                _e1 = (_p1 - _p0) / (np.linalg.norm(_p1 - _p0) + 1e-9); _e2 = (_p2 - _p1) / (np.linalg.norm(_p2 - _p1) + 1e-9)
                _n1 = np.array([_e1[1], -_e1[0]]); _n2 = np.array([_e2[1], -_e2[0]]); _mi = _n1 + _n2; _mi /= (np.linalg.norm(_mi) + 1e-9)
                _o = _p1 + _mi * min(0.75 / max(float(_mi @ _n1), 0.35), 2.0)
                _zt = _zr(_o) - 0.04; OUT_.append(_o); NRM.append(_mi); ZF.append(_zt)
                SV += [(_p1[0], _p1[1], _zt - 0.32), (_o[0], _o[1], _zt - 0.32), (_o[0], _o[1], _zt)]
            for _k in range(_nv):
                if _k == _skip: continue
                a_, c_ = 3 * _k, 3 * ((_k + 1) % _nv)
                SF += [(a_, c_, c_ + 1, a_ + 1), (a_ + 1, c_ + 1, c_ + 2, a_ + 2)]
            # rafter tails every 0.6 m under the soffit (Morehead: exposed dark rafters)
            for _k in range(_nv):
                _a, _c = _cc[_k], _cc[(_k + 1) % _nv]; _L = float(np.linalg.norm(_c - _a))
                if _L < 1.0 or _k == _skip: continue
                _t = (_c - _a) / _L; _n = np.array([_t[1], -_t[0]]); _z0 = ZF[_k] - 0.32; _z1 = ZF[(_k + 1) % _nv] - 0.32
                for _s in np.arange(0.4, _L - 0.3, 0.6):
                    _q = _a + _t * _s; _zz = _z0 + (_z1 - _z0) * _s / _L; base = len(SV)
                    for (_u, _w) in ((-0.035, 0.0), (0.035, 0.0), (0.035, 0.70), (-0.035, 0.70)):
                        x_, y_ = _q + _t * _u + _n * _w; SV += [(x_, y_, _zz), (x_, y_, _zz - 0.14)]
                    SF += [(base, base + 2, base + 4, base + 6), (base + 1, base + 7, base + 5, base + 3), (base, base + 1, base + 3, base + 2),
                           (base + 2, base + 3, base + 5, base + 4), (base + 4, base + 5, base + 7, base + 6), (base + 6, base + 7, base + 1, base)]
            if _skip >= 0:   # 3f: close the boxed eave where it dies into the pavilion (end board)
                for _k in (_skip, (_skip + 1) % _nv):
                    _p1 = _cc[_k]; SV.append((_p1[0], _p1[1], ZF[_k])); SF.append((3 * _k, 3 * _k + 1, 3 * _k + 2, len(SV) - 1))
            mesh_obj(f'{nm} eave soffit + fascia + rafter tails', SV, SF, col, m_fascia)
            # barrel-tile eave course: half-round tile noses every 0.25 m, following the roof slope (their thickness is most of the red band in the photo)
            TV, TF, TC = [], [], []
            _rt = random.Random(int(b['osm_id']) % 1000003)
            def _tcol():   # per tile: +-12 % value, slight hue drift, ~3.5 % newer replacement tiles (brighter orange), ~3.5 % weathered dark
                r_ = _rt.random()
                base_ = (0.56, 0.21, 0.09) if r_ < 0.035 else ((0.27, 0.095, 0.055) if r_ < 0.07 else (0.42, 0.13, 0.07))
                g_ = _rt.uniform(0.86, 1.12); h_ = _rt.uniform(-0.03, 0.03)
                return (base_[0] * g_ * (1 + h_), base_[1] * g_, base_[2] * g_ * (1 - h_), 1.0)
            for _k in range(_nv):
                _a, _c = OUT_[_k], OUT_[(_k + 1) % _nv]; _L = float(np.linalg.norm(_c - _a))
                if _L < 0.6 or _k == _skip: continue
                _t = (_c - _a) / _L; _n = np.array([_t[1], -_t[0]])
                _zin = _zr(_a + (_c - _a) * 0.5 - _n * 1.6); _zed = _zr(_a + (_c - _a) * 0.5 - _n * 0.1); _sl = float(np.clip((_zin - _zed) / 1.5, 0.3, 0.9))
                dvec = Vector((-_n[0], -_n[1], _sl)).normalized(); tv = Vector((_t[0], _t[1], 0)); up = dvec.cross(tv).normalized()
                if up.z < 0: up = -up
                for _s in np.arange(0.12, _L - 0.1, 0.25):
                    _q = _a + _t * _s + _n * (0.04 + _rt.uniform(-0.015, 0.015)); _zz = ZF[_k] + (ZF[(_k + 1) % _nv] - ZF[_k]) * _s / _L + 0.04
                    p0 = Vector((_q[0], _q[1], _zz)); base = len(TV)
                    _R = Matrix.Rotation(_rt.uniform(-0.07, 0.07), 3, 'Z') @ Matrix.Rotation(_rt.uniform(-0.04, 0.04), 3, dvec)   # small yaw / roll per tile
                    _tv, _dv, _up = _R @ tv, _R @ dvec, _R @ up
                    _ln = 0.38 if _rt.random() > 0.03 else _rt.uniform(0.22, 0.3)   # ~3 % chipped / broken noses
                    for ring_ in range(2):
                        pc_ = p0 + _dv * (0.38 - _ln + _ln * ring_)
                        for j in range(7):
                            th = math.pi * j / 6; TV.append(tuple(pc_ + _tv * (0.11 * math.cos(th)) + _up * (0.10 * math.sin(th))))
                    TF += [(base + j, base + j + 1, base + 8 + j, base + 7 + j) for j in range(6)]
                    if b['osm_id'] in ('312933183', '313021866', '1188721159'):   # 3g: tile edge ring + recessed mortar bird stop in the barrel mouth
                        pc0 = p0 + _dv * (0.38 - _ln); ib = len(TV)
                        for j in range(7):
                            th = math.pi * j / 6; TV.append(tuple(pc0 + _tv * (0.088 * math.cos(th)) + _up * (0.078 * math.sin(th))))
                        _rk = _rt.random(); _dep = 0.09 if _rk < 0.07 else _rt.uniform(0.012, 0.045)   # 3h: ~7 % missing bird stops (deep dark gap)
                        for j in range(7):
                            th = math.pi * j / 6; TV.append(tuple(pc0 + _dv * _dep + _tv * (0.088 * math.cos(th)) + _up * (0.078 * math.sin(th))))
                        TF += [(base + j, base + j + 1, ib + j + 1, ib + j) for j in range(6)]
                        TF += [(ib + j, ib + j + 1, ib + 8 + j, ib + 7 + j) for j in range(6)]
                        TF.append(tuple(ib + 7 + j for j in range(6, -1, -1)))
                        _c = _tcol(); _mo = _rt.uniform(0.7, 1.15); _hu = _rt.uniform(-0.04, 0.04)
                        if _rk < 0.07: _bs = (0.02, 0.018, 0.015, 1.0)                                       # missing: dark cavity
                        elif _rk < 0.25: _bs = tuple(v_ * _rt.uniform(0.75, 1.05) for v_ in _c[:3]) + (1.0,)   # terracotta closure piece
                        else: _bs = (0.5 * _mo * (1 + _hu), 0.46 * _mo, 0.39 * _mo * (1 - _hu), 1.0)           # mortar, tone varies (dirt, repairs)
                        TC.extend([_c] * 6 + [_c] * 6 + [tuple(v_ * 0.8 for v_ in _c[:3]) + (1.0,)] * 6 + [_bs])
                    else:
                        TF.append(tuple(base + j for j in range(6, -1, -1)))
                        TC.extend([_tcol()] * 7)
            if TF:
                _to = mesh_obj(f'{nm} barrel tile eave course', TV, TF, col, m_tile_course)
                _to.data.color_attributes.new('tcol', 'FLOAT_COLOR', 'FACE').data.foreach_set('color', np.array(TC, np.float32).ravel())
            # 3f: hip caps up each convex corner + ridge cap along the tile/flat transition (ring / band roofs), laid bottom-up, per-tile colour
            _ch = CH.get('last')
            if _ch is not None and b['osm_id'] != '312849089':
                from mathutils.bvhtree import BVHTree as _BVH
                _bv = _BVH.FromPolygons([tuple(map(float, v)) for v in RV[vi]], [tuple(map(int, t_)) for t_ in tri])
                CV, CF, CC = [], [], []
                def _capseg(P):
                    if P[0].z > P[-1].z: P = P[::-1]
                    for i_ in range(len(P) - 1):
                        a0, a1 = P[i_], P[i_ + 1]; d = a1 - a0
                        if d.length < 0.05: continue
                        dn = d.normalized(); upv = Vector((0, 0, 1)) - dn * dn.z
                        if upv.length < 1e-3: continue
                        upv.normalize(); sdv = dn.cross(upv); base = len(CV)
                        for (pp, rr) in ((a0, 0.135), (a1 + dn * 0.05, 0.12)):
                            for j in range(9):
                                th = math.pi * j / 8; CV.append(tuple(pp + sdv * (rr * math.cos(th)) + upv * (0.8 * rr * math.sin(th))))
                        CF.extend([(base + j, base + j + 1, base + 10 + j, base + 9 + j) for j in range(8)]); CF.append(tuple(range(base + 8, base - 1, -1)))
                        CC.extend([_tcol()] * 9)
                def _caprun(pts):
                    P = []
                    for (x_, y_) in pts:
                        h_ = _bv.ray_cast(Vector((x_, y_, 2000.0)), Vector((0, 0, -1)))
                        if h_[0] is None:
                            if len(P) > 1: _capseg(P)
                            P = []; continue
                        P.append(Vector((x_, y_, h_[0].z + 0.035)))
                    if len(P) > 1: _capseg(P)
                _ez, _s, _top, _pl, _fm = _ch; nh = 0
                for _k in range(_nv):
                    _p0, _p1, _p2 = _cc[_k - 1], _cc[_k], _cc[(_k + 1) % _nv]; _e1 = _p1 - _p0; _e2 = _p2 - _p1
                    if _e1[0] * _e2[1] - _e1[1] * _e2[0] <= 0.2 * np.linalg.norm(_e1) * np.linalg.norm(_e2): continue   # reflex / near-straight: valley or no hip
                    _mi = NRM[_k]; _cs = float(_mi @ (np.array([_e1[1], -_e1[0]]) / np.linalg.norm(_e1)))
                    _st = OUT_[_k]; _sd0 = float(_signed_dist(_pl, np.array([_st[0]]), np.array([_st[1]]))[0])
                    ts = np.arange(0.0, 40.0, 0.42); X = _st[None, :] - np.outer(ts, _mi)
                    sdt_ = _signed_dist(_pl, X[:, 0], X[:, 1]); sda = _sd0 + ts * _cs
                    ok = ((sda < 0.3) | (np.abs(sdt_ - sda) < 0.25)) & (_ez + _s * sda < _top - 0.05)
                    nl_ = len(ok) if ok.all() else int(np.argmin(ok))
                    if nl_ >= 3: _caprun([tuple(p) for p in X[:nl_]]); nh += 1
                if _fm in ('ring', 'lidar') and _top < 1e8:
                    _ip = _pl.buffer(-(_top - _ez) / _s, join_style=2)
                    for g_ in getattr(_ip, 'geoms', [_ip]):
                        if g_.geom_type != 'Polygon' or g_.area < 4: continue
                        ls_ = g_.exterior; n_ = max(2, int(ls_.length / 0.42))
                        _caprun([tuple(ls_.interpolate(i_ / n_, normalized=True).coords[0]) for i_ in range(n_ + 1)])
                if CF:
                    _co = mesh_obj(f'{nm} hip + ridge cap tiles', CV, CF, col, m_tile_course)
                    _co.data.color_attributes.new('tcol', 'FLOAT_COLOR', 'FACE').data.foreach_set('color', np.array(CC, np.float32).ravel())
                print('CAPS', nm, 'hips', nh, 'cap tiles', len(CF) // 9)
            EAVES.append(dict(osm=b['osm_id'], nm=nm, col=col, cc=_cc.copy(), out=[np.array(o_) for o_ in OUT_], zf=list(ZF), skip=_skip))
    ro = mesh_obj(f'{nm} roof (LiDAR)', RV[vi], tri, col, m_roof, smooth=False)
    _mv = RA[vi] < 0.5
    _lm_ = float(np.median((G['roof_col'][vi][_mv, :3]**2.2) @ np.array([0.2126, 0.7152, 0.0722]))) if _mv.sum() > 20 else 0.0
    ro['tpo'] = float(np.clip((_lm_ - 0.28) / 0.12, 0.0, 1.0)); print('TPO', nm, round(_lm_, 3), round(ro['tpo'], 2))
    try:   # TPO seam direction = long axis of the footprint's minimum rotated rectangle
        _rr = np.array(_shp.Polygon(_SDF[b['osm_id']]['pts']).buffer(0).minimum_rotated_rectangle.exterior.coords)
        _e = [(_rr[k+1] - _rr[k]) for k in range(2)]; _e = max(_e, key=lambda v: np.hypot(*v)); ro['seam_angle'] = float(math.atan2(_e[1], _e[0]))
    except Exception: ro['seam_angle'] = 0.0
    ro.data.materials.append(m_eave)
    ro.data.materials.append(m_fascia)
    tsel = (RT[:,0] >= v0) & (RT[:,0] <= vi[-1]); fl = G['roof_tflag'][tsel]
    if len(fl) == len(ro.data.polygons): ro.data.polygons.foreach_set('material_index', fl.astype(np.int32))
    ca = ro.data.color_attributes.new('roofc', 'FLOAT_COLOR', 'POINT'); rcol = G['roof_col'][vi]
    ca.data.foreach_set('color', np.c_[rcol[:, :3]**2.2, RA[vi]].astype(np.float32).ravel())
    wi = np.nonzero(WB == i)[0]
    Vw = WV[wi].reshape(-1, 3); Fw = np.arange(len(Vw)).reshape(-1, 4)
    wo = mesh_obj(f'{nm} walls', Vw, Fw, col, m_wall_scm if b['osm_id'] == '1188721159' else m_wall_stucco)
    uvl = wo.data.uv_layers.new(name='facade'); uvl.data.foreach_set('uv', WU[wi].reshape(-1, 2).astype(np.float32).ravel())
    bm = bmesh.new(); bm.from_mesh(wo.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001); bm.to_mesh(wo.data); bm.free()
    hgt = (b['height_p50_m'] or 9.0)
    scm = b['osm_id'] == '1188721159'
    props = dict(win_pitch=3.4 if scm else 3.6, win_w=2.6 if scm else 2.2, floor_h=4.2 if scm else 4.4,
                 win_h=2.6 if scm else 2.45, win_bottom=0.9, win_top=(M.get('hip_info', {}).get(b['osm_id'], [hgt + 0.2])[0] - 1.0) if b['osm_id'] in M.get('hip_info', {}) else max(3.5, hgt - 0.8), mull_w=0.035 if scm else 0.10, muntin=0.0 if scm else 1.0)
    for k, v in props.items(): wo[k] = v
    for o in (ro, wo):
        o['osm_id'] = b['osm_id']; o['source'] = 'Footprint: OSM (ODbL). Heights/roof: USGS 3DEP NJ 2023 LiDAR (public domain).'
    cents[b['osm_id']] = (RV[vi,0].mean(), RV[vi,1].mean(), b['ground_min'], RV[vi,2].max())
c_eq = coll('Roof_equipment_parapets')
m_pent = rgb('Roof_penthouse_precast', (0.42, 0.41, 0.39), 0.75)
m_hvac = rgb('Roof_HVAC_galv_metal', (0.36, 0.37, 0.38), 0.45, 0.6)
m_vent = rgb('Roof_vent_dark_metal', (0.12, 0.12, 0.13), 0.5, 0.5)
m_cope = rgb('Parapet_coping_concrete', (0.50, 0.49, 0.46), 0.7)
for k_, mt_ in (('pent', m_pent), ('hvac', m_hvac), ('vent', m_vent), ('parapet', m_wall_stucco), ('coping', m_cope)):
    _o = _boxes_mesh(f'Roof_{k_}', EQ[k_], c_eq, mt_)
    if _o is not None and k_ == 'parapet':   # facade shader needs props: no windows on parapets
        _o.data.materials.clear(); _o.data.materials.append(m_pent_par := rgb('Parapet_stucco', (0.80, 0.79, 0.75), 0.8))
print('roof equipment', {k: len(v) for k, v in EQ.items()})
# ---------- day 2: CCOM tall section + Morehead west entrance pavilion
from mathutils import Matrix
c_d2 = coll('Day2_details')
m_stucco_plain, *_ = pbr('Stucco_plain_white', 'Plaster001', 2.5, tint=(0.95, 0.94, 0.90), bump=0.3)
m_scm_plain, *_ = pbr('SCM_tower_precast', 'Plaster003', 2.5, tint=(0.90, 0.87, 0.80), bump=0.3)
m_dark_glass = rgb('Dark_glass', (0.02, 0.025, 0.03), 0.05)
m_door = rgb('Door_dark_wood', (0.035, 0.025, 0.018), 0.45)
m_frame = rgb('Window_frame_brown', (0.05, 0.035, 0.025), 0.4)
m_conc = rgb('Concrete_steps', (0.55, 0.53, 0.50), 0.8)
m_letters = rgb('Lettering_bronze', (0.08, 0.06, 0.04), 0.35, 0.6)
m_lamp_body = rgb('Lamp_black_metal', (0.02, 0.02, 0.02), 0.35, 0.8)
m_lamp_glass = bpy.data.materials.new('Lamp_glass_warm'); m_lamp_glass.use_nodes = True
_lb = m_lamp_glass.node_tree.nodes['Principled BSDF']; _lb.inputs['Base Color'].default_value = (1, 0.85, 0.6, 1)
_lb.inputs['Emission Color'].default_value = (1, 0.75, 0.45, 1); _lb.inputs['Emission Strength'].default_value = 4.0
for tp in M.get('tall_parts', []):   # SUPERSEDED by scripts/ccom_tower.py (4a): this prism straddled the OSM wing wall; objects are deleted there
    cs = tp['coords']; nb_ = len(cs); zb_, zt_ = tp['gmin'] - 0.5, tp['top']
    V = [(x, y, zb_) for x, y in cs] + [(x, y, zt_) for x, y in cs]
    F = [(k, (k+1) % nb_, nb_ + (k+1) % nb_, nb_ + k) for k in range(nb_)] + [tuple(range(nb_, 2*nb_))]
    o = mesh_obj('CCOM tall section (LiDAR 22 m)', V, F, c_d2, m_scm_plain)
    # parapet cap
    cx_ = sum(x for x, y in cs)/nb_; cy_ = sum(y for x, y in cs)/nb_
    V2 = [(cx_ + (x-cx_)*1.04, cy_ + (y-cy_)*1.04, zt_) for x, y in cs] + [(cx_ + (x-cx_)*1.04, cy_ + (y-cy_)*1.04, zt_ + 0.35) for x, y in cs]
    mesh_obj('CCOM tall section coping', V2, F, c_d2, m_conc)
    # facade articulation (UNVERIFIED in detail: no current exterior photo of the tower yet; sources only say "white Mission-style tower left of the entrance").
    # Restrained: plinth, string courses at the CCOM floor lines (4.2 m), one recessed window per floor per face with jamb/head/sill reveals and a
    # mullion + transom grid, a deeper belfry-style opening pair at the top, and a cornice under the coping.
    tw = []; tg = []; tf = []
    poly_t = _shp.Polygon(cs); ccw_t = poly_t.exterior.is_ccw
    def tbox(lst, a, tx_, ty_, nx_, ny_, u0, u1, w0, w1, z0, z1):
        # box in edge frame: u along the edge from a, w outward from the face, world z
        lst.append(((a[0] + tx_*(u0+u1)/2 + nx_*(w0+w1)/2), (a[1] + ty_*(u0+u1)/2 + ny_*(w0+w1)/2), math.atan2(ty_, tx_), u1 - u0, w1 - w0, z0, z1))
    for k in range(nb_):
        a, c = cs[k], cs[(k+1) % nb_]; ex, ey = c[0]-a[0], c[1]-a[1]; L_ = math.hypot(ex, ey)
        if L_ < 2.5: continue
        tx_, ty_ = ex/L_, ey/L_; nx_, ny_ = (ty_, -tx_) if ccw_t else (-ty_, tx_)   # outward
        tbox(tw, a, tx_, ty_, nx_, ny_, -0.1, L_ + 0.1, -0.05, 0.10, zb_ + 0.5, tp['gmin'] + 0.6)            # plinth
        for zz in np.arange(tp['gmin'] + 4.2, zt_ - 3.0, 4.2):
            tbox(tw, a, tx_, ty_, nx_, ny_, -0.08, L_ + 0.08, -0.05, 0.08, zz - 0.12, zz + 0.12)             # string course
        tbox(tw, a, tx_, ty_, nx_, ny_, -0.15, L_ + 0.15, -0.05, 0.16, zt_ - 0.75, zt_ - 0.45)               # cornice
        ww = min(1.5, 0.28 * L_); u0w = L_/2 - ww/2; u1w = L_/2 + ww/2
        floors = list(np.arange(tp['gmin'] + 4.2, zt_ - 4.0, 4.2))
        for zf in floors:
            z0w, z1w = zf + 0.9, zf + 3.1
            tg.append(None); tg.pop()
            tbox(tg, a, tx_, ty_, nx_, ny_, u0w, u1w, 0.005, 0.02, z0w, z1w)                                   # glass (reads recessed behind the reveals)
            tbox(tf, a, tx_, ty_, nx_, ny_, L_/2 - 0.03, L_/2 + 0.03, 0.0, 0.07, z0w, z1w)                     # mullion
            tbox(tf, a, tx_, ty_, nx_, ny_, u0w, u1w, 0.0, 0.07, z0w + 1.45, z0w + 1.51)                       # transom
            for uu in (u0w - 0.22, u1w):
                tbox(tw, a, tx_, ty_, nx_, ny_, uu, uu + 0.22, -0.05, 0.24, z0w - 0.08, z1w + 0.22)           # jambs (0.24 m reveal)
            tbox(tw, a, tx_, ty_, nx_, ny_, u0w - 0.22, u1w + 0.22, -0.05, 0.24, z1w, z1w + 0.22)              # head
            tbox(tw, a, tx_, ty_, nx_, ny_, u0w - 0.3, u1w + 0.3, -0.05, 0.30, z0w - 0.1, z0w)                 # projecting sill
        # belfry-style opening pair at the top
        for sgn_ in (-1, 1):
            uc = L_/2 + sgn_ * min(1.1, 0.2 * L_); bw = min(0.8, 0.14 * L_)
            tbox(tg, a, tx_, ty_, nx_, ny_, uc - bw/2, uc + bw/2, 0.005, 0.02, zt_ - 3.4, zt_ - 1.3)
            for uu in (uc - bw/2 - 0.2, uc + bw/2):
                tbox(tw, a, tx_, ty_, nx_, ny_, uu, uu + 0.2, -0.05, 0.28, zt_ - 3.5, zt_ - 1.1)
            tbox(tw, a, tx_, ty_, nx_, ny_, uc - bw/2 - 0.2, uc + bw/2 + 0.2, -0.05, 0.28, zt_ - 1.3, zt_ - 1.1)
            tbox(tw, a, tx_, ty_, nx_, ny_, uc - bw/2 - 0.25, uc + bw/2 + 0.25, -0.05, 0.32, zt_ - 3.55, zt_ - 3.4)
    _boxes_mesh('CCOM tower trim (string courses, reveals, cornice)', tw, c_d2, m_scm_plain)
    _boxes_mesh('CCOM tower glass', tg, c_d2, m_dark_glass)
    _boxes_mesh('CCOM tower mullions', tf, c_d2, rgb('CCOM_tower_mullion_bronze', (0.06, 0.05, 0.04), 0.4, 0.6))
ME = M.get('morehead_entrance')
if ME:
    _wo = [o for o in bpy.data.objects if o.get('osm_id') == '312933183' and o.name.endswith('walls')][0]
    _bid = [x for x in M['buildings'] if x['osm_id'] == '312933183'][0]['bid']
    _wi = np.nonzero(WB == _bid)[0]; _Q = WV[_wi]; _U = WU[_wi]
    _mid = (_Q[:, 0, :2] + _Q[:, 1, :2]) / 2; _k = int(np.argmin(np.linalg.norm(_mid - np.array(ME['center']), axis=1)))
    _up = float((_U[_k, 0, 0] + _U[_k, 1, 0]) / 2); _pw = float(_wo['win_pitch'])
    _wo['win_u0'] = _up - round(_up / _pw) * _pw   # pavilion centre sits on a gap between window columns
    t = Vector((*ME['t'], 0)); nv = Vector((*ME['n'], 0)); c0 = Vector((*ME['center'], ME['ground']))
    He = ME['eave'] - ME['ground']
    XF = Matrix(((t.x, nv.x, 0, c0.x), (t.y, nv.y, 0, c0.y), (0, 0, 1, c0.z), (0, 0, 0, 1)))
    def lbox(name, u0, u1, w0, w1, z0, z1, mat):
        V = [(u, w, z) for z in (z0, z1) for (u, w) in ((u0, w0), (u1, w0), (u1, w1), (u0, w1))]
        F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        o = mesh_obj(name, V, F, c_d2, mat); o.matrix_world = XF; return o
    def lprism(name, prof, w0, w1, mat):
        n_ = len(prof); V = [(u, w0, z) for u, z in prof] + [(u, w1, z) for u, z in prof]
        F = [tuple(range(n_))[::-1], tuple(range(n_, 2*n_))] + [(k, (k+1) % n_, n_ + (k+1) % n_, n_ + k) for k in range(n_)]
        o = mesh_obj(name, V, F, c_d2, mat); o.matrix_world = XF; return o
    def arc(cu, cz, r, a0, a1, n=12):
        return [(cu + r*math.cos(math.radians(a0 + (a1-a0)*i/n)), cz + r*math.sin(math.radians(a0 + (a1-a0)*i/n))) for i in range(n+1)]
    W2 = 2.95
    def volute(name, cu, cz, r0, turns, w0, w1, band, hand):
        # spiral band (Archimedean, shrinking toward the eye) extruded from the wall: gives the carved scroll real relief and shadow
        n_ = int(turns * 24); th = [i / 24 * math.tau for i in range(n_ + 1)]
        rr = [r0 * (1 - 0.8 * t / th[-1]) for t in th]
        outer = [(cu + hand * r * math.cos(t), cz + r * math.sin(t)) for r, t in zip(rr, th)]
        inner = [(cu + hand * max(r - band, 0.02) * math.cos(t), cz + max(r - band, 0.02) * math.sin(t)) for r, t in zip(rr, th)]
        prof = outer + inner[::-1]
        if hand < 0: prof = prof[::-1]
        return lprism(name, prof, w0, w1, m_stucco_plain)
    lbox('Morehead entrance pavilion body', -W2, W2, -0.3, 0.45, -0.6, He + 0.4, m_stucco_plain)
    # scrolled baroque parapet (profile in u-z)
    half = [(W2, He + 0.4), (W2, He + 1.0)] + arc(W2 - 0.45, He + 1.0, 0.45, 0, 180, 8)[1:] + [(W2 - 1.1, He + 1.25)] + \
           arc(W2 - 1.1 - 0.35, He + 1.25, 0.35, 0, 90, 4)[1:] + [(0.9, He + 2.2)] + arc(0, He + 2.2, 0.9, 0, 90, 8)[1:]
    prof = half + [(-u, z) for u, z in reversed(half)][1:]
    lprism('Morehead entrance parapet (baroque scrolls)', prof, -0.3, 0.42, m_stucco_plain)
    lprism('Morehead parapet cap', [(u, z) for u, z in arc(0, He + 3.1, 0.35, 0, 360, 12)][:-1], 0.0, 0.5, m_stucco_plain)
    lprism('Morehead parapet round window', arc(0, He + 1.75, 0.32, 0, 360, 16)[:-1], 0.42, 0.44, m_dark_glass)
    lprism('Morehead parapet round window frame', arc(0, He + 1.75, 0.42, 0, 360, 16)[:-1], 0.40, 0.43, m_stucco_plain)
    lbox('Morehead entrance cornice', -W2 - 0.2, W2 + 0.2, 0.45, 0.75, He + 0.15, He + 0.45, m_stucco_plain)
    # entablature with lettering, pilasters, door, transom
    lbox('Morehead entablature', -2.1, 2.1, 0.45, 0.66, 3.75, 4.35, m_stucco_plain)
    lbox('Morehead entablature cornice', -2.25, 2.25, 0.45, 0.74, 4.35, 4.5, m_stucco_plain)
    for sgn_ in (-1, 1):
        lbox(f'Morehead pilaster {sgn_:+d}', sgn_*1.55, sgn_*2.0, 0.45, 0.66, 0.0, 3.75, m_stucco_plain)
        lbox(f'Morehead pilaster capital {sgn_:+d}', sgn_*1.5, sgn_*2.05, 0.45, 0.72, 3.55, 3.75, m_stucco_plain)
        lbox(f'Morehead pilaster base {sgn_:+d}', sgn_*1.5, sgn_*2.05, 0.45, 0.72, 0.0, 0.3, m_stucco_plain)
        # scroll brackets flanking the arched window
        # scroll consoles flanking the arched window: recessed backing disc + raised spiral volute band + eye boss (photo: carved volutes)
        lprism(f'Morehead window scroll back {sgn_:+d}', [(sgn_*1.15 + 0.27*math.cos(math.radians(a)), 5.2 + 0.27*math.sin(math.radians(a))) for a in range(0, 360, 20)], 0.45, 0.53, m_stucco_plain)
        volute(f'Morehead window scroll volute {sgn_:+d}', sgn_*1.15, 5.2, 0.27, 2.1, 0.45, 0.66, 0.055, sgn_)
        lprism(f'Morehead window scroll eye {sgn_:+d}', arc(sgn_*1.15, 5.2, 0.06, 0, 360, 10)[:-1], 0.45, 0.70, m_stucco_plain)
        lbox(f'Morehead window scroll console {sgn_:+d}', sgn_*1.15 - 0.1, sgn_*1.15 + 0.1, 0.45, 0.6, 4.55, 4.95, m_stucco_plain)
        volute(f'Morehead parapet scroll volute {sgn_:+d}', sgn_*(W2 - 0.45), He + 1.0, 0.40, 1.8, 0.40, 0.52, 0.06, -sgn_)
        lbox(f'Morehead finial {sgn_:+d}', sgn_*1.08 - 0.08, sgn_*1.08 + 0.08, 0.45, 0.6, 5.45, 6.1, m_stucco_plain)
        # wall lanterns
        lb = lbox(f'Morehead wall lantern body {sgn_:+d}', sgn_*1.25 - 0.11, sgn_*1.25 + 0.11, 0.66, 0.9, 2.55, 2.62, m_lamp_body)
        lbox(f'Morehead wall lantern glass {sgn_:+d}', sgn_*1.25 - 0.09, sgn_*1.25 + 0.09, 0.68, 0.88, 2.25, 2.55, m_lamp_glass)
        lbox(f'Morehead wall lantern arm {sgn_:+d}', sgn_*1.25 - 0.02, sgn_*1.25 + 0.02, 0.45, 0.78, 2.6, 2.66, m_lamp_body)
    lbox('Morehead door recess', -1.0, 1.0, 0.40, 0.47, 0.0, 2.75, m_door)
    lbox('Morehead door glass L', -0.85, -0.12, 0.47, 0.48, 0.9, 2.5, m_dark_glass)
    lbox('Morehead door glass R', 0.12, 0.85, 0.47, 0.48, 0.9, 2.5, m_dark_glass)
    # 3f: clear transom pane with a lit EXIT sign just inside (dark vestibule behind)
    m_transom = bpy.data.materials.new('Transom_glass_clear'); m_transom.use_nodes = True; _pb = m_transom.node_tree.nodes['Principled BSDF']
    _pb.inputs['Base Color'].default_value = (0.75, 0.78, 0.76, 1); _pb.inputs['Transmission Weight'].default_value = 1.0; _pb.inputs['Roughness'].default_value = 0.03
    lbox('Morehead door transom pane (clear)', -1.0, 1.0, 0.476, 0.48, 2.9, 3.55, m_transom)
    lbox('Morehead vestibule (dark, behind transom)', -1.0, 1.0, 0.448, 0.452, 2.9, 3.55, rgb('Vestibule_dark', (0.012, 0.011, 0.01), 0.8))
    m_exit = bpy.data.materials.new('Exit_sign_red_LED'); m_exit.use_nodes = True; _pe = m_exit.node_tree.nodes['Principled BSDF']
    _pe.inputs['Base Color'].default_value = (0.8, 0.02, 0.01, 1); _pe.inputs['Emission Color'].default_value = (1.0, 0.03, 0.01, 1); _pe.inputs['Emission Strength'].default_value = 8.0
    lbox('Morehead EXIT sign housing (inside)', -0.17, 0.17, 0.452, 0.468, 3.06, 3.30, rgb('Exit_sign_housing_white', (0.7, 0.7, 0.68), 0.4))
    _cu = bpy.data.curves.new('EXIT', 'FONT'); _cu.body = 'EXIT'; _cu.size = 0.13; _cu.extrude = 0.002; _cu.align_x = 'CENTER'; _cu.align_y = 'CENTER'
    _tx = bpy.data.objects.new('Morehead EXIT sign letters', _cu); c_d2.objects.link(_tx); _cu.materials.append(m_exit)
    _tx.matrix_world = XF @ Matrix.Translation((0, 0.4705, 3.18)) @ Matrix.Rotation(math.radians(180), 4, 'Z') @ Matrix.Rotation(math.radians(90), 4, 'X')
    # red fire-alarm / Knox boxes on the pavilion face beside the right pilaster (Commons photo)
    _rgt = Vector((-nv.x, -nv.y, 0)).cross(Vector((0, 0, 1))); _us = 1.0 if _rgt.dot(t) > 0 else -1.0
    m_red_box = rgb('Fire_alarm_box_red', (0.45, 0.015, 0.012), 0.35)
    lbox('Morehead fire alarm box (photo)', _us * 2.32, _us * 2.5, 0.45, 0.53, 3.95, 4.2, m_red_box)
    lbox('Morehead Knox box (photo)', _us * 2.36, _us * 2.52, 0.45, 0.52, 1.95, 2.2, m_red_box)
    lbox('Morehead door surround', -1.15, 1.15, 0.45, 0.52, 2.75, 2.9, m_stucco_plain)
    lbox('Morehead entrance landing', -2.3, 2.3, 0.45, 2.4, -0.4, 0.12, m_conc)
    # arched upper window (2nd floor) with frame and muntins
    win = [(-0.75, 4.75), (0.75, 4.75)] + arc(0, 6.9, 0.75, 0, 180, 14)
    lprism('Morehead arched window frame', [(u*1.12, 4.65 + (z-4.75)*1.04) for u, z in win], 0.44, 0.47, m_frame)
    lprism('Morehead arched window glass', win, 0.47, 0.48, m_dark_glass)
    for uu in (-0.25, 0.25):
        lbox(f'Morehead arched window mullion {uu}', uu - 0.025, uu + 0.025, 0.48, 0.5, 4.75, 7.3, m_frame)
    for zz in (5.25, 5.75, 6.25, 6.9):
        lbox(f'Morehead arched window transom {zz}', -0.75, 0.75, 0.48, 0.5, zz - 0.02, zz + 0.02, m_frame)
    lbox('Morehead window panel', -0.75, 0.75, 0.45, 0.5, 4.5, 4.75, m_frame)
    # lettering
    cu = bpy.data.curves.new('MOREHEAD HALL', 'FONT'); cu.body = 'MOREHEAD HALL'; cu.size = 0.24; cu.extrude = 0.012
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.space_character = 1.15
    txt = bpy.data.objects.new('Morehead lettering', cu); c_d2.objects.link(txt); cu.materials.append(m_letters)
    txt.matrix_world = XF @ Matrix.Translation((0, 0.67, 4.05)) @ Matrix.Rotation(math.radians(180), 4, 'Z') @ Matrix.Rotation(math.radians(90), 4, 'X')
    # pilaster fluting: raised fillets between grooves (real shadow lines)
    for sgn_ in (-1, 1):
        for kf in range(4):
            uu = sgn_*1.55 + sgn_*(0.075 + kf*0.1)
            lbox(f'Morehead pilaster fillet {sgn_:+d} {kf}', uu - 0.022, uu + 0.022, 0.66, 0.695, 0.35, 3.5, m_stucco_plain)
    # carved cartouche around the round parapet window: bead ring, keystone, side volutes
    for kb in range(16):
        a_ = 2*math.pi*kb/16; cu_, cz_ = 0.55*math.cos(a_), He + 1.75 + 0.55*math.sin(a_)
        lprism(f'Morehead cartouche bead {kb}', [(cu_ + 0.075*math.cos(2*math.pi*j/8), cz_ + 0.075*math.sin(2*math.pi*j/8)) for j in range(8)], 0.40, 0.50, m_stucco_plain)
    lprism('Morehead cartouche keystone', [(-0.14, He + 2.22), (0.14, He + 2.22), (0.2, He + 2.55), (-0.2, He + 2.55)], 0.40, 0.55, m_stucco_plain)
    for sgn_ in (-1, 1):
        lprism(f'Morehead cartouche volute {sgn_:+d}', arc(sgn_*0.78, He + 1.55, 0.2, 0, 360, 12)[:-1], 0.40, 0.52, m_stucco_plain)
        lprism(f'Morehead cartouche volute eye {sgn_:+d}', arc(sgn_*0.78, He + 1.55, 0.08, 0, 360, 8)[:-1], 0.52, 0.56, m_stucco_plain)
    # planting bed along the west wall: mulch strip, brick edging, shrubs (terrain-following via ray casts)
    dg = bpy.context.evaluated_depsgraph_get()
    def ground_at(p):
        hit, loc, *_ = ter.ray_cast(Vector((p.x, p.y, p.z + 60)), Vector((0, 0, -1)), distance=200)  # terrain only (identity transform)
        return loc.z if hit else c0.z
    m_mulch, *_ = pbr('Mulch_bed', 'Ground054', 1.2, tint=(0.45, 0.3, 0.2), box=False, bump=0.8)
    m_brick, *_ = pbr('Brick_edging', 'Bricks066', 1.0, box=True, bump=0.5)
    Lw = ME['wall_len']/2 - 1.0; step_ = 1.0
    Vb, Fb, Ve, Fe = [], [], [], []
    us = np.arange(-Lw, Lw + 0.01, step_)
    for seg in (us[us < -2.6], us[us > 2.6]):
        if len(seg) < 2: continue
        bV, bF = Vb, Fb
        base = len(bV)
        for uu in seg:
            for ww_ in (0.3, 1.5):
                p = c0 + t*float(uu) + nv*ww_; bV.append((p.x, p.y, ground_at(p) + 0.05))
        for i_ in range(len(seg) - 1):
            a0 = base + 2*i_; bF.append((a0, a0 + 2, a0 + 3, a0 + 1))
        base = len(Ve)
        for uu in seg:
            p = c0 + t*float(uu) + nv*1.6; gz = ground_at(p)
            for ww_ in (1.5, 1.68):
                for zz in (gz - 0.05, gz + 0.09):
                    q = c0 + t*float(uu) + nv*ww_; Ve.append((q.x, q.y, zz))
        for i_ in range(len(seg) - 1):
            a0 = base + 4*i_; b0 = a0 + 4
            Fe.extend([(a0 + 1, a0 + 3, b0 + 3, b0 + 1), (a0 + 2, a0 + 3, b0 + 3, b0 + 2), (a0, a0 + 1, b0 + 1, b0)])
    mesh_obj('Morehead west planting bed (mulch)', Vb, Fb, c_d2, m_mulch)
    mesh_obj('Morehead west bed brick edging', Ve, Fe, c_d2, m_brick)
    shrub_proto = []
    m_shrub = rgb('Shrub_leaves', (0.035, 0.07, 0.02), 0.65)
    for k_ in range(3):
        bm = bmesh.new()
        for j in range(5):
            r_ = random.uniform(0.18, 0.3); cc_ = (random.uniform(-0.2, 0.2), random.uniform(-0.12, 0.12), random.uniform(0.2, 0.38))
            res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r_, matrix=Matrix.Translation(cc_))
            for vv in res['verts']: vv.co += (vv.co - Vector(cc_)).normalized() * random.uniform(-0.03, 0.03)
        me_ = bpy.data.meshes.new(f'shrub_proto_{k_}'); bm.to_mesh(me_); bm.free(); me_.materials.append(m_shrub); me_.shade_smooth()
        shrub_proto.append(me_)
    ns = 0
    for uu in np.arange(-Lw + 0.6, Lw, 1.15):
        if abs(uu) < 3.1: continue
        p = c0 + t*float(uu + random.uniform(-0.2, 0.2)) + nv*random.uniform(0.75, 1.05)
        o = bpy.data.objects.new(f'shrub_{ns:03d}', shrub_proto[ns % 3]); c_d2.objects.link(o)
        s_ = random.uniform(0.8, 1.25); o.scale = (s_, s_, s_*random.uniform(0.8, 1.1)); o.rotation_euler[2] = math.atan2(t.y, t.x) + random.uniform(-0.3, 0.3)
        o.location = (p.x, p.y, ground_at(p) - 0.05); ns += 1
    print('shrubs', ns)
    sc['morehead_entrance_note'] = 'Pavilion placed at midpoint of the longest west-facing wall (OSM). Dimensions estimated from Commons photo; ornament simplified.'
# ---------- 3i: Morehead N/S/E + Life Hall main facade + CCOM main entrance (photo) ---------------------------------
# Sources: Morehead west Commons photo (continuous sill course, low base moulding, door surround style); CCOM entrance from
# Commons File:School_of_Communications.jpg (2021): tiered tan stone arch, ~7x10 mahogany mullion glass grid, double doors,
# white tower lettering. Everything on Morehead N/S/E and Life Hall is extrapolated from the west front: UNVERIFIED.
c_3i = coll('Facades_3i')
m_cast = rgb('Cast_stone_tan', (0.62, 0.50, 0.34), 0.75)           # CCOM arch surround (#D2B48C-ish in sRGB)
m_mahog = rgb('Mullion_mahogany', (0.10, 0.026, 0.02), 0.45)         # #5A2A27
m_steel = rgb('Push_bar_steel', (0.55, 0.55, 0.55), 0.3, 0.9)
m_band = rgb('Stucco_band_white', (0.80, 0.79, 0.75), 0.75)
# CCOM atrium glass: dark interior, a grid of ceiling lights inside, strong clear-coat reflection (no real interior volume)
m_atr = bpy.data.materials.new('CCOM_atrium_glass_interior'); m_atr.use_nodes = True
_an = m_atr.node_tree.nodes; _al = m_atr.node_tree.links; _ab = _an['Principled BSDF']
_ab.inputs['Base Color'].default_value = (0.018, 0.02, 0.022, 1); _ab.inputs['Roughness'].default_value = 0.35
_ab.inputs['Coat Weight'].default_value = 1.0; _ab.inputs['Coat Roughness'].default_value = 0.02
_atc = _an.new('ShaderNodeTexCoord'); _asx = _an.new('ShaderNodeSeparateXYZ'); _al.new(_atc.outputs['Object'], _asx.inputs[0])
_abr = _an.new('ShaderNodeTexBrick'); _abr.inputs['Scale'].default_value = 1.0; _abr.inputs['Mortar Size'].default_value = 0.35
_abr.inputs['Color1'].default_value = (0, 0, 0, 1); _abr.inputs['Color2'].default_value = (0, 0, 0, 1); _abr.inputs['Mortar'].default_value = (1, 1, 1, 1)
_abr.inputs['Brick Width'].default_value = 0.9; _abr.inputs['Row Height'].default_value = 1.2
_al.new(_atc.outputs['Object'], _abr.inputs['Vector'])
_ainv = _an.new('ShaderNodeMath'); _ainv.operation = 'SUBTRACT'; _ainv.inputs[0].default_value = 1.0; _al.new(_abr.outputs['Fac'], _ainv.inputs[1])
_ahi = _an.new('ShaderNodeMath'); _ahi.operation = 'GREATER_THAN'; _ahi.inputs[1].default_value = 4.0; _al.new(_asx.outputs['Z'], _ahi.inputs[0])   # lights only in the upper atrium
_aem = _an.new('ShaderNodeMath'); _aem.operation = 'MULTIPLY'; _al.new(_ainv.outputs[0], _aem.inputs[0]); _al.new(_ahi.outputs[0], _aem.inputs[1])
_ab.inputs['Emission Color'].default_value = (1.0, 0.93, 0.8, 1)
_aes = _an.new('ShaderNodeMath'); _aes.operation = 'MULTIPLY'; _aes.inputs[1].default_value = 0.9; _al.new(_aem.outputs[0], _aes.inputs[0])
_al.new(_aes.outputs[0], _ab.inputs['Emission Strength'])

def _bld(osm):
    return [x for x in M['buildings'] if x['osm_id'] == osm][0]
def _walls(osm):
    return [o for o in bpy.data.objects if o.get('osm_id') == osm and o.name.endswith('walls')][0]
def _poly(osm):
    return _shp.Polygon([E for E in EAVES if E['osm'] == osm][0]['cc'])
def facade_frame(osm, near, want_n, snap='window'):
    """Snap a point on the facade nearest `near` (facing ~want_n) to the window grid. Returns (pc2, t2, n2, g, quad_len, info)."""
    b = _bld(osm); wo = _walls(osm); pw = float(wo['win_pitch']); u0off = float(wo.get('win_u0', 0.0))
    wi = np.nonzero(WB == b['bid'])[0]; Q = WV[wi]; U = WU[wi]; plg = _poly(osm)
    best = None
    for k in range(len(wi)):
        a = Q[k, 0, :2]; c = Q[k, 1, :2]; L = float(np.linalg.norm(c - a))
        if L < 0.05: continue
        t2 = (c - a) / L; n2 = np.array([t2[1], -t2[0]])
        if plg.contains(_shp.Point(*((a + c) / 2 + n2 * 1.2))): n2 = -n2   # eave ring is offset outward by the overhang (<=0.75 m)
        if float(n2 @ np.array(want_n)) < 0.85: continue
        s = float(np.clip((np.array(near) - a) @ t2, 0, L)); p = a + t2 * s; d = float(np.linalg.norm(p - np.array(near)))
        if best is None or d < best[0]: best = (d, k, a, c, t2, n2, L, s)
    d, k, a, c, t2, n2, L, s = best
    u0, u1 = float(U[k, 0, 0]), float(U[k, 1, 0]); u = u0 + (u1 - u0) * s / L
    uc = ((math.floor((u - u0off) / pw) + 0.5) * pw + u0off) if snap == 'window' else (round((u - u0off) / pw) * pw + u0off)
    if not (min(u0, u1) + 0.3 <= uc <= max(u0, u1) - 0.3): uc = u
    p = a + (c - a) * (uc - u0) / (u1 - u0); g = float(Q[k, 0, 2] - U[k, 0, 1])
    # length of the collinear run around p (so wide portals don't overhang a corner)
    return Vector((float(p[0]), float(p[1]))), Vector((float(t2[0]), float(t2[1]))), Vector((float(n2[0]), float(n2[1]))), g, L, dict(d=round(d, 2), quad=k)
def frame_xf(pc, n2, g):
    t = Vector((n2.y, -n2.x, 0)); nv = Vector((n2.x, n2.y, 0))   # (t, n, z) right-handed, same convention as the Morehead pavilion
    return Matrix(((t.x, nv.x, 0, pc.x), (t.y, nv.y, 0, pc.y), (0, 0, 1, g), (0, 0, 0, 1)))
def fbox(XFm, name, u0, u1, w0, w1, z0, z1, mat, col=None):
    V = [(u, w, z) for z in (z0, z1) for (u, w) in ((u0, w0), (u1, w0), (u1, w1), (u0, w1))]
    F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    o = mesh_obj(name, V, F, col or c_3i, mat); o.matrix_world = XFm; return o
def fprism(XFm, name, prof, w0, w1, mat):
    n_ = len(prof); V = [(u, w0, z) for u, z in prof] + [(u, w1, z) for u, z in prof]
    F = [tuple(range(n_))[::-1], tuple(range(n_, 2*n_))] + [(k, (k+1) % n_, n_ + (k+1) % n_, n_ + k) for k in range(n_)]
    o = mesh_obj(name, V, F, c_3i, mat); o.matrix_world = XFm; return o
def ftext(XFm, name, body, size, u, w, z, mat):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.size = size; cu.extrude = 0.01; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.space_character = 1.1
    tx = bpy.data.objects.new(name, cu); c_3i.objects.link(tx); cu.materials.append(mat)
    tx.matrix_world = XFm @ Matrix.Translation((u, w, z)) @ Matrix.Rotation(math.radians(180), 4, 'Z') @ Matrix.Rotation(math.radians(90), 4, 'X'); return tx
def ground_xy(x, y):
    hit, loc, *_ = ter.ray_cast(Vector((x, y, 400)), Vector((0, 0, -1)), distance=800)
    return loc.z if hit else gz(x, y)

def steps_down(XFm, nm, u0, u1, w0, g, top=0.12, mat=None):
    """Steps from a landing (top at g+top, front edge w0) down to the terrain in front; returns the number of risers."""
    pf = XFm @ Vector(((u0 + u1) / 2, w0 + 0.6, 0)); drop = g + top - ground_xy(pf.x, pf.y); nr = max(0, int(math.ceil(drop / 0.17)) - 1)
    for k in range(nr):
        zt = top - (k + 1) * drop / (nr + 1); fbox(XFm, f'{nm} step {k}', u0, u1, w0 + k * 0.32, w0 + (k + 1) * 0.32, top - drop - 0.3, zt, mat or m_conc)
    return nr, round(drop, 2)
EXCL = {}   # osm -> list of (xy Vector, radius, max height above grade) where window reveals are skipped
ENTR_3I = []
def portal(osm, tag, pc, n2, g, kind='secondary', label=None):
    XFm = frame_xf(pc, n2, g); nm = f'{tag} entrance ({kind}, 3i UNVERIFIED)'
    if kind == 'secondary':   # door surround in the Morehead west style, on the wall plane (covers the ground-floor window cell)
        for s_ in (-1, 1):
            fbox(XFm, f'{nm} pilaster {s_:+d}', s_*1.15, s_*1.45, -0.02, 0.18, 0.0, 2.95, m_stucco_plain)
            fbox(XFm, f'{nm} pilaster base {s_:+d}', s_*1.1, s_*1.5, -0.02, 0.22, 0.0, 0.28, m_stucco_plain)
            fbox(XFm, f'{nm} lantern {s_:+d}', s_*1.75 - 0.09, s_*1.75 + 0.09, 0.12, 0.3, 2.2, 2.48, m_lamp_glass)
            fbox(XFm, f'{nm} lantern cap {s_:+d}', s_*1.75 - 0.11, s_*1.75 + 0.11, 0.1, 0.32, 2.48, 2.55, m_lamp_body)
            fbox(XFm, f'{nm} lantern arm {s_:+d}', s_*1.75 - 0.02, s_*1.75 + 0.02, -0.02, 0.2, 2.5, 2.56, m_lamp_body)
        fbox(XFm, f'{nm} entablature', -1.5, 1.5, -0.02, 0.2, 2.95, 3.45, m_stucco_plain)
        fbox(XFm, f'{nm} cornice', -1.62, 1.62, -0.02, 0.28, 3.45, 3.6, m_stucco_plain)
        fbox(XFm, f'{nm} door leaves', -1.15, 1.15, -0.03, 0.02, 0.0, 2.95, m_door)
        for s_ in (-1, 1):
            fbox(XFm, f'{nm} door glass {s_:+d}', s_*0.12 if s_ > 0 else -0.95, 0.95 if s_ > 0 else -0.12, 0.02, 0.025, 0.95, 2.3, m_dark_glass)
            fbox(XFm, f'{nm} pull {s_:+d}', s_*0.06 - 0.015, s_*0.06 + 0.015, 0.02, 0.07, 1.0, 1.4, m_steel)
        fbox(XFm, f'{nm} transom', -0.95, 0.95, 0.02, 0.025, 2.45, 2.85, m_dark_glass)
        fbox(XFm, f'{nm} landing', -1.9, 1.9, -0.05, 1.5, -1.5, 0.12, m_conc)
        print('3i steps', tag, steps_down(XFm, nm, -1.9, 1.9, 1.5, g))
        EXCL.setdefault(osm, []).append((pc.copy(), 1.9, 3.6))
    else:   # main portal (Life Hall): projecting two-storey-high bay with pilasters, entablature, arched transom, landing with steps
        Hp = 5.0
        fbox(XFm, f'{nm} body', -2.4, 2.4, -0.05, 0.4, -0.3, Hp, m_stucco_plain)
        fbox(XFm, f'{nm} cornice', -2.6, 2.6, -0.05, 0.62, Hp - 0.05, Hp + 0.25, m_stucco_plain)
        fbox(XFm, f'{nm} parapet panel', -1.8, 1.8, -0.05, 0.38, Hp + 0.25, Hp + 0.95, m_stucco_plain)
        fbox(XFm, f'{nm} parapet cap', -1.95, 1.95, -0.05, 0.48, Hp + 0.95, Hp + 1.07, m_stucco_plain)
        for s_ in (-1, 1):
            fbox(XFm, f'{nm} pilaster {s_:+d}', s_*1.55, s_*2.05, 0.4, 0.62, 0.0, 3.9, m_stucco_plain)
            fbox(XFm, f'{nm} capital {s_:+d}', s_*1.5, s_*2.1, 0.4, 0.68, 3.7, 3.9, m_stucco_plain)
            for kf in range(4):
                uu = s_*1.55 + s_*(0.07 + kf*0.11)
                fbox(XFm, f'{nm} fillet {s_:+d}{kf}', uu - 0.02, uu + 0.02, 0.62, 0.65, 0.35, 3.6, m_stucco_plain)
            fbox(XFm, f'{nm} lantern {s_:+d}', s_*1.25 - 0.09, s_*1.25 + 0.09, 0.62, 0.8, 2.3, 2.58, m_lamp_glass)
            fbox(XFm, f'{nm} lantern cap {s_:+d}', s_*1.25 - 0.11, s_*1.25 + 0.11, 0.6, 0.82, 2.58, 2.65, m_lamp_body)
        fbox(XFm, f'{nm} entablature', -2.15, 2.15, 0.4, 0.62, 3.9, 4.45, m_stucco_plain)
        fbox(XFm, f'{nm} entablature cornice', -2.3, 2.3, 0.4, 0.72, 4.45, 4.6, m_stucco_plain)
        fbox(XFm, f'{nm} door recess', -1.1, 1.1, 0.33, 0.41, 0.0, 2.8, m_door)
        for s_ in (-1, 1):
            fbox(XFm, f'{nm} door glass {s_:+d}', 0.12 if s_ > 0 else -0.95, 0.95 if s_ > 0 else -0.12, 0.41, 0.415, 0.95, 2.45, m_dark_glass)
        arcp = [(-1.1, 2.85)] + [(1.1 * math.cos(math.radians(180 - a)), 2.85 + 0.75 * math.sin(math.radians(180 - a))) for a in range(0, 181, 15)]
        fprism(XFm, f'{nm} arched transom glass', arcp, 0.4, 0.405, m_dark_glass)
        fprism(XFm, f'{nm} arched transom frame', [(u*1.12, 2.8 + (z - 2.85)*1.12) for u, z in arcp], 0.39, 0.402, m_frame)
        if label: ftext(XFm, f'{nm} lettering', label, 0.22, 0, 0.73, 4.17, m_letters)
        fbox(XFm, f'{nm} landing', -2.8, 2.8, 0.3, 2.6, -1.5, 0.14, m_conc)
        print('3i steps', tag, steps_down(XFm, nm, -2.8, 2.8, 2.6, g, 0.14))
        EXCL.setdefault(osm, []).append((pc.copy(), 2.45, 5.2))
    ENTR_3I.append((tag, kind, round(pc.x, 1), round(pc.y, 1)))
    return XFm

# Morehead secondary entrances on the N / S / E faces (UNVERIFIED: positions picked at the run midpoints, door style copied from the west front)
for tag, near, wn in (('Morehead east', (-10.9, -49.7), (0.97, -0.24)), ('Morehead south', (-32.7, -70.2), (-0.24, -0.97)), ('Morehead north', (-17.0, -14.4), (0.24, 0.97))):
    try:
        pc, t2, n2, g, L, inf = facade_frame('312933183', near, wn); portal('312933183', tag, pc, n2, g, 'secondary'); print('3i portal', tag, inf, round(L, 1))
    except Exception as ex: print('3i portal failed', tag, ex)
# Life Hall main entrance: longest exterior west run (faces the campus walks; UNVERIFIED - no Life Hall photo on Commons or MSU pages found)
try:
    _lpc, _lt, _ln, _lg, _lL, _linf = facade_frame('313021866', (12.5, 97.2), (-0.97, 0.23))
    LIFE_XF = portal('313021866', 'Life Hall main', _lpc, _ln, _lg, 'main', label=None); LIFE_FRONT = (_lpc, _ln, _lg); print('3i Life portal', _linf, round(_lL, 1))
except Exception as ex:
    LIFE_FRONT = None; print('3i Life portal failed', ex)

# continuous sill course + low base moulding on Morehead (all faces, as in the west-front photo) and Life Hall (UNVERIFIED)
def string_courses(osm, skip_pts):
    b = _bld(osm); wo = _walls(osm); wb_ = float(wo['win_bottom']); wi = np.nonzero(WB == b['bid'])[0]; Q = WV[wi]; U = WU[wi]; plg = _poly(osm)
    boxes = []; nseg = 0
    for k in range(len(wi)):
        a = Q[k, 0, :2]; c = Q[k, 1, :2]; L = float(np.linalg.norm(c - a))
        if L < 0.3: continue
        t2 = (c - a) / L; n2 = np.array([t2[1], -t2[0]])
        if plg.contains(_shp.Point(*((a + c) / 2 + n2 * 1.2))): n2 = -n2   # eave ring is offset outward by the overhang (<=0.75 m)
        g = float(Q[k, 0, 2] - U[k, 0, 1]); ns = max(1, int(L / 0.6))
        for j in range(ns):
            s0, s1 = L * j / ns, L * (j + 1) / ns; m = a + t2 * (s0 + s1) / 2
            if any((Vector((float(m[0]), float(m[1]))) - p).length < r for p, r in skip_pts): continue
            ang = math.atan2(t2[1], t2[0]); ln = s1 - s0 + 0.02
            for (w0, w1, z0, z1) in ((0.0, 0.09, wb_ - 0.12, wb_ - 0.02), (0.0, 0.06, 0.32, 0.42), (0.0, 0.03, -0.3, 0.32)):
                cx = m[0] + n2[0] * (w0 + w1) / 2; cy = m[1] + n2[1] * (w0 + w1) / 2
                boxes.append((float(cx), float(cy), ang, ln, w1 - w0, g + z0, g + z1))
            nseg += 1
    _boxes_mesh(f'{b["name"]} sill course + base moulding (3i)', boxes, c_3i, m_band)
    print('3i string courses', b['name'], nseg)
try:
    _skM = [(p, r) for p, r, h in EXCL.get('312933183', [])] + ([(Vector((ME['center'][0], ME['center'][1])), 3.3)] if ME else [])
    string_courses('312933183', _skM)
    string_courses('313021866', [(p, r) for p, r, h in EXCL.get('313021866', [])])
except Exception as ex: print('3i string courses failed', ex)

# CCOM main entrance (Commons 2021 photo): west face just south of the white tower, where the brick forecourt meets the building (ortho)
CCOM_ENT = None
try:
    pc, t2, n2, g, L, inf = facade_frame('1188721159', (-21.0, 12.0), (-0.97, 0.24), snap='pier')
    XFc = frame_xf(pc, n2, g); CCOM_ENT = (pc, n2, g); print('3i CCOM entrance', inf, round(L, 1), (round(pc.x, 1), round(pc.y, 1)))
    _top = min(12.3, float(M['hip_info']['1188721159'][0]) - 0.5); R1, R2, SP = 2.9, 2.55, 6.0
    # outer piers + spandrel (w 0..0.45) and inner tier (w 0..0.3): tiered tan stone surround
    for s_ in (-1, 1):
        fbox(XFc, f'CCOM entrance pier {s_:+d}', s_*R1, s_*3.6, -0.03, 0.45, -0.2, _top, m_cast)
        fbox(XFc, f'CCOM entrance inner tier {s_:+d}', s_*R2, s_*R1, -0.03, 0.3, -0.2, SP, m_cast)
    def _spandrel(R, w1, nm):
        prof = [(-3.6 if R == R1 else -R1, SP), (-R, SP)] + [(R * math.cos(math.radians(a)), SP + R * math.sin(math.radians(a))) for a in range(180, -1, -10)][1:-1] + [(R, SP), (3.6 if R == R1 else R1, SP),
                (3.6 if R == R1 else R1, _top if R == R1 else SP + R1), (-3.6 if R == R1 else -R1, _top if R == R1 else SP + R1)]
        fprism(XFc, nm, prof, -0.03, w1, m_cast)
    _spandrel(R1, 0.45, 'CCOM entrance spandrel (outer)'); _spandrel(R2, 0.3, 'CCOM entrance arch ring (inner tier)')
    fbox(XFc, 'CCOM entrance cornice', -3.8, 3.8, -0.03, 0.6, _top - 0.05, _top + 0.2, m_cast)
    fbox(XFc, 'CCOM entrance keystone', -0.28, 0.28, -0.03, 0.5, SP + R1 - 0.25, SP + R1 + 0.35, m_cast)
    # glass curtain: 7 columns x 10 rows (photo), arched head
    gl = [(-R2, 0.0), (R2, 0.0)] + [(R2 * math.cos(math.radians(a)), SP + R2 * math.sin(math.radians(a))) for a in range(0, 181, 6)]
    fprism(XFc, 'CCOM atrium glass (arched, 7x10 grid)', gl, 0.06, 0.07, m_atr)
    mb = []; ncol, nrow = 7, 10; topz = SP + R2
    for i in range(1, ncol):
        u = -R2 + 2 * R2 * i / ncol; zt = SP + math.sqrt(max(R2 * R2 - u * u, 0))
        mb.append((u, -0.035, 0.035, 0.0, zt))
    for j in range(1, nrow):
        z = topz * j / nrow; hw = R2 if z <= SP else math.sqrt(max(R2 * R2 - (z - SP) ** 2, 0))
        if hw > 0.1: mb.append((0.0, -hw, hw, z - 0.03, z + 0.03))
    for k_, (u, a_, b_, z0, z1) in enumerate(mb):
        if z1 - z0 > 0.1: fbox(XFc, f'CCOM atrium mullion v{k_}', u - 0.04, u + 0.04, 0.07, 0.16, z0, z1, m_mahog)
        else: fbox(XFc, f'CCOM atrium mullion h{k_}', a_, b_, 0.07, 0.15, z0, z1, m_mahog)
    _ring = [(R2 * math.cos(math.radians(a)), SP + R2 * math.sin(math.radians(a))) for a in range(0, 181, 6)]
    _ri = [((R2 - 0.1) * math.cos(math.radians(a)), SP + (R2 - 0.1) * math.sin(math.radians(a))) for a in range(180, -1, -6)]
    fprism(XFc, 'CCOM atrium arch frame', _ring + _ri, 0.07, 0.17, m_mahog)
    # two pairs of double doors (photo) with steel push bars
    for s_ in (-1, 1):
        uc = s_ * 1.25
        fbox(XFc, f'CCOM door frame {s_:+d}', uc - 0.95, uc + 0.95, 0.07, 0.2, 2.55, 2.68, m_mahog)
        for e_ in (-0.95, 0.0, 0.95):
            fbox(XFc, f'CCOM door stile {s_:+d}{e_}', uc + e_ - 0.05, uc + e_ + 0.05, 0.07, 0.2, 0.0, 2.6, m_mahog)
        for e_ in (-0.47, 0.47):
            fbox(XFc, f'CCOM push bar {s_:+d}{e_}', uc + e_ - 0.36, uc + e_ + 0.36, 0.2, 0.24, 1.0, 1.04, m_steel)
    fbox(XFc, 'CCOM entrance threshold', -R2, R2, -0.03, 0.6, -1.5, 0.04, m_conc)
    print('3i steps CCOM', steps_down(XFc, 'CCOM entrance', -R2, R2, 0.6, g, 0.04, m_cast))
    EXCL.setdefault('1188721159', []).append((pc.copy(), 3.7, 99.0))
    # trash / landfill / recycling trio against the wall beside the arch (photo)
    for kb, colr in enumerate(((0.02, 0.02, 0.02), (0.35, 0.02, 0.02), (0.02, 0.06, 0.35))):
        u = 4.2 + kb * 0.7; p = pc + Vector((n2.y, -n2.x)) * u + n2 * 0.45
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.29, depth=0.95, location=(p.x, p.y, ground_xy(p.x, p.y) + 0.475))
        bo = bpy.context.active_object; bo.name = f'CCOM entrance bin {kb} (photo)'; bo.data.materials.append(rgb(f'Bin_plastic_{kb}', colr, 0.45))
        for cc in bo.users_collection: cc.objects.unlink(bo)
        c_3i.objects.link(bo)
    # brick forecourt from the arch to the main walk (ortho shows a terracotta herringbone strip; photo: herringbone brick)
    m_herr, _nth, _bh, _mph = pbr('Brick_forecourt_herringbone', 'PavingStones126A', 1.2, tint=(1.05, 0.72, 0.55), box=False, bump=0.4)
    _mph.inputs['Rotation'].default_value = (0, 0, math.atan2(n2.y, n2.x) + math.radians(45))
    tt = Vector((n2.y, -n2.x)); FV, FF = [], []; nu_, nw_ = 9, 19
    for j in range(nw_):
        for i in range(nu_):
            u = -3.4 + 6.8 * i / (nu_ - 1); w = 0.6 + 8.6 * j / (nw_ - 1); p = pc + tt * u + n2 * w
            FV.append((p.x, p.y, ground_xy(p.x, p.y) + 0.07))
    FF = [(j*nu_+i, j*nu_+i+1, (j+1)*nu_+i+1, (j+1)*nu_+i) for j in range(nw_-1) for i in range(nu_-1)]
    mesh_obj('CCOM brick forecourt (ortho + photo)', FV, FF, c_3i, m_herr)
    # tower lettering (photo, 2021): black sans-serif on the tower's west face; height on the shaft approximate
    _tp = M['tall_parts'][0]['coords']; _tw = max(((np.array(_tp[k]), np.array(_tp[(k + 1) % len(_tp)])) for k in range(len(_tp))), key=lambda e: -(((e[0] + e[1]) / 2) @ np.array([0.97, -0.24])))
    _tm = (_tw[0] + _tw[1]) / 2; _tn = Vector((-0.97, 0.24)); _tc = Vector((float(_tm[0]), float(_tm[1]))) + _tn * 0.02
    _tg = ground_xy(_tc.x, _tc.y); XFt = frame_xf(_tc, _tn, _tg)
    m_blk = rgb('Lettering_black', (0.01, 0.01, 0.01), 0.4)
    # placed in the blank band between the ground-floor window heads and the second-floor sills (1731 test: 6.75-7.35 m overlapped a window)
    _wt = _walls('1188721159'); _zb2 = float(_wt['win_bottom']) + float(_wt['floor_h']); _zh1 = float(_wt['win_bottom']) + float(_wt['win_h']) + 0.16
    _zl = _zh1 + 0.36;   # 1745: band centre still clipped the 2nd-floor tower window surround -> sit just above the ground-floor heads
    print('3i tower lettering band', round(_zh1, 2), round(_zb2, 2))
    ftext(XFt, 'CCOM tower lettering COLLEGE OF', 'COLLEGE OF', 0.24, 0, 0.04, _zl + 0.15, m_blk)
    ftext(XFt, 'CCOM tower lettering COMMUNICATION AND MEDIA', 'COMMUNICATION AND MEDIA', 0.18, 0, 0.04, _zl - 0.14, m_blk)
except Exception as ex:
    import traceback; traceback.print_exc(); print('3i CCOM entrance failed', ex)
print('3i entrances', ENTR_3I, 'CCOM', CCOM_ENT is not None)

# ---------- day 2: Morehead window reveals and sills (geometry, matches the facade shader grid)
def window_reveals(osm_id, pav=None, cam_xy=None, mat=None, frame_mat=None, depth=0.14, zmax=None):
    bb = [x for x in M['buildings'] if x['osm_id'] == osm_id][0]; i = bb['bid']
    wo = [o for o in bpy.data.objects if o.get('osm_id') == osm_id and o.name.endswith('walls')][0]
    pw, ww, fh, wh, wb, wt = (wo[k] for k in ('win_pitch', 'win_w', 'floor_h', 'win_h', 'win_bottom', 'win_top'))
    u0off = float(wo.get('win_u0', 0.0))
    wi = np.nonzero(WB == i)[0]; Q = WV[wi]; U = WU[wi]
    P0 = Q[:, 0, :2]; P1 = Q[:, 1, :2]; u0 = U[:, 0, 0]; u1 = U[:, 1, 0]
    gref = Q[:, 0, 2] - U[:, 0, 1]
    cen = Vector((float(Q[:, :, 0].mean()), float(Q[:, :, 1].mean()), 0))
    V, F = [], []
    def box(o_, t_, n_, a0, a1, w0, w1, z0, z1):
        base = len(V)
        for z in (z0, z1):
            for a, w in ((a0, w0), (a1, w0), (a1, w1), (a0, w1)):
                p = o_ + t_*a + n_*w; V.append((p.x, p.y, z))
        F.extend([(base+0, base+3, base+2, base+1), (base+4, base+5, base+6, base+7), (base+0, base+1, base+5, base+4),
                  (base+1, base+2, base+6, base+5), (base+2, base+3, base+7, base+6), (base+3, base+0, base+4, base+7)])
    total = u1.max(); m = 0; count = 0; FB = []
    while (m + 0.5) * pw < total:
        uc = (m + 0.5) * pw + u0off; m += 1
        k = int(np.searchsorted(u0, uc, side='right') - 1)
        if k < 0 or k >= len(u0): continue
        ka = int(np.searchsorted(u0, uc - ww/2, side='right') - 1); kb = int(np.searchsorted(u0, uc + ww/2, side='right') - 1)
        def tdir(j):
            d_ = Vector((*(P1[j] - P0[j]), 0)); return d_.normalized() if d_.length > 1e-6 else Vector((1, 0, 0))
        t_ = tdir(k)
        if ka < 0 or kb >= len(u0) or tdir(ka).dot(t_) < 0.995 or tdir(kb).dot(t_) < 0.995: continue
        fr = (uc - u0[k]) / max(u1[k] - u0[k], 1e-6)
        pc = Vector((*(P0[k] + (P1[k] - P0[k]) * fr), 0))
        n_ = Vector((t_.y, -t_.x, 0))
        if (pc + n_ - cen).length < (pc - n_ - cen).length: n_ = -n_
        if pav is not None and (pc - pav).length < 3.4: continue
        _ex = [(p_, r_, h_) for p_, r_, h_ in EXCL.get(osm_id, []) if (pc.xy - p_).length < r_]
        if cam_xy is not None:   # only faces that the eye-level camera sees (memory)
            dv = Vector((cam_xy[0] - pc.x, cam_xy[1] - pc.y, 0))
            if dv.length > 160 or dv.normalized().dot(n_) < 0.15: continue
        g = float(gref[k])
        row = 0
        while True:
            zb = g + wb + row * fh; zt = zb + wh
            if zb - g > wt or zt - g > wt + 0.3: break
            if zmax is not None and zt + 0.3 > zmax: break
            if any(zb - g < h_ for p_, r_, h_ in _ex): row += 1; continue
            hw = ww/2
            box(pc, t_, n_, -hw - 0.10, -hw + 0.0, -0.02, 0.14, zb, zt)        # jamb L
            box(pc, t_, n_, hw - 0.0, hw + 0.10, -0.02, 0.14, zb, zt)          # jamb R
            box(pc, t_, n_, -hw - 0.10, hw + 0.10, -0.02, 0.16, zt, zt + 0.16) # head
            box(pc, t_, n_, -hw - 0.16, hw + 0.16, -0.02, 0.22, zb - 0.08, zb) # sill
            if frame_mat is not None:   # aluminium frame inside the reveal + centre mullion + transom (glass sits on the wall plane = recessed)
                FB.append((pc, t_, n_, hw, zb, zt))
            row += 1; count += 1
    o = mesh_obj(f"{bb['name']} window reveals + sills", V, F, c_d2, mat or m_stucco_plain)
    if FB:
        V.clear(); F.clear()
        for (pc, t_, n_, hw, zb, zt) in FB:
            box(pc, t_, n_, -hw, -hw + 0.06, -0.02, 0.05, zb, zt); box(pc, t_, n_, hw - 0.06, hw, -0.02, 0.05, zb, zt)
            box(pc, t_, n_, -hw, hw, -0.02, 0.05, zt - 0.06, zt); box(pc, t_, n_, -hw, hw, -0.02, 0.05, zb, zb + 0.06)
            box(pc, t_, n_, -0.03, 0.03, -0.02, 0.06, zb, zt); box(pc, t_, n_, -hw, hw, -0.02, 0.05, zb + 0.62*(zt - zb), zb + 0.62*(zt - zb) + 0.05)
        mesh_obj(f"{bb['name']} window frames (aluminium)", V, F, c_d2, frame_mat)
    print('reveals', bb['name'], count)
    return o
try:
    _pav = Vector((*M['morehead_entrance']['center'], 0)) if M.get('morehead_entrance') else None
    window_reveals('312933183', _pav)
    window_reveals('313021866', None)   # 3i: Life Hall reveals + sills (same casement grid as Morehead; UNVERIFIED)
    _sc = cents['1188721159']   # CAM_eye_west_walk sits at scm + (-48, -12) (see cameras below)
    window_reveals('1188721159', None, cam_xy=(_sc[0] - 48, _sc[1] - 12), zmax=_sc[2] + M['hip_info']['1188721159'][0] - 0.4, mat=m_scm_plain,
                   frame_mat=rgb('CCOM_window_frame_alu', (0.11, 0.11, 0.115), 0.35, 0.8))
except Exception as ex:
    print('reveals failed', ex)
# ---------- trees (instanced prototypes)
c_tp = coll('Tree_prototypes'); c_tr = coll('Trees_LiDAR')
leaf = bpy.data.materials.new('Leaves'); leaf.use_nodes = True; N = leaf.node_tree.nodes; L = leaf.node_tree.links
bs = N['Principled BSDF']; oinfo = N.new('ShaderNodeObjectInfo'); ramp = N.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color = (0.03, 0.06, 0.015, 1); ramp.color_ramp.elements[1].color = (0.22, 0.16, 0.03, 1)
e = ramp.color_ramp.elements.new(0.8); e.color = (0.07, 0.11, 0.025, 1); ramp.color_ramp.elements[1].position = 1.0
L.new(oinfo.outputs['Random'], ramp.inputs[0]); L.new(ramp.outputs[0], bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value = 0.7; bs.inputs['Subsurface Weight'].default_value = 0.0
nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 6; bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.6
L.new(nz.outputs['Fac'], bp.inputs['Height']); L.new(bp.outputs['Normal'], bs.inputs['Normal'])
bark = rgb('Bark', (0.09, 0.07, 0.05), 0.9)
protos = []
random.seed(7)
for k in range(4):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.035, radius2=0.02, depth=0.45, matrix=__import__('mathutils').Matrix.Translation((0, 0, 0.225)))
    for j in range(22):
        r = random.uniform(0.07, 0.13)
        th_ = random.uniform(0, 6.283); rad = random.uniform(0, 0.17); zc = random.uniform(0.5, 0.88)
        c = (rad*math.cos(th_), rad*math.sin(th_), zc)
        res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r, matrix=__import__('mathutils').Matrix.Translation(c))
        for v in res['verts']:
            v.co += (v.co - Vector(c)).normalized() * random.uniform(-0.025, 0.025) * (r / 0.1)
    for j in range(5):
        a_ = random.uniform(0, 6.283)
        bmesh.ops.create_cone(bm, cap_ends=False, segments=5, radius1=0.012, radius2=0.004, depth=0.25,
            matrix=__import__('mathutils').Matrix.Translation((0.07*math.cos(a_), 0.07*math.sin(a_), 0.55)) @ __import__('mathutils').Euler((0.7*math.sin(a_), -0.7*math.cos(a_), 0)).to_matrix().to_4x4())
    for f in bm.faces: f.material_index = 1 if (f.calc_center_median().z < 0.45 or f.calc_area() < 0.0004 and len(f.verts) == 4) else 0
    me = bpy.data.meshes.new(f'tree_proto_{k}'); bm.to_mesh(me); bm.free()
    me.materials.append(leaf); me.materials.append(bark)
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(f'tree_proto_{k}', me); c_tp.objects.link(o); protos.append(me)
c_tp.hide_render = True; c_tp.hide_viewport = True
T = G['trees']
USE_ASSET_TREES = True
for j, (x, y, z, h) in (enumerate([]) if USE_ASSET_TREES else enumerate(T)):
    o = bpy.data.objects.new(f'tree_{j:04d}', protos[j % 4]); c_tr.objects.link(o)
    s = float(h) / 0.9; o.location = (float(x), float(y), float(z) - 0.2); o.scale = (s*random.uniform(0.85, 1.1), s*random.uniform(0.85, 1.1), s)
    o.rotation_euler[2] = random.uniform(0, 6.28)
# ---------- sun (NOAA solar position) + sky
def sun_pos(lat, lon, y, mo, d, hr_utc):
    import datetime
    dt = datetime.datetime(y, mo, d) + datetime.timedelta(hours=hr_utc)
    jd = dt.toordinal() + 1721424.5 + hr_utc/24 - (0 if True else 0)
    jd = 367*y - int(7*(y+int((mo+9)/12))/4) + int(275*mo/9) + d + 1721013.5 + hr_utc/24
    T_ = (jd - 2451545.0)/36525
    L0 = (280.46646 + T_*(36000.76983 + T_*0.0003032)) % 360; Mn = 357.52911 + T_*(35999.05029 - 0.0001537*T_)
    ec = 0.016708634 - T_*(0.000042037 + 0.0000001267*T_)
    Cc = math.sin(math.radians(Mn))*(1.914602 - T_*(0.004817+0.000014*T_)) + math.sin(math.radians(2*Mn))*(0.019993-0.000101*T_) + math.sin(math.radians(3*Mn))*0.000289
    tl = L0 + Cc; om = 125.04 - 1934.136*T_; lam = tl - 0.00569 - 0.00478*math.sin(math.radians(om))
    eps = 23 + (26 + (21.448 - T_*(46.815 + T_*(0.00059 - T_*0.001813)))/60)/60 + 0.00256*math.cos(math.radians(om))
    decl = math.degrees(math.asin(math.sin(math.radians(eps))*math.sin(math.radians(lam))))
    yv = math.tan(math.radians(eps/2))**2
    eot = 4*math.degrees(yv*math.sin(2*math.radians(L0)) - 2*ec*math.sin(math.radians(Mn)) + 4*ec*yv*math.sin(math.radians(Mn))*math.cos(2*math.radians(L0)) - 0.5*yv*yv*math.sin(4*math.radians(L0)) - 1.25*ec*ec*math.sin(2*math.radians(Mn)))
    tst = (hr_utc*60 + eot + 4*lon) % 1440; ha = tst/4 - 180
    zen = math.degrees(math.acos(math.sin(math.radians(lat))*math.sin(math.radians(decl)) + math.cos(math.radians(lat))*math.cos(math.radians(decl))*math.cos(math.radians(ha))))
    az = (math.degrees(math.atan2(math.sin(math.radians(ha)), math.cos(math.radians(ha))*math.sin(math.radians(lat)) - math.tan(math.radians(decl))*math.cos(math.radians(lat)))) + 180) % 360
    return 90 - zen, az
SUN_LOCAL = 13.0  # midday (solar noon here is ~12:57 EDT)
elev, az = sun_pos(LAT, LON, 2026, 10, 8, SUN_LOCAL + 4)
sc['sun_time'] = '2026-10-08 13:00 EDT'; sc['sun_elev_deg'] = elev; sc['sun_az_deg'] = az
sd = bpy.data.lights.new('Sun', 'SUN'); sd.energy = 3.6; sd.angle = math.radians(0.53)
so = bpy.data.objects.new('Sun', sd); sc.collection.objects.link(so)
# Blender: +Y = grid north (state plane; convergence ~0.2 deg ignored), sun light points along -Z of object
so.rotation_euler = (math.radians(90 - elev), 0, math.radians(180 - az))
w = bpy.data.worlds.new('Sky'); sc.world = w; w.use_nodes = True; wn = w.node_tree.nodes
w.cycles.sampling_method = 'MANUAL'; w.cycles.sample_map_resolution = 1024   # memory: AUTOMATIC built a huge world importance map (render peak 1.21 GB -> ~0.88 GB)
sky = wn.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'; sky.sun_disc = False
sky.sun_elevation = math.radians(elev); sky.sun_rotation = math.radians(az)
sky.altitude = 140; sky.air_density = 1.0; sky.dust_density = 1.5
bg = wn['Background']; bg.inputs['Strength'].default_value = 0.35
w.node_tree.links.new(sky.outputs['Color'], bg.inputs['Color'])
try:
    sp = sc.sun_pos_properties; sp.latitude = LAT; sp.longitude = LON; sp.UTC_zone = -4; sp.use_daylight_savings = False
    sp.year = 2026; sp.month = 10; sp.day = 8; sp.time = SUN_LOCAL; sp.sun_object = so; sp.usage_mode = 'NORMAL'
except Exception as ex: print('sun_position addon not configured:', ex)
# ---------- render settings
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 48; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6; sc.render.threads_mode = 'FIXED'; sc.render.threads = 7; sc.render.use_persistent_data = True
sc.render.resolution_x = 1280; sc.render.resolution_y = 720; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 90
# ---------- cameras
def cam(name, loc, target, lens=28):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 3000
    o = bpy.data.objects.new(name, cd); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
json.dump({k: [float(a) for a in v] for k, v in cents.items()}, open(f'{ROOT}/data/centroids.json', 'w'))
scm, mor, life = cents['1188721159'], cents['312933183'], cents['313021866']
cx = (scm[0]+mor[0]+life[0])/3; cy = (scm[1]+mor[1]+life[1])/3
cam('CAM_aerial_oblique_SW', (cx-120, cy-135, 225), (cx+8, cy+12, 138), 32)
cam('CAM_eye_west_walk', (scm[0]-48, scm[1]-12, scm[2]+1.7+1.5), (scm[0], scm[1]+8, scm[2]+8), 24)
cam('CAM_eye_south_Morehead', (mor[0]-18, mor[1]-60, mor[2]+1.7), (mor[0], mor[1], mor[2]+7), 24)
mo = [o for o in bpy.data.objects if o.name.startswith('Morehead Hall walls')][0]
mxs = [v.co.x for v in mo.data.vertices]; wx = min(mxs)
cam('CAM_closeup_Morehead_west', (wx-13, mor[1]-20, mor[2]+2.5), (wx, mor[1]-3, mor[2]+7.5), 30)
if ME:
    _c = Vector((*ME['center'], ME['ground'])); _n = Vector((*ME['n'], 0)); _t = Vector((*ME['t'], 0))
    _rc = cam('CAM_ref_Morehead_west_photo', tuple(_c + _n*13.4 + Vector((0, 0, 1.6))), tuple(_c + Vector((0, 0, 1.6))), 18); _rc.data.shift_y = 0.215
    cam('CAM_closeup_Morehead_entrance', tuple(_c + _n*9 - _t*4.5 + Vector((0, 0, 2.2))), tuple(_c + _n*0.5 + Vector((0, 0, 4.6))), 24)
    tp0 = M['tall_parts'][0]; tcx = sum(x for x, y in tp0['coords'])/len(tp0['coords']); tcy = sum(y for x, y in tp0['coords'])/len(tp0['coords'])
# 3i: two eye-level cameras on the new faces (1.7 m eye height, standing on the ground / walk in front of each face)
if LIFE_FRONT:
    _lp, _lnn, _lgg = LIFE_FRONT; _lt3 = Vector((_lnn.y, -_lnn.x, 0)); _ln3 = Vector((_lnn.x, _lnn.y, 0))
    _lc = Vector((_lp.x, _lp.y, 0)) + _ln3 * float(os.environ.get('LIFE_CAM_D', '19')) + _lt3 * 4.0
    cam('CAM_eye_Life_front', (_lc.x, _lc.y, ground_xy(_lc.x, _lc.y) + 1.7), tuple(Vector((_lp.x, _lp.y, _lgg + 5.4)) + _lt3 * 1.0), 24)   # aim a bit higher: less of the flat far-lawn shader in frame (no grass hair here, memory)
if CCOM_ENT:
    _cp, _cnn, _cgg = CCOM_ENT; _ct3 = Vector((_cnn.y, -_cnn.x, 0)); _cn3 = Vector((_cnn.x, _cnn.y, 0))
    _cc = Vector((_cp.x, _cp.y, 0)) + _cn3 * float(os.environ.get('CCOM_CAM_D', '19.5')) - _ct3 * 3.5
    cam('CAM_eye_CCOM_entrance', (_cc.x, _cc.y, ground_xy(_cc.x, _cc.y) + 1.7), tuple(Vector((_cp.x, _cp.y, _cgg + 5.4)) - _ct3 * 2.0), 22)
sc.camera = bpy.data.objects['CAM_aerial_oblique_SW']
# ---------- 3f: gutters + downspouts + splash blocks on eave faces seen from the eye-level cameras / a walkthrough near them
# Life Hall and CCOM: UNVERIFIED (no photo of those faces). Morehead: not on the west front - the Commons photo shows no gutter or downspout there.
_gcams = [bpy.data.objects[c].location.xy.copy() for c in ('CAM_eye_west_walk', 'CAM_ref_Morehead_west_photo', 'CAM_closeup_Morehead_entrance', 'CAM_eye_south_Morehead', 'CAM_eye_Life_front', 'CAM_eye_CCOM_entrance') if c in bpy.data.objects]
m_gut = rgb('Gutter_downspout_painted_bronze', (0.07, 0.055, 0.04), 0.4, 0.3)
m_splash = rgb('Splash_block_concrete', (0.52, 0.5, 0.47), 0.85)
def _segbox(V_, F_, P, Q, side, a, b_):
    d = Q - P; dn = d.normalized(); s_ = (side - dn * side.dot(dn)).normalized(); th = dn.cross(s_); base = len(V_)
    for pp in (P, Q):
        for (i_, j_) in ((-1, -1), (1, -1), (1, 1), (-1, 1)): V_.append(tuple(pp + s_ * (a / 2 * i_) + th * (b_ / 2 * j_)))
    F_.extend([(base, base+1, base+2, base+3), (base+7, base+6, base+5, base+4), (base, base+4, base+5, base+1), (base+1, base+5, base+6, base+2), (base+2, base+6, base+7, base+3), (base+3, base+7, base+4, base)])
def _tz(x, y):
    hit, loc, *_ = ter.ray_cast(Vector((x, y, 400)), Vector((0, 0, -1)), distance=600); return loc.z if hit else 135.0
GV, GF, DV, DF, BV, BF, KV, KF, BRV, BRF = [], [], [], [], [], [], [], [], [], []; ndsp = 0
for E in EAVES:
    if E['osm'] not in ('1188721159', '313021866', '312933183'): continue
    wo_ = [o for o in bpy.data.objects if o.get('osm_id') == E['osm'] and o.name.endswith('walls')][0]
    _pw, _ww, _u0 = float(wo_['win_pitch']), float(wo_['win_w']), float(wo_.get('win_u0', 0.0))
    _wi = np.nonzero(WB == [x for x in M['buildings'] if x['osm_id'] == E['osm']][0]['bid'])[0]; _WQ = WV[_wi]; _WU = WU[_wi]
    def _win_shift(q):   # shift (m, along the wall) that moves a downspout off a window column onto the pier between windows
        a_ = _WQ[:, 0, :2]; c_ = _WQ[:, 1, :2]; ab = c_ - a_; L2 = (ab ** 2).sum(1) + 1e-9
        tt = np.clip(((q - a_) * ab).sum(1) / L2, 0, 1); dd = np.linalg.norm(a_ + ab * tt[:, None] - q, axis=1); j = int(np.argmin(dd))
        u = _WU[j, 0, 0] + (_WU[j, 1, 0] - _WU[j, 0, 0]) * tt[j]; f = ((u - _u0) / _pw) % 1.0
        return 0.0 if abs(f - 0.5) * _pw > _ww / 2 + 0.25 else ((-f * _pw) if f < 0.5 else ((1 - f) * _pw))
    cc_, nv_ = E['cc'], len(E['cc'])
    for k in range(nv_):
        if k == E['skip']: continue
        a_, c_ = cc_[k], cc_[(k + 1) % nv_]; L_ = float(np.linalg.norm(c_ - a_))
        if L_ < 3.0: continue
        t_ = (c_ - a_) / L_; n_ = np.array([t_[1], -t_[0]]); mid = (a_ + c_) / 2
        if E['osm'] == '312933183' and ME and float(n_ @ np.array(ME['n'])) > 0.9: continue   # Morehead west front: no gutters in the photo
        if not any(np.hypot(*(np.array(cm) - mid)) < 90 and float((np.array(cm) - mid) @ n_) > 0 for cm in _gcams): continue
        oa, oc = E['out'][k], E['out'][(k + 1) % nv_]; za, zc = E['zf'][k], E['zf'][(k + 1) % nv_]
        # half-round gutter (r 7.5 cm) hung on the fascia just under the tile noses
        base = len(GV)
        for (o_, z_) in ((oa, za), (oc, zc)):
            for j in range(9):
                th = math.pi + math.pi * j / 8; ww_ = 0.085 + 0.075 * math.cos(th)
                GV.append((o_[0] + n_[0] * ww_, o_[1] + n_[1] * ww_, z_ - 0.035 + 0.075 * math.sin(th)))
        GF.extend([(base + j, base + j + 1, base + 10 + j, base + 9 + j) for j in range(8)])
        GF.append(tuple(range(base, base + 9))); GF.append(tuple(range(base + 17, base + 8, -1)))   # 3g: end caps
        ss = [0.5, L_ - 0.5] + ([L_ / 2] if L_ > 24 and E['osm'] != '1188721159' else [])   # CCOM: corners only (mid-wall bays/glazing)
        for s0 in ss:
            # 3g: search +-2 m (0.2 m steps, nearest first) for a spot on a pier (no window column); none -> no downspout (never over glass)
            _cand = [s0 + d_ for d_ in sorted(np.arange(-2.0, 2.01, 0.2), key=abs) if 0.3 <= s0 + d_ <= L_ - 0.3]
            s1 = next((c_ for c_ in _cand if _win_shift(a_ + t_ * c_) == 0.0), None)
            if s1 is None: continue
            q = a_ + t_ * s1; zf_ = za + (zc - za) * s1 / L_; og = oa + (oc - oa) * s1 / L_ + n_ * 0.085; gz_ = _tz(*q)
            T3 = Vector((t_[0], t_[1], 0)); N3 = Vector((n_[0], n_[1], 0)); Q3 = Vector((q[0], q[1], 0))
            P1 = Vector((og[0], og[1], zf_ - 0.08)); P2 = Vector((og[0], og[1], zf_ - 0.58)); P3 = Q3 + N3 * 0.07 + Vector((0, 0, zf_ - 1.1))
            P4 = Q3 + N3 * 0.07 + Vector((0, 0, gz_ + 0.32)); P5 = Q3 + N3 * 0.34 + Vector((0, 0, gz_ + 0.1))
            _segbox(DV, DF, P1 + Vector((0, 0, -0.02)), P1 + Vector((0, 0, -0.09)), T3, 0.1, 0.125)   # 3g: outlet drop collar under the gutter
            boot = E['osm'] == '1188721159'   # CCOM: downspouts run into cast-iron boots and a drain grate (storm line); others: kick-out shoe + splash block
            for A_, B_ in (((P1, P2), (P2, P3), (P3, P4)) if boot else ((P1, P2), (P2, P3), (P3, P4), (P4, P5))): _segbox(DV, DF, A_, B_, T3, 0.075, 0.1)
            if boot:
                _segbox(KV, KF, Q3 + N3 * 0.075 + Vector((0, 0, gz_ - 0.05)), Q3 + N3 * 0.075 + Vector((0, 0, gz_ + 0.5)), T3, 0.13, 0.15)
                _segbox(KV, KF, Q3 + N3 * 0.075 + Vector((0, 0, gz_ + 0.5)), Q3 + N3 * 0.075 + Vector((0, 0, gz_ + 0.56)), T3, 0.15, 0.17)
                _segbox(BV, BF, Q3 + N3 * 0.3 + Vector((0, 0, gz_ - 0.03)), Q3 + N3 * 0.3 + Vector((0, 0, gz_ + 0.03)), T3, 0.62, 0.5)   # 3h: concrete collar round the boot
                _segbox(BRV, BRF, Q3 + N3 * 0.42 + Vector((0, 0, gz_ + 0.03)), Q3 + N3 * 0.42 + Vector((0, 0, gz_ + 0.05)), T3, 0.11, 0.11)   # brass cleanout plug
                _segbox(BRV, BRF, Q3 + N3 * 0.42 + Vector((0, 0, gz_ + 0.05)), Q3 + N3 * 0.42 + Vector((0, 0, gz_ + 0.062)), T3, 0.035, 0.035)  # square drive nut
                gc_ = Q3 + N3 * 1.05   # storm grate on the leader line, 1 m out, in its own concrete frame
                _segbox(BV, BF, gc_ + Vector((0, 0, gz_ - 0.03)), gc_ + Vector((0, 0, gz_ + 0.025)), T3, 0.56, 0.56)
                _segbox(KV, KF, gc_ + Vector((0, 0, gz_ + 0.0)), gc_ + Vector((0, 0, gz_ + 0.03)), T3, 0.4, 0.4)
                _segbox(KV, KF, gc_ + Vector((0, 0, gz_ + 0.0)), gc_ + Vector((0, 0, gz_ + 0.012)), T3, 0.36, 0.36)
                for bi in range(-3, 4):
                    _segbox(KV, KF, gc_ + T3 * (bi * 0.045) + Vector((0, 0, gz_ + 0.02)), gc_ + T3 * (bi * 0.045) + Vector((0, 0, gz_ + 0.033)), N3, 0.34, 0.018)
                ndsp += 1; continue
            for zz in np.arange(gz_ + 1.2, zf_ - 1.3, 2.2):   # straps
                _segbox(DV, DF, Q3 + N3 * 0.07 + Vector((0, 0, zz)), Q3 + N3 * 0.07 + Vector((0, 0, zz + 0.035)), T3, 0.095, 0.12)
            _segbox(BV, BF, Q3 + N3 * 0.3 + Vector((0, 0, gz_ + 0.015)), Q3 + N3 * 0.92 + Vector((0, 0, gz_ + 0.015)), T3, 0.3, 0.06); ndsp += 1
if GF: mesh_obj('Gutters half-round (3f, Life/CCOM UNVERIFIED)', GV, GF, c_d2, m_gut)
if DF: mesh_obj('Downspouts (3f)', DV, DF, c_d2, m_gut)
if BF: mesh_obj('Downspout splash blocks (3f)', BV, BF, c_d2, m_splash)
if KF: mesh_obj('Downspout boots + drain grates (3g, CCOM)', KV, KF, c_d2, rgb('Cast_iron_boot_grate', (0.035, 0.033, 0.03), 0.55, 0.7))
if BRF: mesh_obj('Downspout cleanout plugs brass (3h, CCOM)', BRV, BRF, c_d2, rgb('Cleanout_brass_weathered', (0.32, 0.22, 0.09), 0.45, 0.85))
# 3g: dirt / moss streaks on the stucco just under the eaves (alpha strip 0.9 m tall, 1 cm proud of the wall, above the window heads)
m_str = bpy.data.materials.new('Eave_drip_streaks'); m_str.use_nodes = True; SN = m_str.node_tree.nodes; SL = m_str.node_tree.links; spb = SN['Principled BSDF']
spb.inputs['Base Color'].default_value = (0.07, 0.075, 0.055, 1); spb.inputs['Roughness'].default_value = 0.9
_suv = SN.new('ShaderNodeUVMap'); _ssp = SN.new('ShaderNodeSeparateXYZ'); SL.new(_suv.outputs['UV'], _ssp.inputs[0])
def _sm(op, a, c=None):
    n_ = SN.new('ShaderNodeMath'); n_.operation = op
    for i_, v_ in enumerate((a, c)):
        if v_ is None: continue
        if isinstance(v_, (int, float)): n_.inputs[i_].default_value = v_
        else: SL.new(v_, n_.inputs[i_])
    return n_.outputs[0]
_sat = SN.new('ShaderNodeAttribute'); _sat.attribute_name = 'skv'   # 3h: per-building (u offset, intensity, length scale)
_sats = SN.new('ShaderNodeSeparateColor'); SL.new(_sat.outputs['Color'], _sats.inputs[0])
_su = _sm('ADD', _ssp.outputs['X'], _sm('MULTIPLY', _sats.outputs[0], 100.0)); _sv = _sm('DIVIDE', _ssp.outputs['Y'], _sm('MAXIMUM', _sats.outputs[2], 0.3))
_scx = SN.new('ShaderNodeCombineXYZ'); SL.new(_sm('MULTIPLY', _su, 2.3), _scx.inputs[0])
_sn1 = SN.new('ShaderNodeTexNoise'); _sn1.inputs['Scale'].default_value = 1.0; _sn1.inputs['Detail'].default_value = 4; SL.new(_scx.outputs[0], _sn1.inputs['Vector'])
_scx2 = SN.new('ShaderNodeCombineXYZ'); SL.new(_sm('MULTIPLY', _su, 0.31), _scx2.inputs[0])
_scx3 = SN.new('ShaderNodeCombineXYZ'); SL.new(_sm('MULTIPLY', _su, 0.06), _scx3.inputs[0]); SL.new(_sats.outputs[1], _scx3.inputs[1])
_sn3 = SN.new('ShaderNodeTexNoise'); _sn3.inputs['Scale'].default_value = 1.0; SL.new(_scx3.outputs[0], _sn3.inputs['Vector'])   # bays that stay clean vs dirty runs
_sn2 = SN.new('ShaderNodeTexNoise'); _sn2.inputs['Scale'].default_value = 1.0; SL.new(_scx2.outputs[0], _sn2.inputs['Vector'])
_streak = _sm('MULTIPLY', _sm('SUBTRACT', _sn1.outputs['Fac'], 0.47), 4.0)                                  # per-column drips
_len = _sm('ADD', _sm('MULTIPLY', _sn2.outputs['Fac'], 1.2), -0.25)                                           # drip length varies along the wall
_fade = _sm('SUBTRACT', 1.0, _sm('DIVIDE', _sv, _sm('MAXIMUM', _len, 0.05)))
_alpha = _sm('MINIMUM', _sm('MAXIMUM', _sm('ADD', _sm('MULTIPLY', _sm('MAXIMUM', _streak, 0.0), _sm('MAXIMUM', _fade, 0.0)), _sm('MULTIPLY', _sm('POWER', _sm('SUBTRACT', 1.0, _ssp.outputs['Y']), 6.0), 0.22)), 0.0), 0.55)
_alpha = _sm('MULTIPLY', _alpha, _sm('MULTIPLY', _sats.outputs[1], _sm('MULTIPLY', _sm('MAXIMUM', _sm('SUBTRACT', _sn3.outputs['Fac'], 0.3), 0.0), 3.0)))
SL.new(_alpha, spb.inputs['Alpha'])
SVs, SFs, SUs, SKs = [], [], [], []
for E in EAVES:
    if E['osm'] not in ('312933183', '313021866', '1188721159', '312932811', '315085717'): continue
    _wi = np.nonzero(WB == [x for x in M['buildings'] if x['osm_id'] == E['osm']][0]['bid'])[0]; _WQ = WV[_wi]; _WU = WU[_wi]
    _plg = _shp.Polygon(E['cc']); _rs = random.Random(int(E['osm']) % 9973); _skv = (_rs.random(), _rs.uniform(0.55, 1.25), _rs.uniform(0.6, 1.4), 1.0)
    for j in range(len(_wi)):
        q = _WQ[j]; zt = float(q[:, 2].max()); a2, c2 = q[0, :2], q[1, :2]; ln = float(np.linalg.norm(c2 - a2))
        if ln < 0.2: continue
        tq = (c2 - a2) / ln; nq = np.array([tq[1], -tq[0]]); mq = (a2 + c2) / 2
        if _plg.contains(_shp.Point(*(mq + nq * 0.3))): nq = -nq
        if E['osm'] == '312933183' and ME and abs(float((mq - np.array(ME['center'])) @ np.array(ME['t']))) < 3.1 and float(nq @ np.array(ME['n'])) > 0.9: continue   # not on the pavilion
        b0 = len(SVs); u0_, u1_ = float(_WU[j, 0, 0]), float(_WU[j, 1, 0])
        for (pp, uu) in ((a2, u0_), (c2, u1_)):
            for zz, vv in ((zt - 0.02, 0.0), (zt - 0.92, 1.0)):
                SVs.append((pp[0] + nq[0] * 0.012, pp[1] + nq[1] * 0.012, zz)); SUs.append((uu, vv * 0.9))
        SFs.append((b0, b0 + 1, b0 + 3, b0 + 2)); SKs.append(_skv)
if SFs:
    _so = mesh_obj('Eave drip / moss streaks on stucco (3g)', SVs, SFs, c_d2, m_str)
    _so.data.uv_layers.new(name='UVMap').data.foreach_set('uv', np.array([SUs[i] for f in SFs for i in f], np.float32).ravel())
    _so.data.color_attributes.new('skv', 'FLOAT_COLOR', 'FACE').data.foreach_set('color', np.array(SKs, np.float32).ravel())
print('streak quads', len(SFs))
print('gutters faces', len(GF), 'downspouts', ndsp)

# ---------- day 3: library assets (linked from /workspace/nj-scenes/assets/campus_assets.blend; library untouched)
import sys
sys.path.append('/workspace/nj-scenes/assets/scripts'); sys.path.append('/workspace/nj-scenes/blender_pylib'); import use_assets as ua
SD = json.load(open(f'{ROOT}/data/scene_data.json'))
from shapely.geometry import Polygon as _Poly, LineString as _LS, Point as _Pt
from shapely.ops import unary_union as _uu
_foot = _uu([_Poly(f['pts']).buffer(0) for f in SD['features'] if 'building' in f['tags'] and f['closed'] and len(f['pts']) >= 4])
_roads = _uu([_LS(f['pts']).buffer(4.5) for f in SD['features'] if f['tags'].get('highway') in ('service', 'residential', 'tertiary', 'secondary', 'primary', 'unclassified')])
def gz(x, y):
    hit, loc, *_ = ter.ray_cast(Vector((x, y, 400)), Vector((0, 0, -1)), distance=600)
    return loc.z if hit else 135.0
hero = [tuple(bpy.data.objects[c].location[:2]) for c in ('CAM_eye_west_walk', 'CAM_ref_Morehead_west_photo', 'CAM_closeup_Morehead_entrance', 'CAM_eye_south_Morehead') if c in bpy.data.objects]
# trees: species mix, LiDAR height, LOD0 only near hero cameras and only for 3 species (memory)
LOD0_OK = set(__import__('os').environ.get('LOD0_SPECIES', '').split(',')) - {''}
names = ua.tree_names(); pick = {}
for sp in ua.CAMPUS_MIX:
    for lod in (0, 1):
        cand = sorted(n for n in names if n.startswith(f'Tree_{sp}_LOD{lod}_'))
        if cand: pick[(sp, lod)] = cand[0]
need = sorted({v for (sp, lod), v in pick.items() if sp in __import__('os').environ.get('TREE_SPECIES', 'RedMaple,SugarMaple,PinOak,LondonPlane').split(',') and (lod == 1 or sp in LOD0_OK)})
objs = ua.link(need)
# October tree v2 (assets/campus_trees_v2.blend, build_trees_v2.py): smaller/more alpha-cut leaf cards, edge twigs, 'bare' partial leaf fall
TV2 = '/workspace/nj-scenes/assets/campus_trees_v2.blend'
if os.environ.get('TREES_V2', '1') != '0' and os.path.exists(TV2):
    with bpy.data.libraries.load(TV2, link=True) as (src_, dst_):
        dst_.objects = [n for n in src_.objects if n.endswith('_LOD1_v2Oct')]
    for o_ in dst_.objects:
        if o_ is None: continue
        sp_ = o_.name.split('_')[1]; pick[(sp_, 1)] = o_.name; objs[o_.name] = o_
    print('trees v2 linked', [o_.name for o_ in dst_.objects if o_])
_rb = random.Random(5)
BARE_P = {'RedMaple': 0.35, 'SugarMaple': 0.25, 'LondonPlane': 0.15, 'PinOak': 0.05}   # share of trees already thinning on Oct 8 (red maples drop first, pin oaks hold)
c_trees = coll('Trees_assets_LiDAR')
rnd = random.Random(11)
_SPS = __import__('os').environ.get('TREE_SPECIES', 'RedMaple,SugarMaple,PinOak,LondonPlane').split(',')  # 4 species = memory budget
sps = [s for s in ua.CAMPUS_MIX if s in _SPS]; wts = [ua.CAMPUS_MIX[s][0] for s in sps]
def pick_species(h):  # match species to LiDAR height: tall crowns -> oak/plane, small -> red maple
    w = [wt * (2.5 if (h > 16 and s in ('PinOak', 'LondonPlane')) or (h < 9 and s == 'RedMaple') else 1.0) for s, wt in zip(sps, wts)]
    return rnd.choices(sps, w)[0]
n0 = n1 = 0
for x, y, z, h in T:
    if h < 4.0: continue
    x, y = float(x), float(y)
    if _foot.contains(_Pt(x, y)): continue
    sp = pick_species(float(h))
    near = min(math.hypot(x - a, y - b_) for a, b_ in hero) < 55 if hero else False
    lod = 0 if (near and sp in LOD0_OK) else 1
    src = objs.get(pick.get((sp, lod)))
    if src is None: continue
    o = bpy.data.objects.new(f'T_{sp}_L{lod}_{n0+n1:04d}', src.data)
    s_ = float(h) / max(src.dimensions.z, 1.0) * rnd.uniform(0.97, 1.03)
    o.location = (x, y, float(z) - 0.15); o.scale = (s_ * rnd.uniform(0.9, 1.1), s_ * rnd.uniform(0.9, 1.1), s_)
    o.rotation_euler.z = rnd.uniform(0, math.tau); lo, hi = ua.CAMPUS_MIX[sp][1]; o['autumn'] = 0.55 * rnd.uniform(lo, hi)  # Oct 8: early colour in north Jersey (peak is late Oct)
    o['bare'] = _rb.uniform(0.25, 0.55) if _rb.random() < BARE_P.get(sp, 0.1) else _rb.uniform(0.0, 0.08)   # own RNG: species/placement unchanged
    c_trees.objects.link(o)
    if lod == 0: n0 += 1
    else: n1 += 1
print('asset trees LOD0', n0, 'LOD1', n1)
# site furniture
fur = ua.link(['Lamp_Post_Acorn_Period', 'Bench_Campus_WoodSlat', 'BikeRack_InvertedU_x3', 'TrashCan_Slatted_Steel'])
c_f = coll('Site_furniture')
_cshadow_V, _cshadow_F = [], []
def place(src_name, x, y, rotz, name, contact=False, contact_r=0.55):
    src = fur[src_name]; o = bpy.data.objects.new(name, src.data)
    # 3h: flush — sit the lowest mesh point on the DTM (asset origins sit above the feet on some props)
    z0 = gz(x, y)
    try:
        bb = [src.matrix_world @ Vector(c) for c in src.bound_box] if src.bound_box else None
        # linked asset: use data bound_box in object space (origin at feet for lamps; benches may have origin mid-seat)
        zs = [c[2] for c in src.bound_box] if src.bound_box else [0.0]
        z_off = -min(zs)   # lift so the lowest vertex sits at z0
    except Exception:
        z_off = 0.0
    o.location = (x, y, z0 + z_off); o.rotation_euler.z = rotz
    c_f.objects.link(o)
    if contact:   # soft elliptical contact darkening under furniture (AO-like, cheap mesh)
        nseg = 10; b0 = len(_cshadow_V)
        _cshadow_V.append((x, y, z0 + 0.004))
        for i in range(nseg):
            a = 2 * math.pi * i / nseg
            rx = contact_r * (1.6 if 'Bench' in name else 0.7); ry = contact_r * (0.55 if 'Bench' in name else 0.7)
            _cshadow_V.append((x + rx * math.cos(a) * math.cos(rotz) - ry * math.sin(a) * math.sin(rotz),
                               y + rx * math.cos(a) * math.sin(rotz) + ry * math.sin(a) * math.cos(rotz), z0 + 0.004))
        for i in range(nseg):
            _cshadow_F.append((b0, b0 + 1 + i, b0 + 1 + ((i + 1) % nseg)))
    return o
nl = 0; nb_walk = 0; placed_pts = []
for f in SD['features']:
    if f['tags'].get('highway') not in ('footway', 'pedestrian', 'path') or f['tags'].get('footway') == 'crossing': continue
    ls = _LS(f['pts'])
    if ls.length < 15 or ls.distance(_Pt(0, 0)) > 140: continue
    side = _LS(f['pts']).offset_curve(1.9)
    if side.is_empty or side.geom_type != 'LineString': continue
    d_ = 6.0
    while d_ < side.length - 3:
        p = side.interpolate(d_); d_ += 24.0
        if abs(p.x) > 200 or abs(p.y) > 200: continue
        if _foot.buffer(1.5).contains(p) or _roads.contains(p) or any(math.hypot(p.x - a, p.y - b_) < 14 for a, b_ in placed_pts): continue
        place('Lamp_Post_Acorn_Period', p.x, p.y, 0.0, f'Lamp_acorn_{nl:03d}'); placed_pts.append((p.x, p.y)); nl += 1
        if nl % 3 == 1:  # benches along the main walks, on the lawn edge beside a lamp (as in the Sprague Library reference photo)
            p2 = side.interpolate(min(d_ - 24.0 + 0.5, side.length)); p1 = side.interpolate(d_ - 24.0 - 0.5); tl = math.hypot(p2.x - p1.x, p2.y - p1.y) or 1.0
            tx_, ty_ = (p2.x - p1.x) / tl, (p2.y - p1.y) / tl; bx, by = p.x - ty_ * 1.0 + tx_ * 3.5, p.y + tx_ * 1.0 + ty_ * 3.5
            if not (_foot.buffer(1.5).contains(_Pt(bx, by)) or _roads.contains(_Pt(bx, by))):
                place('Bench_Campus_WoodSlat', bx, by, math.atan2(ty_, tx_), f'Bench_walk_{nl:03d}', contact=True, contact_r=0.65); nb_walk += 1
print('lamps', nl, 'walk benches', nb_walk, 'flattened roof verts', nflat)
# 3h: concrete control joints (~1.5 m) + expansion joints (~6 m) as thin recessed groove meshes on OSM walks near heroes
def _paving_joints():
  _JV, _JF = [], []
  _hz = [bpy.data.objects[c].location.xy.copy() for c in ('CAM_eye_west_walk', 'CAM_ref_Morehead_west_photo', 'CAM_closeup_Morehead_entrance', 'CAM_walk_west') if c in bpy.data.objects]
  # walk camera not yet created — use eye_west + Morehead cams + a corridor box
  _hz = [bpy.data.objects[c].location.xy.copy() for c in ('CAM_eye_west_walk', 'CAM_ref_Morehead_west_photo', 'CAM_closeup_Morehead_entrance', 'CAM_eye_south_Morehead', 'CAM_eye_Life_front') if c in bpy.data.objects]
  _zonej = _uu([_Pt(a, b_).buffer(90) for a, b_ in _hz]) if _hz else _Pt(0, 0).buffer(120)
  for f in SD['features']:
      if f['tags'].get('highway') not in ('footway', 'path', 'pedestrian') or f['tags'].get('footway') == 'crossing': continue
      if len(f['pts']) < 2: continue
      ls = _LS(f['pts'])
      if ls.length < 8 or ls.distance(_Pt(0, 0)) > 160: continue
      seg = ls.intersection(_zonej)
      for g in getattr(seg, 'geoms', [seg]):
          if g.geom_type != 'LineString' or g.length < 4: continue
          # sample centreline; emit cross-walk control grooves every 1.5 m and long expansion grooves every 6 m
          n = int(g.length / 1.5)
          for i in range(1, n):
              p = g.interpolate(i * 1.5); q = g.interpolate(min(i * 1.5 + 0.25, g.length))
              tx, ty = q.x - p.x, q.y - p.y; tl = math.hypot(tx, ty) or 1.0; tx, ty = tx / tl, ty / tl
              nx, ny = ty, -tx
              # groove width across walk ~2.8 m, depth 8 mm, thickness 2.5 cm
              half = 1.4; _jw = 0.008 if (i % 4) else 0.015; z0 = gz(p.x, p.y) + 0.068   # paving sits at DTM+6 cm
              a = (p.x - nx * half, p.y - ny * half, z0); b = (p.x + nx * half, p.y + ny * half, z0)
              a2 = (a[0] + tx * _jw, a[1] + ty * _jw, z0); b2 = (b[0] + tx * _jw, b[1] + ty * _jw, z0)
              # drop the groove 8 mm so it reads as a sawcut
              a_ = (a[0], a[1], z0 - 0.008); b_ = (b[0], b[1], z0 - 0.008); a2_ = (a2[0], a2[1], z0 - 0.008); b2_ = (b2[0], b2[1], z0 - 0.008)
              k = len(_JV); _JV += [a, b, b2, a2, a_, b_, b2_, a2_]
              _JF += [(k, k+1, k+2, k+3), (k+4, k+7, k+6, k+5), (k, k+3, k+7, k+4), (k+1, k+5, k+6, k+2), (k, k+4, k+5, k+1), (k+3, k+2, k+6, k+7)]
  if _JF:
      m_j = rgb('Paving_joint_groove', (0.17, 0.165, 0.15), 0.9)
      mesh_obj('Footpath control + expansion joints (3h)', _JV, _JF, c_path, m_j)
      print('paving joint boxes', len(_JF) // 6)
_paving_joints()

_PW = {'footway': 3.0, 'path': 2.5, 'pedestrian': 6.0}
_pav = _uu([(_Poly(f['pts']).buffer(0) if f['closed'] and ('area:highway' in f['tags'] or f['tags'].get('area') == 'yes') else _LS(f['pts']).buffer(_PW[f['tags']['highway']] / 2, cap_style='flat'))
            for f in SD['features'] if f['tags'].get('highway') in _PW or (f['closed'] and 'area:highway' in f['tags'])]).buffer(-0.7)
_pav0 = _pav.buffer(0.5)  # _pav was shrunk 0.7 m; this is the paving shrunk 0.2 m
_footb = _foot.buffer(1.0); _shp.prepare(_pav0); _shp.prepare(_footb); _shp.prepare(_roads)
# worn lawn edge: a 0.6 m strip draped along the paving outline near the hero cameras, alpha fading outward (trampled, thinner grass)
def worn_edges(R=60.0, w=0.9, step=0.5):
    from shapely.geometry.polygon import orient as _orient
    hz = [bpy.data.objects[c].location for c in ('CAM_eye_west_walk', 'CAM_ref_Morehead_west_photo') if c in bpy.data.objects]
    area = _uu([_Pt(h.x, h.y).buffer(R) for h in hz]); pv = _pav.buffer(0.7).intersection(area)
    block = _uu([_foot.buffer(0.8), _roads]); _shp.prepare(block)
    V, F, UV = [], [], []
    for pg in getattr(pv, 'geoms', [pv]):
        if pg.geom_type != 'Polygon' or pg.area < 2: continue
        pg = _orient(pg, 1.0)
        for ring in [pg.exterior] + list(pg.interiors):
            L_ = ring.length; n = int(L_ / step)
            if n < 3: continue
            prev = None
            for i in range(n + 1):
                a = ring.interpolate(min(i * step, L_)); c_ = ring.interpolate(min(i * step + 0.2, L_)) if i * step + 0.2 <= L_ else ring.interpolate(i * step - 0.2)
                tx, ty = c_.x - a.x, c_.y - a.y; tl = math.hypot(tx, ty) or 1.0; tx, ty = tx / tl, ty / tl
                if i * step + 0.2 > L_: tx, ty = -tx, -ty
                nx, ny = ty, -tx                                    # right of travel = outside the paving
                ox, oy = a.x + nx * w, a.y + ny * w
                ok = area.contains(_Pt(a.x, a.y)) and not _shp.contains_xy(block, ox, oy) and not _pav0.contains(_Pt(ox, oy))
                if not ok: prev = None; continue
                k = len(V); V += [(a.x + nx * 0.03, a.y + ny * 0.03, gz(a.x, a.y) + 0.012), (ox, oy, gz(ox, oy) + 0.012)]
                if prev is not None: F.append((prev, k, k + 1, prev + 1))
                prev = k
    if not F: print('worn edges: none'); return
    mw = bpy.data.materials.new('Lawn_worn_edge'); mw.use_nodes = True; N_ = mw.node_tree.nodes; L2 = mw.node_tree.links; pb = N_['Principled BSDF']
    pb.inputs['Base Color'].default_value = (0.20, 0.155, 0.07, 1); pb.inputs['Roughness'].default_value = 0.95
    tc = N_.new('ShaderNodeTexCoord'); sx = N_.new('ShaderNodeSeparateXYZ'); L2.new(tc.outputs['UV'], sx.inputs[0])
    inv = N_.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; L2.new(sx.outputs['Y'], inv.inputs[1])
    pw_ = N_.new('ShaderNodeMath'); pw_.operation = 'POWER'; pw_.inputs[1].default_value = 1.6; L2.new(inv.outputs[0], pw_.inputs[0])
    nz_ = N_.new('ShaderNodeTexNoise'); nz_.inputs['Scale'].default_value = 1.2; nz_.inputs['Detail'].default_value = 4; L2.new(tc.outputs['Object'], nz_.inputs['Vector'])
    mr = N_.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.35; mr.inputs['From Max'].default_value = 0.65; mr.inputs['To Min'].default_value = 0.25; mr.inputs['To Max'].default_value = 0.85
    L2.new(nz_.outputs['Fac'], mr.inputs['Value'])
    mul = N_.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; L2.new(pw_.outputs[0], mul.inputs[0]); L2.new(mr.outputs[0], mul.inputs[1])
    L2.new(mul.outputs[0], pb.inputs['Alpha'])
    o = mesh_obj('Lawn_worn_edge_along_walks', V, F, c_f, mw)
    uvl = o.data.uv_layers.new(name='UVMap'); uvs = []
    for poly_ in o.data.polygons:
        for li in poly_.loop_indices:
            vi_ = o.data.loops[li].vertex_index; uvs += [0.0, float(vi_ % 2)]
    uvl.data.foreach_set('uv', uvs)
    print('worn edge faces', len(F))
def paved_spot(x, y, rot, R=16.0):
    # nearest spot to (x, y) where the whole 3-loop rack (1.85 x 0.85 m + margin, along rot or across it) sits on OSM paving, off roads, off walls
    gx_, gy_ = np.meshgrid(np.arange(-R, R + 0.01, 0.5), np.arange(-R, R + 0.01, 0.5)); px, py = x + gx_.ravel(), y + gy_.ravel()
    best = None
    for rr in (rot, rot + math.pi / 2):
        ca, sa = math.cos(rr), math.sin(rr); ok = np.ones(len(px), bool)
        for du, dw in ((-1.0, -0.5), (1.0, -0.5), (1.0, 0.5), (-1.0, 0.5), (0, 0)):
            qx, qy = px + du * ca - dw * sa, py + du * sa + dw * ca
            ok &= _shp.contains_xy(_pav0, qx, qy) & ~_shp.contains_xy(_footb, qx, qy) & ~_shp.contains_xy(_roads, qx, qy)
        if ok.any():
            d_ = np.hypot(px - x, py - y) + (~ok) * 1e9; k = int(np.argmin(d_))
            if best is None or d_[k] < best[0]: best = (d_[k], float(px[k]), float(py[k]), rr)
    if best is None: print('paved_spot: none near', x, y); return x, y, rot
    print('paved_spot moved', round(best[0], 1), 'm'); return best[1], best[2], best[3]
def entrance_frame(osm_id, west=True):
    f = [f for f in SD['features'] if f['id'] == osm_id][0]
    poly = _Poly(f['pts']).buffer(0).simplify(0.3); cc = list(poly.exterior.coords); sg = 1 if poly.exterior.is_ccw else -1; best = None
    for a, b_ in zip(cc[:-1], cc[1:]):
        ex, ey = b_[0]-a[0], b_[1]-a[1]; L_ = math.hypot(ex, ey); tx, ty = ex/L_, ey/L_; nx_, ny_ = ty*sg, -tx*sg
        if nx_ < -0.7 and (best is None or L_ > best[0]): best = (L_, ((a[0]+b_[0])/2, (a[1]+b_[1])/2), (tx, ty), (nx_, ny_))
    return best
PADS = []
for oid, tag in (('312933183', 'Morehead'), ('1188721159', 'CCOM')):
    L_, (mx, my), (tx, ty), (nx_, ny_) = entrance_frame(oid)
    rot = math.atan2(ty, tx)
    place('Bench_Campus_WoodSlat', mx + nx_*9.0 + tx*7.0, my + ny_*9.0 + ty*7.0, rot + math.pi, f'Bench_{tag}_entrance', contact=True, contact_r=0.7)
    place('TrashCan_Slatted_Steel', mx + nx_*9.0 + tx*8.6, my + ny_*9.0 + ty*8.6, rot, f'TrashCan_{tag}_entrance', contact=True, contact_r=0.45)
    _bx, _by, _br = paved_spot(mx + nx_*8.0 - tx*7.5, my + ny_*8.0 - ty*7.5, rot)
    # concrete pad beside the walk (racks do not sit in the walkway): pick the side off the paving, away from walls and roads
    _px, _py = -math.sin(_br), math.cos(_br)
    for _sg in (1, -1):
        _cx, _cy = _bx + _sg*_px*2.3, _by + _sg*_py*2.3
        _pt = _Pt(_cx, _cy)
        if not (_pav.contains(_pt) or _foot.buffer(1.5).contains(_pt) or _roads.buffer(1.0).contains(_pt)):
            _bx, _by = _cx, _cy; break
    _zp = gz(_bx, _by)
    # pad drapes on the terrain (grid sampled with gz) 1.5 cm proud, with a short skirt into the ground: flush with the lawn, no slab edge
    _ca, _sa = math.cos(_br), math.sin(_br); _nu, _nw = 9, 6; PV, PF = [], []
    for j in range(_nw):
        for i in range(_nu):
            u_, w_ = -1.7 + 3.4 * i / (_nu - 1), -1.1 + 2.2 * j / (_nw - 1); x_, y_ = _bx + u_ * _ca - w_ * _sa, _by + u_ * _sa + w_ * _ca
            PV.append((x_, y_, gz(x_, y_) + 0.015))
    PF = [(j*_nu+i, j*_nu+i+1, (j+1)*_nu+i+1, (j+1)*_nu+i) for j in range(_nw-1) for i in range(_nu-1)]
    ring = [j*0+i for i in range(_nu)] + [(j)*_nu+_nu-1 for j in range(1, _nw)] + [(_nw-1)*_nu+i for i in range(_nu-2, -1, -1)] + [j*_nu for j in range(_nw-2, 0, -1)]
    n0_ = len(PV); PV += [(PV[k][0], PV[k][1], PV[k][2] - 0.2) for k in ring]
    PF += [(ring[k], ring[(k+1) % len(ring)], n0_ + (k+1) % len(ring), n0_ + k) for k in range(len(ring))]
    mesh_obj(f'BikePad_{tag}_concrete', PV, PF, c_f, m_conc)
    PADS.append(_shp.Polygon([(_bx + u_ * _ca - w_ * _sa, _by + u_ * _sa + w_ * _ca) for u_, w_ in ((-1.75, -1.15), (1.75, -1.15), (1.75, 1.15), (-1.75, 1.15))]))
    place('BikeRack_InvertedU_x3', _bx, _by, _br - math.pi / 2,  # rack mesh is long along local Y
          f'BikeRack_{tag}_entrance')
    # 3h: assert rack sits on its concrete pad (not the lawn)
    _pad_poly = PADS[-1]
    print(f'bike rack {tag} on pad', _pad_poly.contains(_Pt(_bx, _by)), 'at', round(_bx, 2), round(_by, 2))
if _cshadow_F:
    m_cs = bpy.data.materials.new('Furniture_contact_shadow'); m_cs.use_nodes = True; m_cs.blend_method = 'BLEND'
    _csn = m_cs.node_tree.nodes; _csl = m_cs.node_tree.links; _csp = _csn['Principled BSDF']
    _csp.inputs['Base Color'].default_value = (0.06, 0.045, 0.03, 1); _csp.inputs['Roughness'].default_value = 1.0   # trampled soil / shade
    _csp.inputs['Alpha'].default_value = 0.35
    # radial fade via generated coords (center dark → rim transparent): approximate with object-space distance from mesh origin per-instance is hard; use soft AO
    _csao = _csn.new('ShaderNodeAmbientOcclusion'); _csao.inputs['Distance'].default_value = 0.25
    _csa = _csn.new('ShaderNodeMath'); _csa.operation = 'MULTIPLY'; _csa.inputs[1].default_value = 0.45
    _csl.new(_csao.outputs['AO'], _csa.inputs[0]);  # unused AO; keep flat alpha
    _csp.inputs['Alpha'].default_value = 0.55
    mesh_obj('Furniture contact darkening (3h)', _cshadow_V, _cshadow_F, c_f, m_cs)
try:
    worn_edges()
except Exception as ex:
    print('worn edges failed', ex)
# curbs: library CurbSweep (granite block) along asphalt road edges near the hero cameras (OSM road widths as in prep_geom)
_WID = {'service': 5.5, 'residential': 8.0, 'tertiary': 10.0, 'secondary': 11.0, 'primary': 12.0, 'unclassified': 7.0, 'living_street': 6.0}
_rp = []
for f in SD['features']:
    t_ = f['tags']; hw = t_.get('highway')
    if hw not in _WID or f['closed'] or t_.get('service') in ('parking_aisle', 'drive-through'): continue
    w_ = _WID[hw]
    try: w_ = float(t_.get('width', '').split()[0])
    except Exception: pass
    _rp.append(_LS(f['pts']).buffer(w_ / 2, cap_style='flat', join_style='round', quad_segs=3))
_zone = _uu([_Pt(a, b_).buffer(110) for a, b_ in hero])
_edges = _uu(_rp).boundary.intersection(_zone).difference(_foot.buffer(1.5))
_cg = ua.link(['Curb_Granite_Block']).get('Curb_Granite_Block')
c_curb = coll('Curbs_granite')
_lines = [g for g in getattr(_edges, 'geoms', [_edges]) if g.geom_type == 'LineString' and g.length > 3]
cu = bpy.data.curves.new('Curb_edges_OSM', 'CURVE'); cu.dimensions = '3D'; ncurb = 0.0
for g in _lines:
    n_ = max(2, int(g.length / 1.5) + 1); pts = [g.interpolate(i / (n_ - 1), normalized=True) for i in range(n_)]
    sp_ = cu.splines.new('POLY'); sp_.points.add(n_ - 1)
    for p_, q in zip(sp_.points, pts): p_.co = (q.x, q.y, gz(q.x, q.y) + 0.02, 1.0)
    ncurb += g.length
co_ = bpy.data.objects.new('Curbs_granite_OSM', cu); c_curb.objects.link(co_)
if _cg and _cg.modifiers:
    m_src = _cg.modifiers[0]; m_ = co_.modifiers.new('CurbSweep', 'NODES'); m_.node_group = m_src.node_group
    for k in ('Socket_2', 'Socket_3', 'Socket_4', 'Socket_5', 'Socket_6'):
        try: m_[k] = m_src[k]
        except Exception as ex: print('curb input', k, ex)
    _cg.hide_render = True; _cg.hide_viewport = True
print('curbs m', round(ncurb), 'splines', len(cu.splines))
# eye-level lawn: appended (local) copy of the library lawn on a terrain overlay, faded out with view distance and limited to green ortho areas
with bpy.data.libraries.load(ua.LIB, link=False) as (src, dst):
    dst.materials = ['Lawn_Varied_Oct']
lawn = dst.materials[0]; lawn.name = 'Lawn_Varied_Oct_local_fade'
for n_ in lawn.node_tree.nodes:
    if n_.type == 'TEX_IMAGE' and n_.image and n_.image.filepath.startswith('//textures'):
        n_.image.filepath = '/workspace/nj-scenes/assets/' + n_.image.filepath[2:]
LN = lawn.node_tree.nodes; LL = lawn.node_tree.links
LN['Map Range.002'].inputs['From Min'].default_value = 0.66; LN['Map Range.002'].inputs['To Max'].default_value = 0.4; LN['Noise Texture.001'].inputs['Scale'].default_value = 1.1  # smaller, fainter leaf-litter patches (early Oct)
lout = LN['Material Output']; lbs = LN['Principled BSDF']
# mowing stripes (alternating 1.8 m passes) + large colour patches (~15 m) so the lawn is not one uniform green
_lc = [l.from_socket for l in lbs.inputs['Base Color'].links][0]
_tc2 = LN.new('ShaderNodeTexCoord'); _sx = LN.new('ShaderNodeSeparateXYZ'); LL.new(_tc2.outputs['Object'], _sx.inputs[0])
def _lm(op, a, c=None):
    n_ = LN.new('ShaderNodeMath'); n_.operation = op
    for i_, v_ in enumerate((a, c)):
        if v_ is None: continue
        if isinstance(v_, (int, float)): n_.inputs[i_].default_value = v_
        else: LL.new(v_, n_.inputs[i_])
    return n_.outputs[0]
_u = _lm('ADD', _lm('MULTIPLY', _sx.outputs['X'], math.cos(math.radians(113))), _lm('MULTIPLY', _sx.outputs['Y'], math.sin(math.radians(113))))   # passes run ~WSW-ENE, parallel to the CCOM walk
_stripe = _lm('MULTIPLY', _lm('SINE', _lm('MULTIPLY', _u, math.pi / 1.8)), 0.13)          # +-13 % value (1.8 m mower passes)
_nzp = LN.new('ShaderNodeTexNoise'); _nzp.inputs['Scale'].default_value = 0.07; _nzp.inputs['Detail'].default_value = 3
LL.new(_tc2.outputs['Object'], _nzp.inputs['Vector'])
_patch = _lm('MULTIPLY', _lm('SUBTRACT', _nzp.outputs['Fac'], 0.5), 0.35)                  # +-~9 % value
_gain = _lm('ADD', _lm('ADD', _stripe, _patch), 1.0)
_hsv = LN.new('ShaderNodeHueSaturation'); LL.new(_lc, _hsv.inputs['Color']); LL.new(_gain, _hsv.inputs['Value'])
_hue = _lm('ADD', _lm('MULTIPLY', _lm('SUBTRACT', _nzp.outputs['Fac'], 0.5), 0.05), 0.5)  # slight yellow/blue-green drift in the patches
LL.new(_hue, _hsv.inputs['Hue'])
LL.new(_hsv.outputs['Color'], lbs.inputs['Base Color'])
camd = LN.new('ShaderNodeCameraData'); fade = LN.new('ShaderNodeMapRange'); fade.inputs[1].default_value = 30; fade.inputs[2].default_value = 95
fade.inputs[3].default_value = 1.0; fade.inputs[4].default_value = 0.0
LL.new(camd.outputs['View Distance'], fade.inputs[0])
oimg = LN.new('ShaderNodeTexImage'); oimg.image = bpy.data.images.load(f'{ROOT}/data/ortho2020.png', check_existing=True)
ouv = LN.new('ShaderNodeUVMap'); ouv.uv_map = 'ortho'; LL.new(ouv.outputs['UV'], oimg.inputs['Vector'])
osep = LN.new('ShaderNodeSeparateColor'); LL.new(oimg.outputs['Color'], osep.inputs[0])
omx = LN.new('ShaderNodeMath'); omx.operation = 'MAXIMUM'; LL.new(osep.outputs[0], omx.inputs[0]); LL.new(osep.outputs[2], omx.inputs[1])
og = LN.new('ShaderNodeMath'); og.operation = 'SUBTRACT'; LL.new(osep.outputs[1], og.inputs[0]); LL.new(omx.outputs[0], og.inputs[1])
ogr = LN.new('ShaderNodeMapRange'); ogr.inputs[1].default_value = -0.07; ogr.inputs[2].default_value = -0.02;  # lenient: paths are separate meshes, ortho path smears should not show LL.new(og.outputs[0], ogr.inputs[0])
fm = LN.new('ShaderNodeMath'); fm.operation = 'MULTIPLY'; LL.new(fade.outputs[0], fm.inputs[0]); LL.new(ogr.outputs[0], fm.inputs[1])
# outside the fade (far / non-green) the slot shows the plain ortho; no separate overlay mesh (memory)
# 3h: cheap distant mown-lawn (clump / colour breakup + normal) so far lawn is not flat ortho paint
obs = LN.new('ShaderNodeBsdfPrincipled'); obs.inputs['Roughness'].default_value = 0.92
_dtc = LN.new('ShaderNodeTexCoord'); _dsx = LN.new('ShaderNodeSeparateXYZ'); LL.new(_dtc.outputs['Object'], _dsx.inputs[0])
_du = _lm('ADD', _lm('MULTIPLY', _dsx.outputs['X'], math.cos(math.radians(113))), _lm('MULTIPLY', _dsx.outputs['Y'], math.sin(math.radians(113))))
_dstripe = _lm('MULTIPLY', _lm('SINE', _lm('MULTIPLY', _du, math.pi / 1.8)), 0.10)
_dn1 = LN.new('ShaderNodeTexNoise'); _dn1.inputs['Scale'].default_value = 0.09; _dn1.inputs['Detail'].default_value = 4; LL.new(_dtc.outputs['Object'], _dn1.inputs['Vector'])
_dn2 = LN.new('ShaderNodeTexNoise'); _dn2.inputs['Scale'].default_value = 0.55; _dn2.inputs['Detail'].default_value = 3; LL.new(_dtc.outputs['Object'], _dn2.inputs['Vector'])
_dclump = _lm('ADD', _lm('MULTIPLY', _lm('SUBTRACT', _dn1.outputs['Fac'], 0.5), 0.28), _lm('MULTIPLY', _lm('SUBTRACT', _dn2.outputs['Fac'], 0.5), 0.12))
_dgain = _lm('ADD', _lm('ADD', _dstripe, _dclump), 1.0)
_dhsv = LN.new('ShaderNodeHueSaturation'); LL.new(oimg.outputs['Color'], _dhsv.inputs['Color']); LL.new(_dgain, _dhsv.inputs['Value'])
_dhue = _lm('ADD', _lm('MULTIPLY', _lm('SUBTRACT', _dn1.outputs['Fac'], 0.5), 0.04), 0.5)
LL.new(_dhue, _dhsv.inputs['Hue']); LL.new(_dhsv.outputs['Color'], obs.inputs['Base Color'])
# procedural normal breakup (clumps read at distance without a texture)
_dbump = LN.new('ShaderNodeBump'); _dbump.inputs['Strength'].default_value = 0.35; _dbump.inputs['Distance'].default_value = 0.08
LL.new(_dn2.outputs['Fac'], _dbump.inputs['Height']); LL.new(_dbump.outputs['Normal'], obs.inputs['Normal'])
mixs = LN.new('ShaderNodeMixShader')
LL.new(fm.outputs[0], mixs.inputs[0]); LL.new(obs.outputs[0], mixs.inputs[1]); LL.new(lbs.outputs[0], mixs.inputs[2])
LL.new(mixs.outputs[0], lout.inputs['Surface'])
ter.data.materials.append(lawn)
_pc = np.zeros(len(ter.data.polygons) * 3, np.float32); ter.data.polygons.foreach_get('center', _pc); _pc = _pc.reshape(-1, 3)
_dm = np.min([np.hypot(_pc[:, 0] - a, _pc[:, 1] - b_) for a, b_ in hero], axis=0)
_mi = (_dm < 105).astype(np.int32); ter.data.polygons.foreach_set('material_index', _mi)
print('lawn terrain faces', int(_mi.sum()))
# terrain LOD (memory): keep the 1 m DTM within 140 m of the hero cameras, collapse-decimate the rest (seen only from the aerial)
_vc = np.zeros(len(ter.data.vertices) * 3, np.float32); ter.data.vertices.foreach_get('co', _vc); _vc = _vc.reshape(-1, 3)
_vd = np.min([np.hypot(_vc[:, 0] - a, _vc[:, 1] - b_) for a, b_ in hero], axis=0)
vg = ter.vertex_groups.new(name='far'); _far_i = np.nonzero(_vd > 140)[0].tolist(); vg.add(_far_i, 1.0, 'REPLACE')
dm = ter.modifiers.new('LOD', 'DECIMATE'); dm.decimate_type = 'COLLAPSE'; dm.ratio = float(os.environ.get('TER_RATIO', '0.25')); dm.vertex_group = 'far'; dm.vertex_group_factor = 1000.0
_dg = bpy.context.evaluated_depsgraph_get(); _nm = bpy.data.meshes.new_from_object(ter.evaluated_get(_dg))
_old = ter.data; ter.modifiers.remove(dm); ter.data = _nm; _nm.name = 'terrain'; bpy.data.meshes.remove(_old); ter.vertex_groups.clear()
_pc = np.zeros(len(_nm.polygons) * 3, np.float32); _nm.polygons.foreach_get('center', _pc); _pc = _pc.reshape(-1, 3)
print('terrain faces after LOD', len(_nm.polygons), 'near', int((np.min([np.hypot(_pc[:, 0] - a, _pc[:, 1] - b_) for a, b_ in hero], axis=0) < 105).sum()))
for o in list(bpy.data.collections['Tree_prototypes'].objects) if 'Tree_prototypes' in bpy.data.collections else []: o.hide_render = True
# ---------- 3g/3h: walk camera along the west OSM footway past CCOM to Morehead pavilion fill (1.65 m eye, ease, step bob)
from shapely.ops import linemerge as _lmg
_fwl = [_LS(f['pts']) for f in SD['features'] if f['tags'].get('highway') in ('footway', 'path', 'pedestrian') and f['tags'].get('footway') != 'crossing' and len(f['pts']) > 1]
# 3h: OSM splits the west walk into short segments; node with unary_union, Dijkstra S -> pavilion approach
_mh_xy = _Pt(ME['center'][0], ME['center'][1]) if ME else _Pt(mor[0], mor[1])
_A = _Pt(ME['center'][0] + ME['n'][0] * 10, ME['center'][1] + ME['n'][1] * 10) if ME else _mh_xy  # ~10 m west of pavilion
# 3i: walk v2 ended under PinOak_0299's crown (real tree on lawn at (-44.5,-29.5), ortho crown ~(-40,-25)). Route on past it to the
# walk point south of the crown, ~9 m oblique to the pavilion. Override with WALK_END=x,y
_A = _Pt(*[float(v) for v in os.environ.get('WALK_END', '-44.2,-45.0').split(',')])
_S = _Pt(-29.0, 14.0)
_fw_noded = list(getattr(_uu(_fwl), 'geoms', [_uu(_fwl)]))
_nodes = []; _nxy = []
def _nid(p, tol=0.6):
    for i, (x, y) in enumerate(_nxy):
        if (x - p.x) ** 2 + (y - p.y) ** 2 < tol * tol: return i
    _nxy.append((p.x, p.y)); _nodes.append(p); return len(_nodes) - 1
_edges = []
for g in _fw_noded:
    if g.geom_type != 'LineString' or g.length < 1.0: continue
    u, v = _nid(_Pt(*g.coords[0])), _nid(_Pt(*g.coords[-1]))
    _edges.append((u, v, g.length, g)); _edges.append((v, u, g.length, _LS(list(g.coords)[::-1])))
import heapq as _hq
_si = min(range(len(_nodes)), key=lambda i: _nodes[i].distance(_S))
_ai = min(range(len(_nodes)), key=lambda i: _nodes[i].distance(_A))
_adj = {}
for u, v, L, g in _edges: _adj.setdefault(u, []).append((v, L, g))
_dist = {_si: 0.0}; _prev = {}; _pq = [(0.0, _si)]
while _pq:
    d, u = _hq.heappop(_pq)
    if d != _dist.get(u): continue
    if u == _ai: break
    for v, L, g in _adj.get(u, []):
        nd = d + L
        if nd < _dist.get(v, 1e18): _dist[v] = nd; _prev[v] = (u, g); _hq.heappush(_pq, (nd, v))
_chain = []
if _ai in _prev:
    cur = _ai
    while cur != _si:
        u, g = _prev[cur]; _chain.append(g); cur = u
    _chain.reverse()
    WALK = _LS([c for g in _chain for c in list(g.coords)[:-1]] + list(_chain[-1].coords))
else:
    _mw = _lmg(_uu(_fwl)); _mw = list(getattr(_mw, 'geoms', [_mw]))
    WALK = min(_mw, key=lambda g: g.distance(_Pt(-33.0, 0.0)))
print('walk chain segs', len(_chain), 'len', round(WALK.length, 1), 'Sdist', round(WALK.distance(_S), 2), 'Adist', round(WALK.distance(_A), 2))
_s0 = WALK.project(_S); _sgn = 1.0 if WALK.interpolate(min(WALK.length, _s0 + 1.0)).y < WALK.interpolate(_s0).y else -1.0
# walk until ~14 m from pavilion centre so a 24 mm lens fills the entrance without clipping into the porch
_s_end = _s0; _best = None
for _k in range(1, int(WALK.length) + 1):
    _ss = _s0 + _sgn * _k; _pp = WALK.interpolate(max(0.0, min(WALK.length, _ss)))
    _d = _pp.distance(_mh_xy)
    if _d <= float(os.environ.get('WALK_STOP', '0.0')): _s_end = _ss; break   # ~13 m: pavilion fills frame without tree mush at the porch
    _best = (_ss, _d)
else:
    _s_end = _best[0] if _best else (_s0 + _sgn * min(40.0, WALK.length * 0.6))
_s_end = _s0 + _sgn * abs(WALK.project(_A) - _s0)   # 3i: stop at the projection of the end point on the walk
WALK_LEN = float(os.environ.get('WALK_M', str(abs(_s_end - _s0))))
# preview budget: cap default frames at 480 (~20 s); full-rate ~1.35 m/s available via WALK_FRAMES=
WALK_MOVE = int(os.environ.get('WALK_FRAMES', str(max(240, int(round(WALK_LEN / 1.55 * 24))))))   # 1.45 m/s walking pace
WALK_HOLD = 24   # 1 s hold on the pavilion at the end
WALK_N = WALK_MOVE + WALK_HOLD
sc.render.fps = 24; sc.frame_start = 1; sc.frame_end = WALK_N
_wd = bpy.data.cameras.new('CAM_walk_west'); _wd.lens = 24; _wd.clip_end = 3000; _wc = bpy.data.objects.new('CAM_walk_west', _wd); sc.collection.objects.link(_wc)
_ccom_t = Vector((scm[0] - 22.0, scm[1] - 2.0, scm[2] + 6.5))
_mh_t = Vector((ME['center'][0] + ME['n'][0] * 0.5, ME['center'][1] + ME['n'][1] * 0.5, ME['ground'] + 4.6)) if ME else Vector((mor[0], mor[1], mor[2] + 5))
WALK_PTS = []
for fr in range(1, WALK_N + 1):
    t = min(1.0, (fr - 1) / max(WALK_MOVE - 1, 1)); e = t * t * (3 - 2 * t)          # smoothstep ease in/out, then hold
    sd_ = _s0 + _sgn * WALK_LEN * e; pp = WALK.interpolate(sd_); pa = WALK.interpolate(sd_ + _sgn * 1.0)
    off = Vector((pa.x - pp.x, pa.y - pp.y)).normalized(); side = Vector((off.y, -off.x))   # walk 0.5 m right of the centreline
    x_, y_ = pp.x + side.x * 0.3, pp.y + side.y * 0.3   # slightly right of the centreline
    spd = 6 * t * (1 - t); bob = 0.008 * spd * 1.5 * math.sin(2 * math.pi * 1.8 * (fr - 1) / 24.0)
    loc = Vector((x_, y_, _tz(x_, y_) + 1.65 + bob)); WALK_PTS.append((x_, y_))
    # late path: look more at the pavilion (fills frame); early: mostly ahead past CCOM
    look_ahead = Vector((off.x, off.y, 0)) * 12 + loc + Vector((0, 0, -0.5))
    pav_look = _mh_t
    look_w = min(1.0, max(0.0, (e - 0.55) / 0.40)); look_w = look_w * look_w * (3 - 2 * look_w)
    tgt = look_ahead.lerp(pav_look, 0.10 + 0.90 * look_w)   # 3i: end looking fully at the pavilion (oblique)   # keep corridor framing; pavilion grows in the end of the walk
    _wc.location = loc; _wc.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
    _wc.keyframe_insert('location', frame=fr); _wc.keyframe_insert('rotation_euler', frame=fr)
for fc in _wc.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
print('walk camera', [round(v, 1) for v in WALK_PTS[0]], '->', [round(v, 1) for v in WALK_PTS[-1]], 'len', WALK_LEN)
# 3h: campus trees over walks are limbed up (~3 m clearance). Trees whose crown overhangs the walk-camera path get a local
# copy of their LOD1 mesh with leaf/twig faces below 3.0 m (world, above the trunk base) removed; trunk / bark faces kept.
import bmesh as _bm
_wl = _LS(WALK_PTS); _limb_cache = {}; _nlimb = 0
for o in list(c_trees.objects):
    h_ = o.dimensions.z
    d_ = _wl.distance(_Pt(o.location.x, o.location.y))
    # also limb any tree within 12 m of the last 15 m of the walk (pavilion approach)
    _tail = _LS(WALK_PTS[max(0, len(WALK_PTS)//2):])
    near_end = _tail.distance(_Pt(o.location.x, o.location.y)) < 12.0
    if d_ > 0.45 * h_ + 1.0 and not near_end: continue
    sz = o.scale.z or 1.0; thr = (float(os.environ.get('LIMB_END', '6.0')) if near_end else 3.0) / sz; rx_ = 0.8 / (o.scale.x or 1.0)
    key = (o.data.name, round(thr, 1))
    if key not in _limb_cache:
        me2 = o.data.copy(); me2.name = o.data.name + f'_limbed{key[1]}'
        bm_ = _bm.new(); bm_.from_mesh(me2)
        bark = {i for i, m in enumerate(me2.materials) if m and ('bark' in m.name.lower() or 'trunk' in m.name.lower())}
        kill = [f for f in bm_.faces if max(v.co.z for v in f.verts) < thr and (f.material_index not in bark or f.calc_center_median().xy.length > rx_)]   # 3i: + low bark limbs off the trunk axis
        _bm.ops.delete(bm_, geom=kill, context='FACES'); bm_.to_mesh(me2); bm_.free(); _limb_cache[key] = me2
        print('limbed', key, 'removed', len(kill))
    o.data = _limb_cache[key]; _nlimb += 1
print('trees limbed over walk', _nlimb)
# ---------- 3f: eye-level grass (particle hair, limited radius around the eye-level cameras, density falls off with distance)
GR = float(os.environ.get('GRASS_R', '26')); GN = int(os.environ.get('GRASS_N', '100000'))
_gc = [(bpy.data.objects[c].location.copy(), r_) for c, r_ in (('CAM_eye_west_walk', GR), ('CAM_closeup_Morehead_entrance', 1e-3), ('CAM_ref_Morehead_west_photo', 1e-3)) if c in bpy.data.objects]
c_gr = coll('Lawn_grass_leaves_3f')
if GN > 0 and _gc:
    _fz = [_shp.Polygon([_cshadow_V[i][:2] for i in range(b + 1, b + 11)]).buffer(-0.08) for b in range(0, len(_cshadow_V), 11)]
    _blk = _uu([_foot.buffer(1.8), _roads, _pav.buffer(0.75)] + [pd.buffer(0.1) for pd in PADS] + _fz); _shp.prepare(_blk); st_ = 0.5   # 3h: + bike pads + worn patches under benches / bins
    # 3g: corridor along the main walk (y -65..+65) + the eye_west view; density from the distance to where a walking / standing camera is
    _cor = _uu([g.intersection(_shp.box(-75, -70, 10, 90)) for g in _fwl]); GRW = float(os.environ.get('GRASS_W', '14'))   # walks between Morehead, CCOM and toward Life
    mnx, mny, mxx, mxy = _cor.buffer(GRW).union(_Pt(_gc[0][0].x, _gc[0][0].y).buffer(GR)).bounds
    xs_ = np.arange(mnx, mxx + 0.01, st_); ys_ = np.arange(mny, mxy + 0.01, st_)
    GX, GY = np.meshgrid(xs_, ys_, indexing='ij')
    # density from the camera distance: the eye_west camera point (radius GR) and the walk lines (a walkthrough camera passes along them, radius GRW)
    _gp = _shp.points(GX.ravel(), GY.ravel())
    dn_ = np.minimum(_shp.distance(_cor, _gp) / GRW, _shp.distance(_Pt(_gc[0][0].x, _gc[0][0].y), _gp) / GR).reshape(GX.shape)
    ok_ = (dn_ <= 1.0) & ~_shp.contains_xy(_blk, GX, GY)
    vid = -np.ones(GX.shape, np.int64); vid[ok_] = np.arange(int(ok_.sum()))
    Vg = [(float(x), float(y), _tz(float(x), float(y)) + 0.004) for x, y in zip(GX[ok_], GY[ok_])]
    Wg = np.clip(1.12 - 1.1 * dn_[ok_], 0.03, 1.0) ** 2.0   # dense near the camera / walk, thinning quadratically to ~0 at the edge
    _gx, _gy = GX[ok_], GY[ok_]   # clumping: smooth pseudo-noise (sum of rotated sines, ~1-3 m) -> tufts and thinner patches
    _cl = sum(np.sin(_gx * math.cos(a_) * f_ + _gy * math.sin(a_) * f_ + p_) for a_, f_, p_ in ((0.3, 2.1, 0.0), (1.4, 3.3, 1.7), (2.5, 4.6, 0.6), (0.9, 6.9, 2.9))) / 4.0
    Wg = Wg * np.clip(0.7 + 0.6 * _cl, 0.25, 1.0)
    a_, b_, c2, d_ = vid[:-1, :-1], vid[1:, :-1], vid[1:, 1:], vid[:-1, 1:]; fm_ = (a_ >= 0) & (b_ >= 0) & (c2 >= 0) & (d_ >= 0)
    Fg = np.c_[a_[fm_], b_[fm_], c2[fm_], d_[fm_]].tolist()
    gme = bpy.data.meshes.new('grass_patch'); gme.from_pydata(Vg, [], Fg); gpo = bpy.data.objects.new('Lawn_grass_hair_eye_level (3f)', gme); c_gr.objects.link(gpo)
    vgp = gpo.vertex_groups.new(name='dens')
    for w_ in np.unique(np.round(Wg, 2)): vgp.add(np.nonzero(np.round(Wg, 2) == w_)[0].tolist(), float(w_), 'REPLACE')
    m_gh = bpy.data.materials.new('Grass_blades_hair'); m_gh.use_nodes = True; GNt = m_gh.node_tree; _gb = GNt.nodes['Principled BSDF']
    _hi_ = GNt.nodes.new('ShaderNodeHairInfo'); _cr = GNt.nodes.new('ShaderNodeValToRGB')
    _cr.color_ramp.elements[0].color = (0.05, 0.095, 0.02, 1); _cr.color_ramp.elements[1].color = (0.15, 0.2, 0.055, 1)
    _mx = GNt.nodes.new('ShaderNodeMath'); _mx.operation = 'MULTIPLY_ADD'; _mx.inputs[1].default_value = 0.55
    GNt.links.new(_hi_.outputs['Intercept'], _mx.inputs[0]); GNt.links.new(_hi_.outputs['Random'], _mx.inputs[2])
    _mx2 = GNt.nodes.new('ShaderNodeMath'); _mx2.operation = 'MULTIPLY'; _mx2.inputs[1].default_value = 0.7; GNt.links.new(_mx.outputs[0], _mx2.inputs[0])
    GNt.links.new(_mx2.outputs[0], _cr.inputs['Fac']); GNt.links.new(_cr.outputs['Color'], _gb.inputs['Base Color'])
    _gb.inputs['Roughness'].default_value = 0.55; _gb.inputs['Subsurface Weight'].default_value = 0.0
    gme.materials.append(m_gh)
    pm_ = gpo.modifiers.new('grass', 'PARTICLE_SYSTEM'); ps_ = gpo.particle_systems[0]; pst = ps_.settings
    pst.type = 'HAIR'; pst.use_advanced_hair = True; pst.count = GN; pst.hair_length = 0.075; pst.emit_from = 'FACE'; pst.distribution = 'RAND'; pst.use_even_distribution = True
    pst.normal_factor = 0.075; pst.factor_random = 0.028; pst.hair_step = 2; pst.display_step = 1; pst.render_step = 1
    pst.root_radius = 1.0; pst.tip_radius = 0.1; pst.radius_scale = 0.0035; pst.material = 1; pst.child_type = 'NONE'
    ps_.vertex_group_density = 'dens'; ps_.seed = 7; gpo.show_instancer_for_render = False
    if os.environ.get('GRASS_TEX'):   # 3g: (off) cloud texture clumping - thinned the lawn too much at this count
        _ctx = bpy.data.textures.new('grass_clumps', 'CLOUDS'); _ctx.noise_scale = 0.18; _ctx.noise_depth = 2
        _cts = pst.texture_slots.add(); _cts.texture = _ctx; _cts.texture_coords = 'GLOBAL'
        _cts.use_map_time = False; _cts.use_map_density = True; _cts.density_factor = 0.45; _cts.use_map_length = True; _cts.length_factor = 0.6
        print('grass clumping texture on')
    sc.cycles_curves.shape = 'RIBBONS'
    print('grass patch verts', len(Vg), 'faces', len(Fg), 'hairs', GN)
    if os.environ.get('GRASS_MODE', 'inst') == 'inst':
        # 3g: instanced grass - 6 blade tiles (0.54 m, 90-420 blades as real tapered, bent blades) instanced per 0.5 m cell by geometry nodes.
        # Cycles stores each tile once, so memory is ~instances x 100 B instead of ~500 B per hair; the hair patch above is removed.
        bpy.data.objects.remove(gpo, do_unlink=True); bpy.data.meshes.remove(gme)
        _tc = bpy.data.collections.new('grass_tiles_3g')   # not linked to the scene: only instanced
        m_gt = bpy.data.materials.new('Grass_blades_mesh'); m_gt.use_nodes = True; _ga = m_gt.node_tree.nodes.new('ShaderNodeAttribute'); _ga.attribute_name = 'gcol'
        _gpb = m_gt.node_tree.nodes['Principled BSDF']; m_gt.node_tree.links.new(_ga.outputs['Color'], _gpb.inputs['Base Color']); _gpb.inputs['Roughness'].default_value = 0.55
        for ti, (nb, sd0) in enumerate(((420, 1), (420, 2), (220, 3), (220, 4), (90, 5), (90, 6))):
            r = random.Random(100 + sd0); V_, F_, C_ = [], [], []
            for i in range(nb):
                x0, y0 = r.uniform(-0.27, 0.27), r.uniform(-0.27, 0.27); h = r.uniform(0.045, 0.1) * (1.6 if r.random() < 0.06 else 1.0); wb_ = r.uniform(0.0015, 0.0026)
                a0 = r.uniform(0, math.tau); bl = r.uniform(0, math.tau); ln = r.uniform(0.08, 0.5)
                sv = Vector((math.cos(a0), math.sin(a0), 0)) * wb_; ld = Vector((math.cos(bl), math.sin(bl), 0))
                p0 = Vector((x0, y0, -0.01)); pm = p0 + Vector((0, 0, h * 0.55)) + ld * (h * 0.25 * math.sin(ln)); pt = p0 + Vector((0, 0, h * math.cos(ln))) + ld * (h * math.sin(ln))
                k = len(V_); V_ += [tuple(p0 - sv), tuple(p0 + sv), tuple(pm + sv * 0.7), tuple(pm - sv * 0.7), tuple(pt)]; F_ += [(k, k + 1, k + 2, k + 3), (k + 3, k + 2, k + 4)]
                g = r.uniform(0.8, 1.2); y_ = r.uniform(0.0, 1.0)
                cb = (0.04 * g, 0.075 * g, 0.018 * g, 1); ct = ((0.12 + 0.06 * y_) * g, (0.17 + 0.03 * y_) * g, (0.045 + 0.01 * y_) * g, 1)
                cm = tuple((cb[j] + ct[j]) / 2 for j in range(4)); C_ += [cb, cb, cm, cm, ct]
            tme = bpy.data.meshes.new(f'gt_{ti}'); tme.from_pydata(V_, [], F_); tme.color_attributes.new('gcol', 'FLOAT_COLOR', 'POINT').data.foreach_set('color', np.array(C_, np.float32).ravel())
            tme.materials.append(m_gt); _tc.objects.link(bpy.data.objects.new(f'gt_{ti}', tme))
        _rg = random.Random(9); PV, PT, PR = [], [], []
        for (x_, y_, z_), w_ in zip(Vg, Wg):
            lv_ = w_ + _rg.uniform(-0.08, 0.08)
            if lv_ >= 0.5: t_ = 0
            elif lv_ >= 0.22: t_ = 2
            elif lv_ >= 0.05 or _rg.random() < lv_ * 12: t_ = 4
            else: continue
            PV.append((x_ + _rg.uniform(-0.06, 0.06), y_ + _rg.uniform(-0.06, 0.06), z_)); PT.append(t_ + _rg.randrange(2)); PR.append(_rg.uniform(0, math.tau))
        pme = bpy.data.meshes.new('grass_points'); pme.from_pydata(PV, [], [])
        pme.attributes.new('tile', 'INT', 'POINT').data.foreach_set('value', PT); pme.attributes.new('rot', 'FLOAT', 'POINT').data.foreach_set('value', PR)
        ng = bpy.data.node_groups.new('GrassInstances3g', 'GeometryNodeTree')
        ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
        NN = ng.nodes; NL = ng.links; gi = NN.new('NodeGroupInput'); go = NN.new('NodeGroupOutput')
        m2p = NN.new('GeometryNodeMeshToPoints'); iop = NN.new('GeometryNodeInstanceOnPoints'); iop.inputs['Pick Instance'].default_value = True
        ci = NN.new('GeometryNodeCollectionInfo'); ci.inputs['Collection'].default_value = _tc; ci.inputs['Separate Children'].default_value = True; ci.inputs['Reset Children'].default_value = True
        nat = NN.new('GeometryNodeInputNamedAttribute'); nat.data_type = 'INT'; nat.inputs['Name'].default_value = 'tile'
        nar = NN.new('GeometryNodeInputNamedAttribute'); nar.data_type = 'FLOAT'; nar.inputs['Name'].default_value = 'rot'
        cxz = NN.new('ShaderNodeCombineXYZ'); NL.new(nar.outputs['Attribute'], cxz.inputs['Z'])
        NL.new(gi.outputs[0], m2p.inputs['Mesh']); NL.new(m2p.outputs['Points'], iop.inputs['Points']); NL.new(ci.outputs['Instances'], iop.inputs['Instance'])
        NL.new(nat.outputs['Attribute'], iop.inputs['Instance Index']); NL.new(cxz.outputs['Vector'], iop.inputs['Rotation']); NL.new(iop.outputs['Instances'], go.inputs[0])
        gpo = bpy.data.objects.new('Lawn_grass_instanced (3g)', pme); c_gr.objects.link(gpo); gm_ = gpo.modifiers.new('grass', 'NODES'); gm_.node_group = ng
        print('grass instanced cells', len(PV), 'tiles', np.bincount(np.array(PT) // 2).tolist())
    # 3g: weeds + unmown tufts along the walk edges (lawn side, 5-35 cm off the paving), only within 18 m of the walk camera path / eye_west camera
    _rw = random.Random(31); WV_, WF_, WC_ = [], [], []
    _pe = _pav.buffer(0.7); _wk = _uu([_LS(WALK_PTS), _Pt(_gc[0][0].x, _gc[0][0].y)])
    def _blade(x0, y0, z0, ang, tilt, L, w, col):
        d = Vector((math.cos(ang) * math.sin(tilt), math.sin(ang) * math.sin(tilt), math.cos(tilt))); sv = Vector((-math.sin(ang), math.cos(ang), 0)) * w
        p0 = Vector((x0, y0, z0)); b = len(WV_); WV_.extend([tuple(p0 - sv), tuple(p0 + sv), tuple(p0 + d * L)]); WF_.append((b, b + 1, b + 2)); WC_.append(col)
    for pg in getattr(_pe, 'geoms', [_pe]):
        if pg.geom_type != 'Polygon': continue
        for ring in [pg.exterior] + list(pg.interiors):
            dl = 0.0
            while dl < ring.length:
                dl += _rw.uniform(0.3, 1.1); p_ = ring.interpolate(dl); q_ = ring.interpolate(dl + 0.2)
                if _wk.distance(_Pt(p_.x, p_.y)) > 18: continue
                tv = Vector((q_.x - p_.x, q_.y - p_.y)); tv = tv.normalized() if tv.length > 1e-6 else Vector((1, 0)); nv_ = Vector((tv.y, -tv.x))
                o_ = _rw.uniform(0.05, 0.35); c_ = Vector((p_.x, p_.y)) + nv_ * o_
                if _shp.contains_xy(_pe, c_.x, c_.y): c_ = Vector((p_.x, p_.y)) - nv_ * o_
                if _shp.contains_xy(_blk, c_.x, c_.y) and not _shp.contains_xy(_pe.buffer(0.4), c_.x, c_.y): continue
                if _shp.contains_xy(_pe, c_.x, c_.y) or _shp.contains_xy(_footb, c_.x, c_.y): continue
                z0 = _tz(c_.x, c_.y) + 0.003; k_ = _rw.random()
                if k_ < 0.4:   # dandelion / plantain rosette: flat lanceolate leaves
                    col = (0.03 * _rw.uniform(0.8, 1.3), 0.065 * _rw.uniform(0.8, 1.2), 0.015, 1.0)
                    for i in range(_rw.randint(5, 8)):
                        a = _rw.uniform(0, math.tau); _blade(c_.x, c_.y, z0, a, _rw.uniform(1.2, 1.45), _rw.uniform(0.07, 0.14), 0.018, col)
                elif k_ < 0.65:   # clover patch: small round-ish leaflets close to the ground
                    col = (0.035, 0.08, 0.02, 1.0)
                    for i in range(_rw.randint(6, 12)):
                        r_ = _rw.uniform(0, 0.12); a = _rw.uniform(0, math.tau); x1, y1 = c_.x + r_ * math.cos(a), c_.y + r_ * math.sin(a)
                        _blade(x1, y1, z0 + 0.03, a, _rw.uniform(1.3, 1.5), 0.022, 0.014, col)
                else:   # unmown tuft at the edge (the mower misses it): taller, splayed, yellower blades
                    col = (0.13 * _rw.uniform(0.8, 1.2), 0.15 * _rw.uniform(0.85, 1.15), 0.05, 1.0)
                    for i in range(_rw.randint(8, 16)):
                        _blade(c_.x + _rw.uniform(-0.03, 0.03), c_.y + _rw.uniform(-0.03, 0.03), z0, _rw.uniform(0, math.tau), _rw.uniform(0.05, 0.5), _rw.uniform(0.1, 0.24), 0.004, col)
    if WF_:
        wme = bpy.data.meshes.new('walk_edge_weeds'); wme.from_pydata(WV_, [], WF_)
        wme.color_attributes.new('wcol', 'FLOAT_COLOR', 'FACE').data.foreach_set('color', np.array(WC_, np.float32).ravel())
        m_wd = bpy.data.materials.new('Weeds_walk_edge'); m_wd.use_nodes = True; _wa = m_wd.node_tree.nodes.new('ShaderNodeAttribute'); _wa.attribute_name = 'wcol'
        m_wd.node_tree.links.new(_wa.outputs['Color'], m_wd.node_tree.nodes['Principled BSDF'].inputs['Base Color']); m_wd.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.6
        wme.materials.append(m_wd); c_gr.objects.link(bpy.data.objects.new('Weeds + unmown tufts at walk edges (3g)', wme))
    print('edge weeds tris', len(WF_))
# fallen leaves under maples near the eye-level cameras (alpha-cut LeafSet024 cells, per-leaf autumn colour; more under the barer crowns)
NLF = int(os.environ.get('LEAVES_N', '24000'))
if NLF > 0 and _gc:
    _lt = [o for o in c_trees.objects if 'Maple' in o.name and min(math.hypot(o.location.x - c.x, o.location.y - c.y) - r for c, r in _gc) < 25]
    _rl = random.Random(23); LV, LF, LUV, LC = [], [], [], []
    wts_ = [max(o.dimensions.z, 4.0) ** 2 * (0.35 + 2.0 * float(o.get('bare', 0))) for o in _lt]; tw_ = sum(wts_) or 1.0
    _palette = [(0.55, 0.06, 0.02), (0.62, 0.18, 0.02), (0.7, 0.36, 0.03), (0.42, 0.2, 0.06), (0.25, 0.12, 0.05), (0.5, 0.45, 0.06)]
    for o, w_ in zip(_lt, wts_):
        rc_ = 0.36 * o.dimensions.z; nl_ = int(NLF * w_ / tw_); red = 'Red' in o.name
        for _ in range(nl_):
            r_ = rc_ * 1.2 * _rl.random() ** 0.6; a_ = _rl.uniform(0, math.tau); x_, y_ = o.location.x + r_ * math.cos(a_), o.location.y + r_ * math.sin(a_)
            if _footb.contains_xy(x_, y_) if hasattr(_footb, 'contains_xy') else _shp.contains_xy(_footb, x_, y_): continue
            onpav = bool(_shp.contains_xy(_pav0, x_, y_))
            if onpav and _rl.random() < 0.45: continue   # 3h: more leaf debris stays on the concrete
            z_ = _tz(x_, y_) + (0.006 if onpav else _rl.uniform(0.02, 0.06))
            hs = _rl.uniform(0.045, 0.07); yaw = _rl.uniform(0, math.tau); tx_, ty_ = _rl.uniform(-0.35, 0.35), _rl.uniform(-0.35, 0.35)
            R_ = Matrix.Rotation(yaw, 3, 'Z') @ Matrix.Rotation(tx_, 3, 'X') @ Matrix.Rotation(ty_, 3, 'Y'); base = len(LV)
            for (u, v) in ((-1, -1), (1, -1), (1, 1), (-1, 1)): LV.append(tuple(Vector((x_, y_, z_)) + R_ @ Vector((u * hs, v * hs, 0))))
            LF.append((base, base + 1, base + 2, base + 3)); ox, oy = _rl.randrange(3) / 3, _rl.randrange(3) / 3
            LUV.extend([(ox, oy), (ox + 1/3, oy), (ox + 1/3, oy + 1/3), (ox, oy + 1/3)])
            c_ = _palette[_rl.choice((0, 0, 1, 1, 2, 3, 4)) if red else _rl.choice((1, 2, 2, 5, 3, 4))]; g_ = _rl.uniform(0.75, 1.15); LC.append((c_[0] * g_, c_[1] * g_, c_[2] * g_, 1.0))
    # a light wind-blown scatter across the eye-level lawn patch (all species colours, ~0.6/m2 near the camera thinning outward)
    if GN > 0 and _gc:
        _c0, _r0 = _gc[0]; nb_ = int(os.environ.get('LEAVES_BLOWN', '2500'))
        for _ in range(nb_ * 3):
            if nb_ <= 0: break
            r_ = _r0 * math.sqrt(_rl.random()); a_ = _rl.uniform(0, math.tau); x_, y_ = _c0.x + r_ * math.cos(a_), _c0.y + r_ * math.sin(a_)
            if _shp.contains_xy(_blk, x_, y_) or _rl.random() < r_ / _r0 * 0.6: continue
            z_ = _tz(x_, y_) + _rl.uniform(0.03, 0.07); hs = _rl.uniform(0.04, 0.065)
            R_ = Matrix.Rotation(_rl.uniform(0, math.tau), 3, 'Z') @ Matrix.Rotation(_rl.uniform(-0.4, 0.4), 3, 'X'); base = len(LV)
            for (u, v) in ((-1, -1), (1, -1), (1, 1), (-1, 1)): LV.append(tuple(Vector((x_, y_, z_)) + R_ @ Vector((u * hs, v * hs, 0))))
            LF.append((base, base + 1, base + 2, base + 3)); ox, oy = _rl.randrange(3) / 3, _rl.randrange(3) / 3
            LUV.extend([(ox, oy), (ox + 1/3, oy), (ox + 1/3, oy + 1/3), (ox, oy + 1/3)])
            c_ = _palette[_rl.randrange(len(_palette))]; g_ = _rl.uniform(0.7, 1.1); LC.append((c_[0] * g_, c_[1] * g_, c_[2] * g_, 1.0)); nb_ -= 1
    if LF:
        lme = bpy.data.meshes.new('fallen_leaves'); lme.from_pydata(LV, [], LF); lme.uv_layers.new(name='UVMap').data.foreach_set('uv', np.array(LUV, np.float32).ravel())
        lme.color_attributes.new('lcol', 'FLOAT_COLOR', 'FACE').data.foreach_set('color', np.array(LC, np.float32).ravel())
        m_fl = bpy.data.materials.new('Fallen_leaves_Oct'); m_fl.use_nodes = True; FN = m_fl.node_tree.nodes; FL = m_fl.node_tree.links; fpb = FN['Principled BSDF']
        _lc = FN.new('ShaderNodeTexImage'); _lc.image = bpy.data.images.load('/workspace/nj-scenes/assets/textures/LeafSet024/LeafSet024_1K-JPG_Color.jpg', check_existing=True)
        _lo = FN.new('ShaderNodeTexImage'); _lo.image = bpy.data.images.load('/workspace/nj-scenes/assets/textures/LeafSet024/LeafSet024_1K-JPG_Opacity.jpg', check_existing=True); _lo.image.colorspace_settings.name = 'Non-Color'
        _bw = FN.new('ShaderNodeRGBToBW'); FL.new(_lc.outputs['Color'], _bw.inputs[0]); _at = FN.new('ShaderNodeAttribute'); _at.attribute_name = 'lcol'
        _mm = FN.new('ShaderNodeMix'); _mm.data_type = 'RGBA'; _mm.blend_type = 'MULTIPLY'; _mm.inputs[0].default_value = 1.0
        _sc3 = FN.new('ShaderNodeMath'); _sc3.operation = 'MULTIPLY'; _sc3.inputs[1].default_value = 3.0; FL.new(_bw.outputs[0], _sc3.inputs[0])
        FL.new(_at.outputs['Color'], _mm.inputs[6]); FL.new(_sc3.outputs[0], _mm.inputs[7]); FL.new(_mm.outputs[2], fpb.inputs['Base Color'])
        FL.new(_lo.outputs['Color'], fpb.inputs['Alpha']); fpb.inputs['Roughness'].default_value = 0.6
        lme.materials.append(m_fl); lo_ = bpy.data.objects.new('Fallen_leaves_under_maples (3f)', lme); c_gr.objects.link(lo_)
    print('fallen leaves', len(LF), 'under', len(_lt), 'maples')
# small life details near the CCOM walk (positions UNVERIFIED): building ID sign (call column removed 2026-10-13: not real)
_ce = bpy.data.objects.get('CAM_eye_west_walk')
if _ce is not None:
    _fw = [_LS(f['pts']) for f in SD['features'] if f['tags'].get('highway') in ('footway', 'path', 'pedestrian') and len(f['pts']) > 1]
    _fwu = _uu(_fw)
    _dir = (Vector((scm[0], scm[1] + 8)) - _ce.location.xy).normalized()
    def _spot(dist, ang, off):
        p_ = _ce.location.xy + Vector(_dir).to_3d().to_2d() * 0 + (Matrix.Rotation(math.radians(ang), 2) @ _dir) * dist
        q_ = _fwu.interpolate(_fwu.project(_Pt(p_.x, p_.y))) if _fwu.geom_type == 'LineString' else min((g.interpolate(g.project(_Pt(p_.x, p_.y))) for g in _fwu.geoms), key=lambda g: g.distance(_Pt(p_.x, p_.y)))
        v_ = Vector((p_.x - q_.x, p_.y - q_.y)); v_ = v_.normalized() if v_.length > 0.1 else Vector((1, 0))
        for o_ in (off, off + 1.0, off + 2.0, -off, -off - 1.0):
            r_ = Vector((q_.x, q_.y)) + v_ * o_
            if not _shp.contains_xy(_blk if GN > 0 else _footb, r_.x, r_.y) and not _footb.contains(_Pt(r_.x, r_.y)): return r_, v_
        return None, v_
    def _cbox(V_, F_, cx, cy, ang, sx, sy, z0, z1):
        _segbox(V_, F_, Vector((cx, cy, z0)), Vector((cx, cy, z1)), Vector((math.cos(ang), math.sin(ang), 0)), sx, sy)
    # REMOVED 2026-10-13: blue-light emergency call column was a guess (UNVERIFIED); Joe confirmed none exists in front of CCOM. Do not re-add without a photo.
    _p, _v = _spot(17.0, 4.0, 2.2)
    if _p is not None:
        gz0 = _tz(_p.x, _p.y); an_ = math.atan2(_v.y, _v.x) + math.pi / 2; Vs_, Fs_, Vq_, Fq_ = [], [], [], []
        for sg in (-0.75, 0.75):
            _cbox(Vq_, Fq_, _p.x + math.cos(an_) * sg, _p.y + math.sin(an_) * sg, an_, 0.1, 0.1, gz0 - 0.1, gz0 + 1.25)
        _cbox(Vs_, Fs_, _p.x, _p.y, an_, 1.7, 0.06, gz0 + 0.5, gz0 + 1.15)
        mesh_obj('Campus sign posts (UNVERIFIED position)', Vq_, Fq_, c_gr, rgb('Sign_post_dark', (0.03, 0.03, 0.03), 0.4, 0.6))
        mesh_obj('Campus building ID sign panel (UNVERIFIED)', Vs_, Fs_, c_gr, rgb('MSU_red_panel', (0.32, 0.012, 0.02), 0.4))['position'] = 'UNVERIFIED'
        for side_ in (1, -1):
            _cu = bpy.data.curves.new('SCMSIGN', 'FONT'); _cu.body = 'SCHOOL OF COMMUNICATION\nAND MEDIA'; _cu.size = 0.085; _cu.extrude = 0.002; _cu.align_x = 'CENTER'; _cu.align_y = 'CENTER'
            _ts = bpy.data.objects.new('Campus sign lettering', _cu); c_gr.objects.link(_ts); _cu.materials.append(rgb('Label_white2', (0.85, 0.85, 0.85), 0.4))
            _nn = Vector((_v.x, _v.y, 0)) * side_
            _ts.matrix_world = Matrix.Translation(Vector((_p.x, _p.y, gz0 + 0.84)) + _nn * 0.032) @ Matrix.Rotation(math.atan2(_nn.y, _nn.x) + math.pi / 2, 4, 'Z') @ Matrix.Rotation(math.pi / 2, 4, 'X')
        print('ID sign at', round(_p.x, 1), round(_p.y, 1))
# sky: Nishita with more haze for lighting; partly cloudy CC0 Poly Haven HDRI seen only by camera rays
sky.dust_density = 3.2; sky.air_density = 1.3
wnt = w.node_tree; WN = wnt.nodes
env = WN.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(f'{ROOT}/hdri/kloofendal_48d_partly_cloudy_puresky_2k.hdr')
# rotate the HDRI so its sun (brightest pixel: az ~124 deg, elev ~48) sits at the scene sun azimuth
_hp = np.array(env.image.pixels[:], np.float32).reshape(env.image.size[1], env.image.size[0], 4)[..., :3].sum(-1)
_hy, _hx = np.unravel_index(_hp.argmax(), _hp.shape); _u = _hx / env.image.size[0]
_dx, _dy = math.cos(-(_u - 0.5) * math.tau), math.sin(-(_u - 0.5) * math.tau); _haz = math.degrees(math.atan2(_dx, _dy)) % 360
tco = WN.new('ShaderNodeTexCoord'); mpw = WN.new('ShaderNodeMapping'); mpw.inputs['Rotation'].default_value[2] = math.radians(az - _haz)
wnt.links.new(tco.outputs['Generated'], mpw.inputs['Vector']); wnt.links.new(mpw.outputs['Vector'], env.inputs['Vector'])
print('HDRI sun az', round(_haz, 1), '-> rotate', round(az - _haz, 1))
bg2 = WN.new('ShaderNodeBackground'); bg2.inputs['Strength'].default_value = 0.55; wnt.links.new(env.outputs['Color'], bg2.inputs['Color'])
lp = WN.new('ShaderNodeLightPath'); mxw = WN.new('ShaderNodeMixShader')
wout = WN['World Output']
wnt.links.new(lp.outputs['Is Camera Ray'], mxw.inputs[0]); wnt.links.new(bg.outputs[0], mxw.inputs[1]); wnt.links.new(bg2.outputs[0], mxw.inputs[2])
wnt.links.new(mxw.outputs[0], wout.inputs['Surface'])
sc['sky_note'] = 'Lighting: Nishita (dust 3.2, air 1.3) + sun. Camera-visible sky: Poly Haven kloofendal_48d_partly_cloudy_puresky (CC0).'
# 4a (2026-10-13): CCOM tower rebuilt as one projecting volume; deletes the day-2 LiDAR prism + its generic windows/lettering and cleans the wing eave/windows around it
exec(open(f'{ROOT}/scripts/ccom_tower.py').read(), {'ROOT': ROOT, '__name__': 'ccom_tower'})   # own namespace (it defines T, G, ...)
exec(open(f'{ROOT}/scripts/ccom_windows.py').read(), {'ROOT': ROOT, '__name__': 'ccom_windows'})   # 2026-10-14: modelled windows replace the CCOM facade-shader windows
bpy.ops.wm.save_as_mainfile(filepath=f'{ROOT}/montclair_state.blend', relative_remap=True, compress=True)
print('SAVED', elev, az, 'trees', len(T), 'cents', scm, mor, life)

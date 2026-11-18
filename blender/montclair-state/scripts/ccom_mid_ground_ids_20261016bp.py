"""2026-10-16 bp: replace the two UNVERIFIED mid-ground proxies in MID_distance_proxies_20261014x
(apartment pair boxes + red/white lattice mast stand-in) with data-identified features:
 - Country Club Towers 1 (12 lv) + 2 (19 lv), 100/140 Hepburn Rd, Clifton: OSM footprints (ODbL), height = levels*3.0+2 m (UNVERIFIED storey height)
 - WPAT-AM four-tower array, 1396 Broad St, Clifton: OSM/GNIS node positions, 108.2 m AGL (FCC ASR 1241949/1241951, 355 ft)
   simple 3-leg lattice (face width 1.5 m UNVERIFIED), FAA 7-band orange/white (UNVERIFIED paint state); no capacity hats modelled.
Ground: 3DEP 30 m DEM (MEASURED) min under footprint / at node. Tones UNVERIFIED. Old proxies hidden (not deleted).
Idempotent: rebuilds collection MID_ids_20261016bp. SAVE=1 saves."""
import bpy, bmesh, json, math, os
from mathutils import Vector
TAG = '20261016bp'; ROOT = '/workspace/nj-scenes/montclair-state'
D = json.load(open(ROOT + '/data/ccom_mid_distance/bp/mid_ground_ids_20261016bp.json'))
def clear_collection(name):
    c = bpy.data.collections.get(name)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o, do_unlink=True)
    else:
        c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c
def node_mat(name, base, rough=0.85):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); bs = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bs.inputs['Base Color'].default_value = base; bs.inputs['Roughness'].default_value = rough
    nt.links.new(bs.outputs[0], out.inputs[0]); m['bp_flag'] = TAG; return m, nt, bs
def facade_mat(name, wall, win, floor_h=3.0, win_frac=0.42, bay=3.2):
    """UNVERIFIED window-grid: horizontal dark window bands per storey + vertical piers every bay (object coords)."""
    m, nt, bs = node_mat(name, wall)
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sep.inputs[0])
    def band(sock, period, frac):
        d = nt.nodes.new('ShaderNodeMath'); d.operation = 'DIVIDE'; d.inputs[1].default_value = period; nt.links.new(sock, d.inputs[0])
        f = nt.nodes.new('ShaderNodeMath'); f.operation = 'FRACT'; nt.links.new(d.outputs[0], f.inputs[0])
        lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = frac; nt.links.new(f.outputs[0], lt.inputs[0]); return lt.outputs[0]
    zb = band(sep.outputs['Z'], floor_h, win_frac)
    hx = band(sep.outputs['X'], bay, 0.62); hy = band(sep.outputs['Y'], bay, 0.62)
    mx = nt.nodes.new('ShaderNodeMath'); mx.operation = 'MAXIMUM'; nt.links.new(hx, mx.inputs[0]); nt.links.new(hy, mx.inputs[1])
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; nt.links.new(zb, mul.inputs[0]); nt.links.new(mx.outputs[0], mul.inputs[1])
    # mask roof/flat faces out via normal z
    gm = nt.nodes.new('ShaderNodeNewGeometry'); sn = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(gm.outputs['Normal'], sn.inputs[0])
    ab = nt.nodes.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; nt.links.new(sn.outputs['Z'], ab.inputs[0])
    lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = 0.5; nt.links.new(ab.outputs[0], lt.inputs[0])
    m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; nt.links.new(mul.outputs[0], m2.inputs[0]); nt.links.new(lt.outputs[0], m2.inputs[1])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    nt.links.new(m2.outputs[0], mix.inputs['Factor']); mix.inputs['A'].default_value = wall; mix.inputs['B'].default_value = win
    nt.links.new(mix.outputs['Result'], bs.inputs['Base Color'])
    rmx = nt.nodes.new('ShaderNodeMapRange'); rmx.inputs['To Min'].default_value = 0.85; rmx.inputs['To Max'].default_value = 0.25
    nt.links.new(m2.outputs[0], rmx.inputs['Value']); nt.links.new(rmx.outputs['Result'], bs.inputs['Roughness'])
    return m
col = clear_collection('MID_ids_' + TAG)
col['UNVERIFIED'] = 'positions/footprints MEASURED (OSM/GNIS, FCC height); storey height, tones, lattice section UNVERIFIED'
# hide proxies
old = bpy.data.collections.get('MID_distance_proxies_20261014x'); nh = 0
if old:
    for o in old.objects:
        if o.name.startswith(('MID_apartment_pair', 'MID_lattice_mast')):
            o.hide_render = True; o.hide_viewport = True; o['bp_hidden_by'] = TAG; nh += 1
print('BP hidden proxies', nh, [o.name for o in old.objects] if old else None)
# hide older house-proxy instances that stood in for the same two towers (ad/ae/pj/af house passes)
def inside(pt, poly):
    x, y = pt; c = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1: c = not c
    return c
hid2 = []
for cc in bpy.data.collections:
    if not cc.name.startswith('MID_houses'): continue
    for o in cc.objects:
        for b in D['buildings']:
            t = o.matrix_world.translation if o.matrix_world.translation.length > 0 else o.location  # hidden objs read 0 matrix after reload
            if inside((t.x, t.y), b['xy']):
                o.hide_render = True; o.hide_viewport = True; o['bp_hidden_by'] = TAG; hid2.append((cc.name, o.name, b['name']))
print('BP hidden house proxies', hid2)
# buildings
m_wall = facade_mat('MID_cct_facade_' + TAG, (0.50, 0.41, 0.29, 1), (0.07, 0.07, 0.08, 1))
m_roof, *_ = node_mat('MID_cct_roof_' + TAG, (0.30, 0.29, 0.27, 1), 0.9)
for b in D['buildings']:
    H = b['levels'] * 3.0 + 2.0; g = min(b['dem_ground']) - 0.5
    bm = bmesh.new(); vs = [bm.verts.new((x, y, g)) for x, y in b['xy']]
    f = bm.faces.new(vs); bmesh.ops.recalc_face_normals(bm, faces=[f])
    if f.normal.z < 0: f.normal_flip()
    r = bmesh.ops.extrude_face_region(bm, geom=[f]); top = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, 0, H))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for fc in bm.faces: fc.material_index = 1 if abs(fc.normal.z) > 0.5 else 0
    me = bpy.data.meshes.new('MID_' + b['name'].replace(' ', '_') + '_' + TAG); bm.to_mesh(me); bm.free()
    me.materials.append(m_wall); me.materials.append(m_roof)
    ob = bpy.data.objects.new(me.name, me); col.objects.link(ob)
    ob['osm_id'] = str(b['osm_id']); ob['MEASURED'] = 'OSM footprint + building:levels; 3DEP DEM ground'
    ob['UNVERIFIED'] = 'height = levels*3.0+2 m; facade tone/window grid artistic'
    print('BP bldg', b['name'], 'H', H, 'ground', round(g, 1), 'faces', len(me.polygons))
# masts
m_or, *_ = node_mat('MID_wpat_orange_' + TAG, (0.70, 0.14, 0.05, 1), 0.7)
m_wh, *_ = node_mat('MID_wpat_white_' + TAG, (0.78, 0.78, 0.76, 1), 0.7)
def strut(bm, a, b, r, mi):
    d = b - a; L = d.length
    if L < 1e-3: return
    z = d.normalized(); x = z.cross(Vector((0, 0, 1)) if abs(z.z) < 0.9 else Vector((1, 0, 0))).normalized(); y = z.cross(x)
    ring0 = [bm.verts.new(a + (x * math.cos(t) + y * math.sin(t)) * r) for t in (0, 2.094, 4.189)]
    ring1 = [bm.verts.new(b + (x * math.cos(t) + y * math.sin(t)) * r) for t in (0, 2.094, 4.189)]
    for i in range(3):
        f = bm.faces.new((ring0[i], ring0[(i + 1) % 3], ring1[(i + 1) % 3], ring1[i])); f.material_index = mi
W = 1.5; SEG = 1.5
for m in D['masts']:
    H = m['h_agl']; g = m['dem_ground'] - 0.5; cx, cy = m['xy']
    R = W / math.sqrt(3)
    legs = [Vector((cx + R * math.cos(t), cy + R * math.sin(t), 0)) for t in (math.pi / 2, math.pi / 2 + 2.094, math.pi / 2 + 4.189)]
    bm = bmesh.new(); n = int(H / SEG)
    band = lambda z: 0 if int(min(6, max(0, (z - g) / (H / 7)))) % 2 == 0 else 1
    for k in range(n):
        z0 = g + k * SEG; z1 = z0 + SEG; mi = band((z0 + z1) / 2)
        for i in range(3):
            a = legs[i].copy(); b = legs[(i + 1) % 3].copy()
            strut(bm, Vector((a.x, a.y, z0)), Vector((a.x, a.y, z1)), 0.07, mi)            # leg
            strut(bm, Vector((a.x, a.y, z0)), Vector((b.x, b.y, z1)), 0.03, mi)            # diagonal
            if k % 2 == 0: strut(bm, Vector((a.x, a.y, z0)), Vector((b.x, b.y, z0)), 0.03, mi)  # horizontal
    me = bpy.data.meshes.new(f"MID_WPAT_tower_{m['osm_id']}_{TAG}"); bm.to_mesh(me); bm.free()
    me.materials.append(m_or); me.materials.append(m_wh)
    ob = bpy.data.objects.new(me.name, me); col.objects.link(ob)
    ob['osm_id'] = str(m['osm_id']); ob['MEASURED'] = 'OSM/GNIS 885051 position; FCC ASR 108.2 m AGL; 3DEP ground'
    ob['UNVERIFIED'] = 'lattice face width 1.5 m, 7-band orange/white paint, no capacity hat'
    print('BP mast', m['osm_id'], 'H', H, 'ground', round(g, 1), 'faces', len(me.polygons))
for o in col.objects: o['bp_pass'] = TAG
bpy.context.scene['bp_mid_ground_ids'] = TAG
if os.environ.get('SAVE') == '1':
    bpy.ops.wm.save_mainfile(); print('BP SAVED')

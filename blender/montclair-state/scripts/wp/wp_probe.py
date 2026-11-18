"""wp throwaway probe: WO patch materials, WM_litter_mask / wk_litter samples vs WJ, OSM/CHM/crown coverage.
Does NOT save the main file."""
import bpy, json, numpy as np, os
from mathutils import Vector

R = '/workspace/nj-scenes/montclair-state'
OUT = f'{R}/data/wp/probe.json'
rep = {}

name = 'WO_gully_head_LiDAR_patch_UNVERIFIED'
E = bpy.data.objects.get(name)
rep['wo_exists'] = E is not None
if not E:
    json.dump(rep, open(OUT, 'w'), indent=1)
    print('NO WO PATCH')
    raise SystemExit(1)

me = E.data
rep['wo_verts'] = len(me.vertices)
rep['wo_faces'] = len(me.polygons)
rep['wo_mats'] = [s.material.name if s.material else None for s in E.material_slots]
rep['wo_mat_users_of_WH'] = None
wh = bpy.data.materials.get('WH_east_dorm_patch_tone_UNVERIFIED')
rep['WH_exists'] = wh is not None
if wh:
    rep['WH_users'] = [o.name for o in bpy.data.objects if o.type == 'MESH' and any(s.material == wh for s in o.material_slots)]
    nt = wh.node_tree
    nodes = [{
        'name': n.name, 'type': n.bl_idname,
        'image': getattr(getattr(n, 'image', None), 'name', None)
    } for n in nt.nodes if n.name.startswith(('WK_', 'WM_'))]
    rep['WH_WK_WM_nodes'] = nodes
    # WK_fac_mr input source
    fm = nt.nodes.get('WK_fac_mr')
    if fm:
        links = []
        for l in fm.inputs['Value'].links:
            links.append({'from': l.from_node.name, 'socket': l.from_socket.name})
        rep['WK_fac_mr_inputs'] = links
    im = bpy.data.images.get('WM_litter_mask')
    rep['WM_litter_mask_image'] = None if not im else {
        'size': list(im.size), 'colorspace': im.colorspace_settings.name,
        'packed': bool(im.packed_file), 'filepath': im.filepath
    }

# attributes on WO
rep['wo_attrs'] = []
for a in me.attributes:
    if a.name.startswith('.'):
        continue
    info = {'name': a.name, 'type': a.data_type, 'domain': a.domain}
    if a.domain == 'POINT' and a.data_type == 'FLOAT' and len(me.vertices):
        vals = np.array([a.data[i].value for i in range(len(me.vertices))])
        info.update({'min': float(vals.min()), 'max': float(vals.max()),
                     'mean': float(vals.mean()), 'gt01': float((vals > 0.1).mean()),
                     'gt05': float((vals > 0.5).mean())})
    rep['wo_attrs'].append(info)

# sample mask image at world XY (same mapping as wm_fix: x120-320, y215-420)
X0, Y0, SX, SY = 120.0, 215.0, 200.0, 205.0
im = bpy.data.images.get('WM_litter_mask')
px = None
if im:
    w, h = im.size
    raw = np.array(im.pixels[:]).reshape(h, w, im.channels)
    # blender image pixels are bottom-to-top already matching the flipped PNG
    px = raw[:, :, 0]

def sample_mask(x, y):
    if px is None:
        return None
    u = (x - X0) / SX
    v = (y - Y0) / SY
    if not (0 <= u <= 1 and 0 <= v <= 1):
        return 0.0
    i = min(max(int(u * (px.shape[1] - 1)), 0), px.shape[1] - 1)
    j = min(max(int(v * (px.shape[0] - 1)), 0), px.shape[0] - 1)
    return float(px[j, i])

def attr_val(obj, an, i):
    a = obj.data.attributes.get(an)
    if not a or a.domain != 'POINT':
        return None
    if a.data_type == 'FLOAT':
        return float(a.data[i].value)
    return None

def summarize(obj, pred, tag):
    mw = obj.matrix_world
    rows = []
    for i, v in enumerate(obj.data.vertices):
        c = mw @ v.co
        if pred(c.x, c.y, c.z):
            rows.append({
                'x': round(c.x, 2), 'y': round(c.y, 2), 'z': round(c.z, 2),
                'mask': sample_mask(c.x, c.y),
                'wk_litter': attr_val(obj, 'wk_litter', i),
                'ou_edge': attr_val(obj, 'ou_edge', i),
                'wh_edge': attr_val(obj, 'wh_edge', i),
                'wo_in': attr_val(obj, 'wo_in', i),
            })
    def col(k):
        vals = [r[k] for r in rows if r[k] is not None]
        if not vals:
            return None
        a = np.array(vals)
        return {'n': len(vals), 'min': float(a.min()), 'max': float(a.max()),
                'mean': float(a.mean()), 'gt01': float((a > 0.1).mean()),
                'gt05': float((a > 0.5).mean())}
    return {
        'n': len(rows),
        'mask': col('mask'), 'wk_litter': col('wk_litter'),
        'ou_edge': col('ou_edge'), 'wh_edge': col('wh_edge'),
        'z': col('z'),
        'samples': rows[::max(1, len(rows)//12)][:12]
    }

WJ = bpy.data.objects['WJ_south_gully_LiDAR_patch_ext_UNVERIFIED']
# WO hollow = NE dip (approx x>=170, y>=314) vs plateau
rep['WO_hollow'] = summarize(E, lambda x, y, z: x >= 170 and y >= 314, 'hollow')
rep['WO_plateau'] = summarize(E, lambda x, y, z: x <= 170 and y <= 310, 'plateau')
rep['WO_all'] = summarize(E, lambda x, y, z: True, 'all')
rep['WJ_litter_core'] = summarize(WJ, lambda x, y, z: 190 <= x <= 220 and 300 <= y <= 318, 'wj')

# trees whose origin or bbox overlaps WO box
trees = []
for o in bpy.data.objects:
    if o.type != 'MESH' or 'tree' not in o.name.lower():
        continue
    t = o.matrix_world.translation
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    xs = [p.x for p in bb]; ys = [p.y for p in bb]; zs = [p.z for p in bb]
    overlap = not (max(xs) < 155 or min(xs) > 182 or max(ys) < 292 or min(ys) > 320)
    in_box = 155 <= t.x <= 182 and 292 <= t.y <= 320
    near = 147 <= t.x <= 192 and 284 <= t.y <= 330
    if overlap or in_box or near:
        trees.append({
            'name': o.name, 'origin': [round(t.x, 2), round(t.y, 2), round(t.z, 2)],
            'zmin': round(min(zs), 2),
            'bbox_xy': [round(min(xs), 1), round(max(xs), 1), round(min(ys), 1), round(max(ys), 1)],
            'in_box': in_box, 'overlap': overlap
        })
rep['trees'] = trees
rep['n_objects'] = len(bpy.data.objects)

# cameras
rep['cams'] = [o.name for o in bpy.data.objects if o.type == 'CAMERA' and (
    o.name.startswith(('WO', 'WP', 'WJ_CAM', 'WF_CAM', 'TI_CAM_oblique_east', 'WN_CAM')))]

json.dump(rep, open(OUT, 'w'), indent=1)
print('WROTE', OUT)
print('mats', rep['wo_mats'])
print('WH users', rep.get('WH_users'))
print('WK_fac_mr', rep.get('WK_fac_mr_inputs'))
print('WO_hollow mask', rep['WO_hollow']['mask'])
print('WO_plateau mask', rep['WO_plateau']['mask'])
print('WO_all mask', rep['WO_all']['mask'])
print('WJ mask', rep['WJ_litter_core']['mask'])
print('trees in/near', len(trees), 'in_box', sum(1 for t in trees if t['in_box']), 'overlap', sum(1 for t in trees if t['overlap']))
print('NO SAVE')

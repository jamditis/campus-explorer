"""wp: reload the updated WM_litter_mask into the packed image (nodes untouched),
tag the WO patch, add a closeup cam that looks into the ravine-head hollow from the
SW lawn plateau so the floor is visible (not the underside of leaf cards)."""
import bpy, json, math, os
from mathutils import Vector

R = '/workspace/nj-scenes/montclair-state'
PNG = f'{R}/data/wm/wm_litter_mask.png'
rep = {}

old = bpy.data.images.get('WM_litter_mask')
rep['had_old'] = old is not None
users = []
if old:
    for mat in bpy.data.materials:
        if not mat.use_nodes or not mat.node_tree:
            continue
        for n in mat.node_tree.nodes:
            if getattr(n, 'image', None) == old:
                users.append((mat.name, n.name))
rep['old_users'] = users

new = bpy.data.images.load(PNG)
new.name = 'WM_litter_mask_wp_load'
new.colorspace_settings.name = 'Non-Color'
if not new.packed_file:
    new.pack()

retargeted = []
for mat_name, node_name in users:
    mat = bpy.data.materials[mat_name]
    mat.node_tree.nodes[node_name].image = new
    retargeted.append((mat_name, node_name))
rep['retargeted'] = retargeted

if old:
    bpy.data.images.remove(old)
new.name = 'WM_litter_mask'
rep['image'] = {
    'size': list(new.size), 'packed': bool(new.packed_file),
    'colorspace': new.colorspace_settings.name, 'filepath': new.filepath
}

# confirm shader hook still intact (do not recreate WK_ nodes)
wh = bpy.data.materials['WH_east_dorm_patch_tone_UNVERIFIED']
fm = wh.node_tree.nodes.get('WK_fac_mr')
src = None
if fm and fm.inputs['Value'].links:
    ln = fm.inputs['Value'].links[0]
    src = {'from': ln.from_node.name, 'image': getattr(getattr(ln.from_node, 'image', None), 'name', None)}
rep['WK_fac_mr'] = src
wh['wp_mat'] = 1
sm = bpy.data.materials.get('WM_skirt_litter_UNVERIFIED')
if sm:
    sm['wp_mat'] = 1

E = bpy.data.objects['WO_gully_head_LiDAR_patch_UNVERIFIED']
E['wp_obj'] = 1
E['UNVERIFIED_wp'] = (
    'wp: ravine-head woodland hollow (OSM wood 315835594 AND (2017 CHM canopy>3 '
    'OR low ravine floor z<134.5 m)) now uses a raised WM_litter_mask so the floor '
    'matches the WJ ravine litter, including gaps between crowns. Stone Hall lawn '
    'plateau west/south of the wood edge is unchanged (mask 0).'
)

# collection + closeup cam
cname = 'WP_gully_head_litter_UNVERIFIED'
col = bpy.data.collections.get(cname) or bpy.data.collections.new(cname)
if col.name not in bpy.context.scene.collection.children:
    bpy.context.scene.collection.children.link(col)

cam_name = 'WP_CAM_closeup_gully_head_floor'
old_cam = bpy.data.objects.get(cam_name)
if old_cam:
    bpy.data.objects.remove(old_cam, do_unlink=True)
cd = bpy.data.cameras.new(cam_name)
cd.lens = 35
cd.clip_end = 30000
cam = bpy.data.objects.new(cam_name, cd)
col.objects.link(cam)
# from the open lawn plateau SW of the hollow, looking NE down onto the wooded dip
# target ~ (174, 318, 131) = west/upper side of the hollow (z~129–134), not the
# (168, 306) plateau that wo's temp closeup aimed at.
loc = Vector((158.0, 302.0, 152.0))
tgt = Vector((174.0, 318.0, 131.0))
cam.location = loc
d = tgt - loc
cam.rotation_euler = (
    math.pi / 2 + math.atan2(d.z, math.hypot(d.x, d.y)),
    0,
    math.atan2(d.y, d.x) - math.pi / 2,
)
cam['wp_obj'] = 1
cam['UNVERIFIED'] = (
    'wp: closeup of the ravine-head woodland floor from the SW lawn plateau '
    '(158,302,152) -> (174,318,131), 35 mm; placed to see the hollow floor rather '
    'than the underside of a tree crown'
)
rep['cam'] = {'name': cam_name, 'loc': list(loc), 'tgt': list(tgt), 'lens': 35}

rep['n_objects'] = len(bpy.data.objects)
json.dump(rep, open(f'{R}/data/wp/fix_report.json', 'w'), indent=1)
print('REP', json.dumps(rep, indent=1))
bpy.ops.wm.save_mainfile()
print('SAVED objs', rep['n_objects'])

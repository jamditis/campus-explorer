"""vg polish2: drop SE oblique to mid-facade; pull S closeup further for full stack. SAVE=1."""
import bpy, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vg'
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
OUT = 0.08
TOPZ = 147.05
log = {'session': 'vg_polish2', 'fixes': []}

e3 = [e for e in OSM['edges'] if e['i'] == 3][0]
U3 = Vector((e3['u'][0], e3['u'][1], 0)).normalized()
N3 = Vector((e3['n'][0], e3['n'][1], 0)).normalized()
A3 = Vector((e3['a'][0], e3['a'][1], 0))
L3 = e3['len']
e5 = [e for e in OSM['edges'] if e['i'] == 5][0]
U5 = Vector((e5['u'][0], e5['u'][1], 0)).normalized()
N5 = Vector((e5['n'][0], e5['n'][1], 0)).normalized()
A5 = Vector((e5['a'][0], e5['a'][1], 0))
L5 = e5['len']

# SE corner of building approx
se = A3 + U3 * L3  # near SE corner along S edge end
# Actually S edge goes E; E edge goes N from near SE. Mid of visible SE: blend
cent = A3 + U3 * (L3 * 0.55) + N3 * (-2.0)  # slightly in from S face
cam4 = bpy.data.objects.get('VG_CAM_oblique_Freeman_from_SE')
if cam4:
    # eye-ish oblique from SE, mid height — see S face + E turn
    cam4.location = (cent.x + N3.x * 22.0 + U3.x * 8.0,
                     cent.y + N3.y * 22.0 + U3.y * 8.0,
                     GR + 14.0)
    tgt = (cent.x - U3.x * 6.0, cent.y - U3.y * 6.0, GR + 7.0)
    direction = Vector(tgt) - Vector(cam4.location)
    cam4.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    if cam4.data: cam4.data.lens = 30
    log['fixes'].append('SE_oblique_mid_facade')

# S closeup — further pullback for full 5-band stack
c_s = A3 + U3 * 7.5
cam = bpy.data.objects.get('VG_CAM_closeup_Freeman_S_pane_grid')
if cam:
    cam.location = (c_s.x + N3.x * 12.0, c_s.y + N3.y * 12.0, GR + 8.0)
    tgt = (c_s.x + N3.x * (OUT + 0.22), c_s.y + N3.y * (OUT + 0.22), (GR + TOPZ) / 2)
    direction = Vector(tgt) - Vector(cam.location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    if cam.data: cam.data.lens = 35
    log['fixes'].append('S_closeup_full_height_pullback')

json.dump(log, open(DATA + '/vg_polish2.json', 'w'), indent=2)
print('VG POLISH2', json.dumps(log))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')

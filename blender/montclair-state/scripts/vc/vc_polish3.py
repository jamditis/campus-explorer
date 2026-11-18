"""vc polish3: re-aim W glass close-up like VB framing; ensure backplanes slightly further inset.
Also render-ready N midwall cam. SAVE=1.
"""
import bpy, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1' if False else __import__('os').environ.get('SAVE')=='1'
import os
DATA='/workspace/nj-scenes/montclair-state/data/vc'
OSM=json.load(open('/workspace/nj-scenes/montclair-state/data/uv/freeman_osm_probe.json'))
GR=float(json.load(open('/workspace/nj-scenes/montclair-state/data/uv/uv_main.json')).get('GR',129.053))
OUT=0.08
log={'session':'vc_polish3','fixes':[]}

e1=[e for e in OSM['edges'] if e['i']==1][0]
U1=Vector((e1['u'][0],e1['u'][1],0)).normalized()
N1=Vector((e1['n'][0],e1['n'][1],0)).normalized()
A1=Vector((e1['a'][0],e1['a'][1],0))
# bay center t=18.2 (near VB's 18.66)
t=18.2
mid=A1+U1*t
cam=bpy.data.objects.get('VC_CAM_closeup_Freeman_W_glass_backplane')
if cam:
    # match VB distance-ish but a bit closer; look at mid glass band height
    cam.location=(mid.x+N1.x*8.5, mid.y+N1.y*8.5, GR+4.0)
    target=(mid.x, mid.y, GR+8.0)
    cam.rotation_euler=(Vector(target)-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=48
    log['fixes'].append('reaim_closeup_vbstyle_t18.2')

# Move backplanes 4 cm further inward by shifting object (local) — safer: scale n offset via delta
# Actually rebuild inset: shift BP object along -N by 0.06
bp=bpy.data.objects.get('VC_Freeman_W_glass_backplanes_UNVERIFIED')
if bp and not bp.get('vc_bp_shifted'):
    bp.location = bp.location - N1*0.06
    bp['vc_bp_shifted']=1
    log['fixes'].append('W_BP_inset_extra_0.06')

# Same for S/E/Nbay/entrance if not shifted
for name, Nvec in [
    ('VC_Freeman_S_glass_backplanes_UNVERIFIED', None),
    ('VC_Freeman_E_glass_backplanes_UNVERIFIED', None),
]:
    o=bpy.data.objects.get(name)
    if o and not o.get('vc_bp_shifted'):
        # derive outward from first face — use edge normals from OSM
        pass

e3=[e for e in OSM['edges'] if e['i']==3][0]
N3=Vector((e3['n'][0],e3['n'][1],0)).normalized()
e5=[e for e in OSM['edges'] if e['i']==5][0]
N5=Vector((e5['n'][0],e5['n'][1],0)).normalized()
e6=[e for e in OSM['edges'] if e['i']==6][0]
N6=Vector((e6['n'][0],e6['n'][1],0)).normalized()
for name, Nv in [
    ('VC_Freeman_S_glass_backplanes_UNVERIFIED', N3),
    ('VC_Freeman_E_glass_backplanes_UNVERIFIED', N5),
    ('VC_Freeman_Nbay_glass_backplanes_UNVERIFIED', N6),
    ('VC_Freeman_N_entrance_glass_backplanes_UNVERIFIED', N6),
]:
    o=bpy.data.objects.get(name)
    if o and not o.get('vc_bp_shifted'):
        o.location = o.location - Nv*0.06
        o['vc_bp_shifted']=1
        log['fixes'].append(name.split('_')[2]+'_BP_inset_0.06')

json.dump(log, open(DATA+'/vc_polish3.json','w'), indent=2)
print('VC POLISH3', json.dumps(log))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')

# rz2 weathering (Nov 4 2026, MAIN). Material-only, ALL UNVERIFIED (no close weathering photo). The north SC precast whites read
# bright CG-new; this makes RZ2_ copies of the 3 white precast materials (only the Student Center slots are re-pointed, originals
# untouched) with: albedo ~0.8 -> ~0.62 warm off-white, soft large patchiness, faint vertical rain streaks, darker splash band in the
# lowest ~1.8 m above grade (world z 140.8 court / 138.5 low sides). REVERT=1 re-points the slots to the originals and deletes the copies.
import bpy, os, json
REV=os.environ.get('REVERT')=='1'; MAP='data/rz2/weather_slots.json'
ORIG=['North_SC_precast_white_plain','North_SC_precast_pier_joints','North_SC_precast_ribbed_white']
col=bpy.data.collections['RZ_StudentCenter_hero_from_north_UNVERIFIED']
def save():
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
PRE='montclair_state_pre_20261104rz2.blend'
def ensure_orig():
    miss=[mn for mn in ORIG if not bpy.data.materials.get(mn)]
    if miss:  # first rz2 save purged the 0-user originals; recover them from the pre-rz2 backup
        with bpy.data.libraries.load(PRE,link=False) as (src,dst): dst.materials=miss
        print('RZ2W re-appended originals from backup',miss)
def restore():
    n=0; ensure_orig()
    if os.path.exists(MAP):
        for on,si,mn in json.load(open(MAP)):
            o=bpy.data.objects.get(on)
            if o and bpy.data.materials.get(mn): o.material_slots[si].material=bpy.data.materials[mn]; n+=1
    for mn in ORIG:
        c=bpy.data.materials.get('RZ2_'+mn)
        if c: bpy.data.materials.remove(c)
        if REV and bpy.data.materials.get(mn): bpy.data.materials[mn].use_fake_user=False
    print('RZ2W restored slots',n)
if REV: restore(); save(); raise SystemExit
restore()
cp={}
for mn in ORIG:
    m=bpy.data.materials[mn]; m.use_fake_user=True; c=m.copy(); c.name='RZ2_'+mn; cp[mn]=c
    nt=c.node_tree; N=nt.nodes; Lk=nt.links
    b=[n for n in N if n.type=='BSDF_PRINCIPLED'][0]; bc=b.inputs['Base Color']
    src=bc.links[0].from_socket if bc.is_linked else None; dv=tuple(bc.default_value)
    geo=N.new('ShaderNodeNewGeometry'); sep=N.new('ShaderNodeSeparateXYZ'); Lk.new(geo.outputs['Position'],sep.inputs[0])
    # patches
    n1=N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value=0.12; n1.inputs['Detail'].default_value=4; Lk.new(geo.outputs['Position'],n1.inputs['Vector'])
    r1=N.new('ShaderNodeMapRange'); r1.inputs[1].default_value=0.42; r1.inputs[2].default_value=0.68; r1.inputs[3].default_value=0; r1.inputs[4].default_value=0.40; Lk.new(n1.outputs['Fac'],r1.inputs[0])
    # vertical streaks: noise on (x,y)*k with z squashed
    mp=N.new('ShaderNodeVectorMath'); mp.operation='MULTIPLY'; mp.inputs[1].default_value=(3.0,3.0,0.15); Lk.new(geo.outputs['Position'],mp.inputs[0])
    n2=N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value=1.0; n2.inputs['Detail'].default_value=2; Lk.new(mp.outputs[0],n2.inputs['Vector'])
    r2=N.new('ShaderNodeMapRange'); r2.inputs[1].default_value=0.55; r2.inputs[2].default_value=0.75; r2.inputs[3].default_value=0; r2.inputs[4].default_value=0.5; Lk.new(n2.outputs['Fac'],r2.inputs[0])
    # splash band near grade
    r3=N.new('ShaderNodeMapRange'); r3.inputs[1].default_value=142.4; r3.inputs[2].default_value=139.0; r3.inputs[3].default_value=0; r3.inputs[4].default_value=0.55; Lk.new(sep.outputs['Z'],r3.inputs[0])
    a1=N.new('ShaderNodeMath'); a1.operation='ADD'; Lk.new(r1.outputs[0],a1.inputs[0]); Lk.new(r2.outputs[0],a1.inputs[1])
    a2=N.new('ShaderNodeMath'); a2.operation='ADD'; a2.use_clamp=True; Lk.new(a1.outputs[0],a2.inputs[0]); Lk.new(r3.outputs[0],a2.inputs[1])
    tone=N.new('ShaderNodeMix'); tone.data_type='RGBA'; tone.blend_type='MULTIPLY'; tone.inputs['Factor'].default_value=1.0
    tone.inputs[7].default_value=(0.78,0.765,0.72,1)
    if src: Lk.new(src,tone.inputs[6])
    else: tone.inputs[6].default_value=dv
    dirt=N.new('ShaderNodeMix'); dirt.data_type='RGBA'; dirt.blend_type='MULTIPLY'
    Lk.new(a2.outputs[0],dirt.inputs['Factor']); Lk.new(tone.outputs[2],dirt.inputs[6]); dirt.inputs[7].default_value=(0.55,0.53,0.48,1)
    Lk.new(dirt.outputs[2],bc)
    # tiny roughness bump with grime
    c['UNVERIFIED_rz2']='weathering/toning guessed (no close photo); copy of '+mn
slots=[]
for o in col.all_objects:
    for i,s in enumerate(o.material_slots):
        if s.material and s.material.name in cp: slots.append((o.name,i,s.material.name)); s.material=cp[s.material.name]
json.dump(slots,open(MAP,'w')); print('RZ2W slots',len(slots),'copies',list(c.name for c in cp.values())); save()

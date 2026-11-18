"""vs: break the overnight alpha/overlay loop. (1) Joe Nov 6 'more reflective where no interior':
Freeman glass -> opaque reflective glazing (Alpha 1, Transmission 0, low rough, dark cool base) so it
reflects the Nishita sky instead of exposing dark backplanes. (2) Hide 80 redundant stacked W interbay
overlays (VJ..VQ x10 each) under VR set (kept VE + VR). (3) Tame fake sky-tint emission.
REVERT=1 restores from stash. SAVE=1 saves."""
import bpy, os, json, re
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
D='/workspace/nj-scenes/montclair-state/data/vs/'; ST=D+'vs_stash.json'
GLASS=['VD_Freeman_W_glass_pane_UNVERIFIED','VG_Freeman_SE_glass_pane_UNVERIFIED',
       'VB_Freeman_glass_cool_clear_UNVERIFIED','UV_Freeman_curtain_glass_UNVERIFIED']
SKY='VF_Freeman_W_sky_tint_UNVERIFIED'
KEYS=['Alpha','Transmission Weight','Roughness','Specular IOR Level','IOR','Coat Weight','Coat Roughness','Base Color','Emission Strength']
SKYEMIS=float(os.environ.get('SKYE','1.2')); SKYA=float(os.environ.get('SKYA','0.12'))
def bsdf(n):
    m=bpy.data.materials.get(n); return m.node_tree.nodes.get('Principled BSDF') if m and m.use_nodes else None
def rd(b,k):
    v=b.inputs[k].default_value; return list(v) if hasattr(v,'__len__') else v
if REVERT:
    st=json.load(open(ST))
    for n,vals in st['mats'].items():
        b=bsdf(n)
        if b:
            for k,v in vals.items(): b.inputs[k].default_value=v
    for on in st['hidden']:
        o=bpy.data.objects.get(on)
        if o: o.hide_render=False; o.hide_viewport=False; o['vs_hidden']=0
    if 'cam' in st:
        c=bpy.data.objects.get(st['cam']['name'])
        if c: c.location=st['cam']['loc']; c.rotation_euler=st['cam']['rot']
    print('VS REVERT done')
else:
    st={'mats':{},'hidden':[]}
    for n in GLASS+[SKY]:
        b=bsdf(n)
        if b: st['mats'][n]={k:rd(b,k) for k in KEYS if k in b.inputs}
    for n in GLASS:
        b=bsdf(n)
        if not b: continue
        b.inputs['Alpha'].default_value=1.0
        b.inputs['Transmission Weight'].default_value=0.0
        b.inputs['Roughness'].default_value=0.03
        b.inputs['Base Color'].default_value=(0.035,0.05,0.065,1.0)
        b.inputs['Specular IOR Level'].default_value=0.75
        b.inputs['IOR'].default_value=1.52
        b.inputs['Coat Weight'].default_value=0.35
        b.inputs['Coat Roughness'].default_value=0.02
        bpy.data.materials[n]['vs_mat']=1
    b=bsdf(SKY)
    if b:
        b.inputs['Emission Strength'].default_value=SKYEMIS; b.inputs['Alpha'].default_value=SKYA
    for o in bpy.data.objects:
        m=re.match(os.environ.get('IBRE',r'(V[J-R])_Freeman_W_interbay'),o.name)
        if m and not o.hide_render:
            o.hide_render=True; o.hide_viewport=True; o['vs_hidden']=1; st['hidden'].append(o.name)
    # N entrance eye cam sat ~0-1 m inside a terrain bank (black wedge lower-left) -> lift to eye height over the bank
    c=bpy.data.objects.get('UV_CAM_eye_Freeman_N_entrance')
    if c:
        from mathutils import Vector
        st['cam']={'name':c.name,'loc':list(c.location),'rot':list(c.rotation_euler)}
        dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
        zmax=-1e9
        fwd=(c.matrix_world.to_quaternion()@Vector((0,0,-1))); fwd.z=0; fwd.normalize()
        T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; Ti=T.matrix_world.inverted()
        for k in range(0,7):
            p=c.location+fwd*(k*0.5)
            a=Ti@Vector((p.x,p.y,p.z+30)); b=Ti@Vector((p.x,p.y,p.z-30))
            ok,loc,n,i=T.ray_cast(a,(b-a).normalized())
            if ok: zmax=max(zmax,(T.matrix_world@loc).z)
        newz=max(c.location.z, zmax+1.65)
        st['cam']['newz']=newz; st['cam']['bank']=zmax
        c.location.z=newz
        c.rotation_euler.x-=0.04  # tip down slightly so doors stay framed
        print('VS cam lift', round(zmax,2), '->', round(newz,2))
    if not os.path.exists(ST) or os.environ.get('RESTASH')=='1':
        json.dump(st,open(ST,'w'),indent=1)
    print('VS applied glass',len(st['mats']),'hidden',len(st['hidden']))
print('OBJECTS',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

import bpy, math, os
sc=bpy.context.scene
base=bpy.data.worlds.get('Sky') or bpy.data.worlds['North_sky']; sun=bpy.data.objects.get('Sun') or bpy.data.objects['North_sun']
HAS_HDRI='Environment Texture' in base.node_tree.nodes
COL='WP2_Lighting_presets_20261109wp2'
col=bpy.data.collections.get(COL) or bpy.data.collections.new(COL)
if COL not in [c.name for c in sc.collection.children]: sc.collection.children.link(col)
R=math.radians
P={'MORNING':dict(el=16,az=112,energy=2.6,color=(1.0,0.90,0.78),ang=0.8,bg=0.40,hdri=0.55,tint=(1.0,0.96,0.90),sat=1.0),
   'GOLDEN': dict(el=6, az=245,energy=2.4,color=(1.0,0.70,0.45),ang=0.8,bg=0.55,hdri=0.42,tint=(1.0,0.78,0.58),sat=0.85),
   'OVERCAST':dict(el=40,az=190,energy=0.10,color=(0.93,0.96,1.0),ang=40.0,bg=1.45,hdri=0.62,tint=(0.95,0.97,1.0),sat=0.12)}
for k,v in P.items():
    old=bpy.data.worlds.get('WP2_World_'+k)
    if old: bpy.data.worlds.remove(old)
    w=base.copy(); w.name='WP2_World_'+k; w.use_fake_user=True
    nt=w.node_tree; N=nt.nodes; L=nt.links
    sky=N['Sky Texture']; sky.sun_elevation=R(v['el']); sky.sun_rotation=R(v['az'])
    N['Background'].inputs['Strength'].default_value=v['bg']
    if HAS_HDRI:
     N['Background.001'].inputs['Strength'].default_value=v['hdri']
     env=N['Environment Texture']; b1=N['Background.001']
     hs=N.new('ShaderNodeHueSaturation'); hs.name='WP2_hdri_sat'; hs.inputs['Saturation'].default_value=v['sat']
     mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.name='WP2_hdri_tint'
     mx.inputs[0].default_value=1.0; mx.inputs[7].default_value=(*v['tint'],1.0)
     L.new(env.outputs['Color'],hs.inputs['Color']); L.new(hs.outputs['Color'],mx.inputs[6]); L.new(mx.outputs[2],b1.inputs['Color'])
    if k=='OVERCAST':
        bg=N['Background']
        for l in list(bg.inputs['Color'].links): L.remove(l)
        bg.inputs['Color'].default_value=(0.78,0.80,0.84,1.0)
    o=bpy.data.objects.get('WP2_Sun_'+k)
    if o: bpy.data.objects.remove(o)
    o=sun.copy(); o.data=sun.data.copy(); o.name='WP2_Sun_'+k; o.data.name='WP2_Sun_'+k
    for c in o.users_collection: c.objects.unlink(o)
    col.objects.link(o)
    o.rotation_euler=(R(90-v['el']),0,R(180-v['az']))
    o.data.energy=v['energy']; o.data.color=v['color']; o.data.angle=R(v['ang'])
    o.hide_render=True; o.hide_viewport=True
src=open('/workspace/nj-scenes/montclair-state/scripts/wp2/wp2_apply.py').read().replace("os.environ.get('WP2_PRESET', 'DEFAULT')","'DEFAULT'  # change to MORNING / GOLDEN / OVERCAST")
t=bpy.data.texts.get('LIGHTING_PRESETS.py') or bpy.data.texts.new('LIGHTING_PRESETS.py'); t.clear(); t.write(src)
md=("# Lighting presets (wp2, Nov 9 2026)\n\nOpen LIGHTING_PRESETS.py in the Text editor, set PRESET, Run Script.\n"
 "- DEFAULT: original world '%s' + object '%s' (left exactly as it was).\n"%(base.name,sun.name)+
 "- MORNING: WP2_World_MORNING + WP2_Sun_MORNING, sun el 16 az 112 (mid-morning, autumn), warm-white.\n"
 "- GOLDEN: WP2_World_GOLDEN + WP2_Sun_GOLDEN, sun el 6 az 245 (late afternoon), warm orange, HDRI background tinted.\n"
 "- OVERCAST: WP2_World_OVERCAST + WP2_Sun_OVERCAST, uniform grey sky dome, very soft weak sun (40 deg disc), desaturated HDRI background.\n"
 "Sun angles are representative, not a specific date/time (UNVERIFIED). No materials are changed by any preset.\n")
t2=bpy.data.texts.get('LIGHTING_PRESETS.md') or bpy.data.texts.new('LIGHTING_PRESETS.md'); t2.clear(); t2.write(md)
sc['wp2_lighting_preset']='DEFAULT'
bpy.ops.wm.save_mainfile()
print('ACTIVECAM',sc.camera.name if sc.camera else None);print('SAVED objs',len(bpy.data.objects),[w.name for w in bpy.data.worlds])

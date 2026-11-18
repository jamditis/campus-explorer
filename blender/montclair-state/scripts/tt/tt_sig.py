import bpy, hashlib, json
f = bpy.data.materials['BD_farfield_ortho_haze_bm']
hs = f.node_tree.nodes['Hue/Saturation/Value']
farv = None
for i in hs.inputs:
    if i.name == 'Value' and not i.is_linked:
        farv = float(i.default_value)
suns = []
for o in bpy.data.objects:
    if o.type == 'LIGHT' and o.data.type == 'SUN' and not o.hide_render:
        suns.append((o.name, round(o.data.energy, 6)))
bgs = []
w = bpy.context.scene.world
for n in w.node_tree.nodes:
    if n.type == 'BACKGROUND':
        bgs.append((n.name, round(n.inputs['Strength'].default_value, 6)))
exp = round(bpy.context.scene.view_settings.exposure, 6)
payload = {'nobj': len(bpy.data.objects), 'farv': farv, 'suns': suns, 'bgs': bgs, 'exp': exp}
sig = hashlib.md5(json.dumps(payload, sort_keys=True).encode()).hexdigest()
print('TTSIG', sig, json.dumps(payload))

import bpy
for l in bpy.data.objects:
    if l.type == 'LIGHT' and not l.hide_render:
        print('L', l.name, l.data.type, round(l.data.energy, 4))
w = bpy.context.scene.world
for n in w.node_tree.nodes:
    if n.type == 'BACKGROUND':
        print('BG', n.name, round(n.inputs['Strength'].default_value, 4))
    if n.type == 'TEX_SKY':
        print('SKY', n.sky_type, getattr(n, 'sun_intensity', None), getattr(n, 'sun_elevation', None))
v = bpy.context.scene.view_settings
print('VIEW', v.view_transform, v.look, 'exp', round(v.exposure, 4))
f = bpy.data.materials['BD_farfield_ortho_haze_bm']
hs = f.node_tree.nodes['Hue/Saturation/Value']
for i in hs.inputs:
    if hasattr(i, 'default_value') and not i.is_linked:
        try:
            print('FAR', i.name, round(float(i.default_value), 4))
        except Exception:
            pass
m = bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']
N = m.node_tree.nodes
for nn in ('TS_naip_hsv', 'EP_haze_mr', 'TS_gate'):
    if nn in N:
        for i in N[nn].inputs:
            if hasattr(i, 'default_value') and not i.is_linked:
                try:
                    print('SK', nn, i.name, round(float(i.default_value), 4))
                except Exception:
                    pass

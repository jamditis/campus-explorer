# LIGHTING_PRESETS (wp2, Nov 9 2026). Set PRESET then Run Script (Text editor), or run headless with env WP2_PRESET.
# Presets: DEFAULT (original world 'Sky'/'North_sky' + 'Sun'/'North_sun'), MORNING, GOLDEN, OVERCAST. Only switches scene.world and which sun renders.
import bpy, os
PRESET = os.environ.get('WP2_PRESET', 'DEFAULT')
def apply(preset):
    sc = bpy.context.scene
    p = preset.upper()
    suns = {k: bpy.data.objects.get('WP2_Sun_' + k) for k in ('MORNING', 'GOLDEN', 'OVERCAST')}
    base = bpy.data.objects.get('Sun') or bpy.data.objects.get('North_sun')
    bw = bpy.data.worlds.get('Sky') or bpy.data.worlds.get('North_sky')
    if p == 'DEFAULT':
        sc.world = bw
    else:
        sc.world = bpy.data.worlds['WP2_World_' + p]
    if base: base.hide_render = (p != 'DEFAULT'); base.hide_viewport = (p != 'DEFAULT')
    for k, o in suns.items():
        if o: o.hide_render = (k != p); o.hide_viewport = (k != p)
    sc['wp2_lighting_preset'] = p
    print('LIGHTING PRESET', p, sc.world.name)
apply(PRESET)

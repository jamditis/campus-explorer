# tt (Nov 5 2026 ~4:25 AM ET, MAIN, day 8 east edge): lower far-field HSV Value + optional tiny env knobs.
# ALL UNVERIFIED tone. Reversible (REVERT=1). Prefer this over re-running ts_main so the skirt hole mesh is not recopied.
# Env: FARV (default 0.45), VAL (skirt TS_naip_hsv Value, optional), HAZE (EP_haze_mr To Max, optional),
#      WMAX (TS_gate To Max, optional), SUN_MULT / BG_MULT (tiny world/sun multipliers, optional; 1.0 = no change).
import bpy, os, json
REV = os.environ.get('REVERT') == '1'
D = '/workspace/nj-scenes/montclair-state/'
FAR = 'BD_farfield_ortho_haze_bm'
SK = 'OW2_Context_skirt_ortho_strip_tone_UNVERIFIED'
OUT = D + 'data/tt/tt_orig.json'

def inp(n, k):
    for i in n.inputs:
        if i.name == k and not i.is_linked and hasattr(i, 'default_value'):
            return i

def record_and_set():
    orig = {}
    # Far-field HSV Value
    f = bpy.data.materials[FAR]
    FN = f.node_tree.nodes
    hs = FN['Hue/Saturation/Value']
    i = inp(hs, 'Value')
    farv = float(os.environ.get('FARV', '0.45'))
    orig['far|HSV|Value'] = float(i.default_value)
    i.default_value = farv
    print('TT FARV', orig['far|HSV|Value'], '->', farv)

    # Optional skirt knobs (only if env set)
    m = bpy.data.materials[SK]
    N = m.node_tree.nodes
    if 'VAL' in os.environ and 'TS_naip_hsv' in N:
        i = inp(N['TS_naip_hsv'], 'Value')
        orig['sk|TS_naip_hsv|Value'] = float(i.default_value)
        i.default_value = float(os.environ['VAL'])
        print('TT VAL', orig['sk|TS_naip_hsv|Value'], '->', i.default_value)
    if 'HAZE' in os.environ and 'EP_haze_mr' in N:
        i = inp(N['EP_haze_mr'], 'To Max')
        orig['sk|EP_haze_mr|To Max'] = float(i.default_value)
        i.default_value = float(os.environ['HAZE'])
        print('TT HAZE', orig['sk|EP_haze_mr|To Max'], '->', i.default_value)
    if 'WMAX' in os.environ and 'TS_gate' in N:
        i = inp(N['TS_gate'], 'To Max')
        orig['sk|TS_gate|To Max'] = float(i.default_value)
        i.default_value = float(os.environ['WMAX'])
        print('TT WMAX', orig['sk|TS_gate|To Max'], '->', i.default_value)

    # Optional tiny sun / world strength
    sun_mult = float(os.environ.get('SUN_MULT', '1.0'))
    bg_mult = float(os.environ.get('BG_MULT', '1.0'))
    if abs(sun_mult - 1.0) > 1e-6:
        for o in bpy.data.objects:
            if o.type == 'LIGHT' and o.data.type == 'SUN' and not o.hide_render:
                key = 'sun|%s|energy' % o.name
                orig[key] = float(o.data.energy)
                o.data.energy = orig[key] * sun_mult
                print('TT SUN', o.name, orig[key], '->', o.data.energy)
    if abs(bg_mult - 1.0) > 1e-6:
        w = bpy.context.scene.world
        for n in w.node_tree.nodes:
            if n.type == 'BACKGROUND':
                key = 'bg|%s|Strength' % n.name
                i = n.inputs['Strength']
                orig[key] = float(i.default_value)
                i.default_value = orig[key] * bg_mult
                print('TT BG', n.name, orig[key], '->', i.default_value)

    # View exposure (optional)
    if 'EXPOSURE' in os.environ:
        v = bpy.context.scene.view_settings
        orig['view|exposure'] = float(v.exposure)
        v.exposure = float(os.environ['EXPOSURE'])
        print('TT EXPOSURE', orig['view|exposure'], '->', v.exposure)

    f['tt_orig'] = True  # marker
    with open(OUT, 'w') as fh:
        json.dump(orig, fh, indent=2)
    print('TT wrote', OUT, 'keys', list(orig.keys()))

def revert():
    if not os.path.exists(OUT):
        print('TT no orig json; nothing to revert')
        return
    orig = json.load(open(OUT))
    f = bpy.data.materials.get(FAR)
    if f:
        FN = f.node_tree.nodes
        if 'far|HSV|Value' in orig:
            inp(FN['Hue/Saturation/Value'], 'Value').default_value = orig['far|HSV|Value']
        if 'tt_orig' in f:
            del f['tt_orig']
    m = bpy.data.materials.get(SK)
    if m:
        N = m.node_tree.nodes
        for key, val in orig.items():
            if not key.startswith('sk|'):
                continue
            _, nn, kn = key.split('|', 2)
            if nn in N:
                i = inp(N[nn], kn)
                if i:
                    i.default_value = val
    for key, val in orig.items():
        if key.startswith('sun|'):
            name = key.split('|')[1]
            o = bpy.data.objects.get(name)
            if o and o.type == 'LIGHT':
                o.data.energy = val
        if key.startswith('bg|'):
            nn = key.split('|')[1]
            w = bpy.context.scene.world
            n = w.node_tree.nodes.get(nn)
            if n:
                n.inputs['Strength'].default_value = val
        if key == 'view|exposure':
            bpy.context.scene.view_settings.exposure = val
    print('TT reverted', list(orig.keys()))

if REV:
    revert()
else:
    # If already applied, revert first then re-apply (idempotent)
    if os.path.exists(OUT):
        revert()
    record_and_set()

if os.environ.get('SAVE') == '1':
    bpy.ops.wm.save_mainfile()
    print('SAVED')
print('NOBJ', len(bpy.data.objects))

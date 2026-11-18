import bpy,os
if os.environ.get('HIDEPA')=='1':
    o=bpy.data.objects['PA_walk_panel_tone_chips_UNVERIFIED']; o.hide_render=True; print('PA hidden')
    for md in o.modifiers: print('PA mod inputs',[ (k, md[k]) for k in md.keys() if not k.endswith('_use_attribute') and not k.endswith('_attribute_name')][:12])

# pv: the 38 red 'DK pier accents' plaques (0.5 x 0.62 m, z 140.7-141.3) were extrapolated in aq (Oct 15) from mref_04,
# which shows the EAST face only; all 38 sit on the west/south/north/courtyard faces, where photo dickson_commons_2007
# shows plain buff brick, and at eye level they read as patches. Hide them (render + viewport); object kept. REVERT=1 unhides.
import bpy, os
REV=os.environ.get('REVERT')=='1'
o=[o for o in bpy.data.collections['DK_pier_accents_20261015aq'].objects][0]
if REV:
    if 'pv_prev_hide' in o:
        h=o['pv_prev_hide']; o.hide_render=bool(h[0]); o.hide_viewport=bool(h[1]); o.hide_set(bool(h[2])) if o.name in bpy.context.view_layer.objects else None; del o['pv_prev_hide']; print('REVERTED_PV_ACCENTS')
else:
    o['pv_prev_hide']=[int(o.hide_render),int(o.hide_viewport),int(o.hide_get()) if o.name in bpy.context.view_layer.objects else 0]
    o.hide_render=True; o.hide_viewport=True; print('PV_ACCENTS hidden',o.name)

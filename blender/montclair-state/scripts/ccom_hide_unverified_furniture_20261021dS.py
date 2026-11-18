"""Session dS (~7:46 AM ET Oct 21). MAIN: hide (not delete) the CCOM-entrance bench + trash can, flagged unverified street furniture since
LOG ~line 1397/1415 (2026-10-13 rule; no photo/ortho source). Bins '(photo)' and Lamp_acorn_059 kept. REVERT=1 unhides. SAVE=1 saves."""
import bpy, os, time
rev = os.environ.get('REVERT') == '1'
for n in ('Bench_CCOM_entrance', 'TrashCan_CCOM_entrance'):
    o = bpy.data.objects.get(n)
    if not o: print('dS furn: missing', n); continue
    o.hide_render = o.hide_viewport = not rev; o['dS_hidden_unverified'] = 0 if rev else 1; print('dS furn:', n, 'hidden' if not rev else 'shown')
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('dS furn: SAVED', time.strftime('%H:%M:%S'))

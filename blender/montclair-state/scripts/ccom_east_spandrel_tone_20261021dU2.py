"""2026-10-21 session dU2 (~9:50 AM ET). Match the tone of dU's plain infill above the CCOM east lounge window
(CCOM_east_window_spandrel_dU, was Wall_SCM_precast = darker) to the flanking stucco pier at the same height
(CCOM_lab_lounge_pier_20261014jf -> material CCOM_east_pier_20261014jf, found by ray probe data/dU2/probe_stucco_dU2.py).
Idempotent; original material kept in prop dU2_orig_mat; REVERT=1 restores. Run AFTER the dU scripts. SAVE=1 saves."""
import bpy, os
o = bpy.data.objects['CCOM_east_window_spandrel_dU']; me = o.data
if os.environ.get('REVERT') == '1':
    if 'dU2_orig_mat' in o: me.materials[0] = bpy.data.materials[o['dU2_orig_mat']]; del o['dU2_orig_mat']
else:
    if 'dU2_orig_mat' not in o: o['dU2_orig_mat'] = me.materials[0].name
    pier = bpy.data.objects['CCOM_lab_lounge_pier_20261014jf']
    m = bpy.data.materials['CCOM_east_pier_20261014jf']
    assert m.name in [s.material.name for s in pier.material_slots if s.material]
    for i in range(len(me.materials)): me.materials[i] = m
print('DU2TONE', o.name, [m.name for m in me.materials], flush=True)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('DU2TONE_SAVED', flush=True)

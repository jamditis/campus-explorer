import bpy
o=bpy.data.objects['MO Health Drop-In Center coping (UNVERIFIED)']
red=bpy.data.materials['MH_Annex_coping_red_metal_photo2016']; w=bpy.data.materials['WS23_Annex_coping_white_JoePhoto']
for s in o.material_slots:
    if s.material==w: s.material=red; print('restored red on',o.name)
if 'ws23_coping_was' in o: del o['ws23_coping_was']
bpy.ops.wm.save_mainfile(); print('SAVED')

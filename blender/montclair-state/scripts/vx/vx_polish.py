"""vx polish: streaks read as wood grain on S pier -> broader/softer; piers a touch darker (still UNVERIFIED)."""
import bpy
for n in ['TN_precast_pier_UNVERIFIED','TN_spandrel_band_UNVERIFIED']:
    nt=bpy.data.materials[n].node_tree
    nt.nodes['VX_streak_map'].inputs['Scale'].default_value=(1.6,1.6,0.25)
    nt.nodes['VX_streak_noise'].inputs['Detail'].default_value=2.0
    nt.nodes['VX_streak_range'].inputs['To Min'].default_value=0.92
    for e in nt.nodes['Color Ramp'].color_ramp.elements:
        c=list(e.color); e.color=(c[0]*0.9,c[1]*0.9,c[2]*0.9,1.0)
bpy.ops.wm.save_mainfile(); print('VXP saved',len(bpy.data.objects))

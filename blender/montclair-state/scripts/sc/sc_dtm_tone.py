# sc: the sb Ground_ortho_grass blue-shade tone mask (x -185..-95, y 195..252) left the foreground of SA_CAM_eye_annex_mural_from_W
# (camera at -128,300) blue/teal. Extend the box north to y 360 by moving node SB_y1 (shader only, UNVERIFIED). REVERT=1 restores 252/246.
import bpy,os
m=bpy.data.materials['Ground_ortho_grass']; n=m.node_tree.nodes['SB_y1']
if os.environ.get('REVERT')=='1':
    n.inputs['From Min'].default_value=252.0; n.inputs['From Max'].default_value=246.0; print('SCT reverted')
else:
    n.inputs['From Min'].default_value=360.0; n.inputs['From Max'].default_value=354.0; print('SCT y1 -> 360')
if os.environ.get('SCSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

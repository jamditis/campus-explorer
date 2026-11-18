# Session eh (Oct 21 2026 ~9:35 PM ET): in the CCOM east oblique WIP the lawn 50-90 m from the camera fades to the 2020 ortho
# (2048 px), which reads grey-blue and blurry. Push the procedural-lawn -> ortho fade further out (FMIN/FMAX, default 60/170 m)
# and give the far ortho branch a mild saturation lift (SAT, default 1.25) so distant lawn stays green.
# Original values kept in material custom props eh_orig. SAVE=1 saves; REVERT=1 restores. Only affects Lawn_Varied_Oct_local_fade.
import bpy, os, json
m=bpy.data.materials['Lawn_Varied_Oct_local_fade']; nt=m.node_tree.nodes
mr=nt['Map Range.003']; hs=nt['Hue/Saturation/Value.002']
REV=os.environ.get('REVERT')=='1'; SAVE=os.environ.get('SAVE')=='1'
if REV:
    o=json.loads(m['eh_orig']); mr.inputs[1].default_value,mr.inputs[2].default_value,hs.inputs['Saturation'].default_value=o; del m['eh_orig']
else:
    if 'eh_orig' not in m: m['eh_orig']=json.dumps([mr.inputs[1].default_value,mr.inputs[2].default_value,hs.inputs['Saturation'].default_value])
    mr.inputs[1].default_value=float(os.environ.get('FMIN','60')); mr.inputs[2].default_value=float(os.environ.get('FMAX','170'))
    hs.inputs['Saturation'].default_value=float(os.environ.get('SAT','1.25'))
print('EH_FADE',mr.inputs[1].default_value,mr.inputs[2].default_value,hs.inputs['Saturation'].default_value)
if SAVE: bpy.ops.wm.save_mainfile(); print('EH_SAVED')

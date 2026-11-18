# qy: plaza paving read too white in every view (Q5). Darken QXP_plaza_scored_concrete_UNVERIFIED brick colours ~35%
# and darken the QY rim band so it reads as a separate edge course. Previous values kept in material props; REVERT=1 restores.
import bpy,os
m=bpy.data.materials['QXP_plaza_scored_concrete_UNVERIFIED']; br=[n for n in m.node_tree.nodes if n.type=='TEX_BRICK'][0]
K=('Color1','Color2','Mortar')
if os.environ.get('REVERT')=='1':
    if 'qy_prev' in m:
        for k,v in zip(K,m['qy_prev']): br.inputs[k].default_value=tuple(v)
        del m['qy_prev']
    print('QYT reverted')
else:
    if 'qy_prev' not in m: m['qy_prev']=[list(br.inputs[k].default_value) for k in K]
    new={'Color1':(0.165,0.16,0.148,1),'Color2':(0.19,0.185,0.17,1),'Mortar':(0.07,0.066,0.06,1)}
    for k in K: br.inputs[k].default_value=new[k]
    r=bpy.data.materials.get('QY_plaza_rim_band_concrete_UNVERIFIED')
    if r:
        cr=[n for n in r.node_tree.nodes if n.type=='VALTORGB'][0].color_ramp
        cr.elements[0].color=(0.10,0.097,0.09,1); cr.elements[1].color=(0.14,0.136,0.125,1)
    print('QYT applied')
if os.environ.get('QYSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

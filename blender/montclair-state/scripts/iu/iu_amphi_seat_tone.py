# Session iu (2026-10-25 ~4:25 PM ET): seat-top tone. Seats read pale/even from the top row.
# (1) overall seat tone x TONE (default 0.90), riser x 0.96; (2) fine granite speckle (noise scale ~140, +-6%) + micro bump;
# (3) grime band at the BACK of each seat (it_rowpos ~0.55..0.88, where the seat meets the next riser up and dirt/leaf litter
# collects), darkened ~18% with noise breakup. Nodes labelled iu_*; idempotent. Order: ip -> iq -> ir -> is -> it -> iu.
import bpy, os
TONE=float(os.environ.get('TONE',0.90)); GR=float(os.environ.get('GRIME',0.82))
for nm,tone,grime in [('hn_amphi_seat_stone_blocks',TONE,GR),('hn_amphi_riser_coursed_stone',0.96,None)]:
    m=bpy.data.materials[nm]; nt=m.node_tree; b=[q for q in nt.nodes if q.bl_idname=='ShaderNodeBsdfPrincipled'][0]
    old=[q for q in nt.nodes if q.label.startswith('iu_')]
    if old:
        first=[q for q in old if q.label=='iu_tone'][0]; nt.links.new(first.inputs[1].links[0].from_socket,b.inputs['Base Color'])
        bump=[q for q in old if q.label=='iu_bump']
        if bump and bump[0].inputs['Normal'].is_linked: nt.links.new(bump[0].inputs['Normal'].links[0].from_socket,b.inputs['Normal'])
        for q in old: nt.nodes.remove(q)
    src=b.inputs['Base Color'].links[0].from_socket
    def N(tp,lab): q=nt.nodes.new(tp); q.label=lab; return q
    t=N('ShaderNodeMixRGB','iu_tone'); t.blend_type='MULTIPLY'; t.inputs[0].default_value=1; t.inputs[2].default_value=(tone,tone*0.995,tone*0.985,1)
    nt.links.new(src,t.inputs[1]); cur=t.outputs[0]
    tc=N('ShaderNodeTexCoord','iu_tc')
    sp=N('ShaderNodeTexNoise','iu_speck'); sp.inputs['Scale'].default_value=140; sp.inputs['Detail'].default_value=2; nt.links.new(tc.outputs['Object'],sp.inputs['Vector'])
    sr=N('ShaderNodeMapRange','iu_speckr'); sr.inputs['From Min'].default_value=0.35; sr.inputs['From Max'].default_value=0.65; sr.inputs['To Min'].default_value=0.94; sr.inputs['To Max'].default_value=1.06
    nt.links.new(sp.outputs['Fac'],sr.inputs['Value'])
    sm=N('ShaderNodeMixRGB','iu_speckmul'); sm.blend_type='MULTIPLY'; sm.inputs[0].default_value=1; nt.links.new(cur,sm.inputs[1]); nt.links.new(sr.outputs[0],sm.inputs[2]); cur=sm.outputs[0]
    if grime:
        at=N('ShaderNodeAttribute','iu_attr'); at.attribute_name='it_rowpos'
        gb=N('ShaderNodeMapRange','iu_gband'); gb.inputs['From Min'].default_value=0.55; gb.inputs['From Max'].default_value=0.86; gb.inputs['To Min'].default_value=0; gb.inputs['To Max'].default_value=1; gb.clamp=True; gb.interpolation_type='SMOOTHSTEP'
        nt.links.new(at.outputs['Fac'],gb.inputs['Value'])
        gn=N('ShaderNodeTexNoise','iu_gnoise'); gn.inputs['Scale'].default_value=3.5; gn.inputs['Detail'].default_value=5; nt.links.new(tc.outputs['Object'],gn.inputs['Vector'])
        gm=N('ShaderNodeMapRange','iu_gnm'); gm.inputs['From Min'].default_value=0.35; gm.inputs['From Max'].default_value=0.65; gm.inputs['To Min'].default_value=0.4; gm.clamp=True
        nt.links.new(gn.outputs['Fac'],gm.inputs['Value'])
        mu=N('ShaderNodeMath','iu_gm'); mu.operation='MULTIPLY'; nt.links.new(gb.outputs[0],mu.inputs[0]); nt.links.new(gm.outputs[0],mu.inputs[1])
        gx=N('ShaderNodeMixRGB','iu_grime'); gx.blend_type='MULTIPLY'; gx.inputs[2].default_value=(grime,grime*0.97,grime*0.92,1)
        nt.links.new(mu.outputs[0],gx.inputs[0]); nt.links.new(cur,gx.inputs[1]); cur=gx.outputs[0]
    nt.links.new(cur,b.inputs['Base Color'])
    # micro bump chained before the existing brick bump
    if b.inputs['Normal'].is_linked:
        prev=b.inputs['Normal'].links[0].from_socket
        bp=N('ShaderNodeBump','iu_bump'); bp.inputs['Strength'].default_value=0.12; bp.inputs['Distance'].default_value=0.0005
        nt.links.new(sp.outputs['Fac'],bp.inputs['Height']); nt.links.new(prev,bp.inputs['Normal']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    print('IU done',nm)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('IU SAVED')

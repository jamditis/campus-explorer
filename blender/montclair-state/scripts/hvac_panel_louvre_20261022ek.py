# Session ek: the 27 rooftop HVAC boxes (object Roof_hvac, LiDAR/ortho placed) were one flat galvanised colour.
# New material ek_HVAC_galv_panels: 1.0 m vertical panel seams along each side (face-tangent coordinate),
# about half the panels (hash of panel id) get horizontal louvre slats (6 cm pitch, darker + bump), faint
# per-panel tint variation and streaking; tops get a 1.2 m seam grid. Typical unit cladding, NOT photo-checked.
# Original material kept (Roof_HVAC_galv_metal). SAVE=1 saves; REVERT=1 reassigns the original.
import bpy, os
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
o=bpy.data.objects['Roof_hvac']; ORIG='Roof_HVAC_galv_metal'; NEW='ek_HVAC_galv_panels'
if REVERT:
    o.data.materials[0]=bpy.data.materials[ORIG]; print('REVERTED')
else:
    m=bpy.data.materials.get(NEW)
    if m: bpy.data.materials.remove(m)
    m=bpy.data.materials.new(NEW); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; Lk=nt.links.new
    b=N['Principled BSDF']; b.inputs['Metallic'].default_value=0.55; b.inputs['Roughness'].default_value=0.46
    def n(t,**kw):
        x=N.new(t)
        for k,v in kw.items(): setattr(x,k,v)
        return x
    def vm(op,a=None,bb=None):
        x=n('ShaderNodeVectorMath',operation=op)
        if a is not None: Lk(a,x.inputs[0])
        if bb is not None:
            if isinstance(bb,tuple): x.inputs[1].default_value=bb
            else: Lk(bb,x.inputs[1])
        return x
    def mt(op,a=None,bb=None,clamp=False):
        x=n('ShaderNodeMath',operation=op); x.use_clamp=clamp
        for i,v in enumerate((a,bb)):
            if v is None: continue
            if isinstance(v,(int,float)): x.inputs[i].default_value=v
            else: Lk(v,x.inputs[i])
        return x
    g=n('ShaderNodeNewGeometry')
    nz=n('ShaderNodeSeparateXYZ'); Lk(g.outputs['Normal'],nz.inputs[0])
    side=mt('SUBTRACT',1.0,mt('ABSOLUTE',nz.outputs['Z']).outputs[0],clamp=True)   # 1 on sides
    side=mt('GREATER_THAN',side.outputs[0],0.5)
    T=vm('NORMALIZE',vm('CROSS_PRODUCT',g.outputs['Normal'],(0,0,1)).outputs[0])
    s=vm('DOT_PRODUCT',g.outputs['Position'],T.outputs[0])            # along-face coordinate
    pz=n('ShaderNodeSeparateXYZ'); Lk(g.outputs['Position'],pz.inputs[0])
    # panel seams: distance to nearest multiple of 1.0 m
    def seam(coord,pitch,w):
        f=mt('PINGPONG',mt('DIVIDE',coord,pitch).outputs[0],0.5)       # 0 at multiples
        return mt('LESS_THAN',f.outputs[0],w/pitch)
    sv=seam(s.outputs['Value'],1.0,0.012)
    pid=mt('FLOOR',mt('DIVIDE',s.outputs['Value'],1.0).outputs[0])
    wn=n('ShaderNodeTexWhiteNoise',noise_dimensions='1D'); Lk(pid.outputs[0],wn.inputs['W'])
    louv=mt('MULTIPLY',mt('GREATER_THAN',wn.outputs['Value'],0.5).outputs[0],side.outputs[0])
    slat=mt('PINGPONG',mt('DIVIDE',pz.outputs['Z'],0.06).outputs[0],0.5)   # 0..0.5 triangle
    slat_d=mt('MULTIPLY',louv.outputs[0],mt('LESS_THAN',slat.outputs[0],0.18).outputs[0])  # dark gaps
    # top grid seams
    top=mt('SUBTRACT',1.0,side.outputs[0])
    tx=seam(pz.outputs["X"],1.2,0.008); ty=seam(pz.outputs["Y"],1.2,0.008)
    tseam=mt('MULTIPLY',mt('MAXIMUM',tx.outputs[0],ty.outputs[0]).outputs[0],top.outputs[0])
    sseam=mt('MULTIPLY',sv.outputs[0],side.outputs[0])
    lines=mt('MAXIMUM',mt('MAXIMUM',sseam.outputs[0],tseam.outputs[0]).outputs[0],slat_d.outputs[0])
    # colour: base galv grey with per-panel tint + vertical streak noise; lines darker
    base=n('ShaderNodeMix',data_type='RGBA'); base.inputs['A'].default_value=(0.33,0.34,0.35,1); base.inputs['B'].default_value=(0.42,0.43,0.43,1)
    Lk(wn.outputs['Value'],base.inputs['Factor'])
    nn=n('ShaderNodeTexNoise'); nn.inputs['Scale'].default_value=1.5; nn.inputs['Detail'].default_value=6
    mp=n('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(4,4,0.4); Lk(g.outputs['Position'],mp.inputs['Vector']); Lk(mp.outputs[0],nn.inputs['Vector'])
    st=n('ShaderNodeMix',data_type='RGBA',blend_type='MULTIPLY'); st.inputs['Factor'].default_value=0.25
    Lk(base.outputs['Result'],st.inputs['A'])
    cr=n('ShaderNodeValToRGB'); Lk(nn.outputs['Fac'],cr.inputs['Fac']); cr.color_ramp.elements[0].position=0.35; cr.color_ramp.elements[0].color=(0.75,0.74,0.72,1); cr.color_ramp.elements[1].position=0.65
    Lk(cr.outputs['Color'],st.inputs['B'])
    dk=n('ShaderNodeMix',data_type='RGBA'); Lk(lines.outputs[0],dk.inputs['Factor']); Lk(st.outputs['Result'],dk.inputs['A']); dk.inputs['B'].default_value=(0.07,0.075,0.08,1)
    Lk(dk.outputs['Result'],b.inputs['Base Color'])
    bp=n('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.35; bp.inputs['Distance'].default_value=0.01
    Lk(mt('SUBTRACT',1.0,lines.outputs[0]).outputs[0],bp.inputs['Height']); Lk(bp.outputs['Normal'],b.inputs['Normal'])
    o.data.materials[0]=m; print('APPLIED',NEW,'faces',len(o.data.polygons))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

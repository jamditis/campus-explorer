# ws213a: WS76 white stall paint (Sprague N row, cogen rows) -> world-XY image mask in fn_lot_asphalt (ws211 pattern), chained after ws211_paint_white
import bpy, json
def _f213():
    m=bpy.data.materials['fn_lot_asphalt']; nt=m.node_tree; N=nt.nodes; L=nt.links
    if 'ws213_paint_white' in N: print('F213 already applied'); return
    TL=json.load(open('/workspace/nj-scenes/montclair-state/data/ws213_mask_tiles.json'))
    sep=N['ws211_sep']; bsdf=N['Principled BSDF']; pw=N['ws211_paint_white']
    CW=tuple(pw.inputs['B'].default_value)
    def lin(inp,a,b,nm):
        s=N.new('ShaderNodeMath'); s.name=nm; s.operation='MULTIPLY_ADD'; L.new(inp,s.inputs[0]); s.inputs[1].default_value=1/(b-a); s.inputs[2].default_value=-a/(b-a); return s
    acc=None
    for k,(nm,tx0,tx1,ty0,ty1) in enumerate(TL):
        img=bpy.data.images.get(nm) or bpy.data.images.load('/workspace/nj-scenes/montclair-state/data/'+nm); img.colorspace_settings.name='Non-Color'; img.pack()
        u=lin(sep.outputs['X'],tx0,tx1,'ws213_u%d'%k); v=lin(sep.outputs['Y'],ty0,ty1,'ws213_v%d'%k)
        cmb=N.new('ShaderNodeCombineXYZ'); cmb.name='ws213_uv%d'%k; L.new(u.outputs[0],cmb.inputs['X']); L.new(v.outputs[0],cmb.inputs['Y'])
        tex=N.new('ShaderNodeTexImage'); tex.name='ws213_mask%d'%k; tex.image=img; tex.extension='CLIP'; tex.interpolation='Linear'; L.new(cmb.outputs[0],tex.inputs['Vector'])
        if acc is None: acc=tex.outputs['Color']
        else:
            mm=N.new('ShaderNodeMix'); mm.name='ws213_max%d'%k; mm.data_type='RGBA'; mm.blend_type='LIGHTEN'; mm.inputs['Factor'].default_value=1.0
            L.new(acc,mm.inputs['A']); L.new(tex.outputs['Color'],mm.inputs['B']); acc=mm.outputs['Result']
    sc=N.new('ShaderNodeSeparateColor'); sc.name='ws213_msep'; L.new(acc,sc.inputs[0])
    r=N.new('ShaderNodeMapRange'); r.name='ws213_thr_r'; r.clamp=True; L.new(sc.outputs['Red'],r.inputs['Value']); r.inputs['From Min'].default_value=0.3; r.inputs['From Max'].default_value=0.7
    f=N.new('ShaderNodeMath'); f.name='ws213_fw'; f.operation='MULTIPLY'; L.new(r.outputs['Result'],f.inputs[0]); f.inputs[1].default_value=0.92
    mw=N.new('ShaderNodeMix'); mw.name='ws213_paint_white'; mw.data_type='RGBA'; mw.blend_type='MIX'
    L.new(f.outputs[0],mw.inputs['Factor']); L.new(pw.outputs['Result'],mw.inputs['A']); mw.inputs['B'].default_value=CW
    L.new(mw.outputs['Result'],bsdf.inputs['Base Color'])
    if 'ws211_pmax' in N and 'ws211_paint_rough' in N:
        pm=N['ws211_pmax']; mx=N.new('ShaderNodeMath'); mx.name='ws213_pmax'; mx.operation='MAXIMUM'
        L.new(pm.outputs[0],mx.inputs[0]); L.new(r.outputs['Result'],mx.inputs[1]); L.new(mx.outputs[0],N['ws211_paint_rough'].inputs['Factor'])
    print('F213 white mask applied tiles',len(TL),'white',[round(c,3) for c in CW],flush=True)
_f213(); del _f213

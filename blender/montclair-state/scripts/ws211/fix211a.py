# ws211a: accessible-lot (WS76 rows A/B) paint -> planar world-XY image mask inside fn_lot_asphalt (flush by construction).
# slight wear: paint coverage 0.9 (old asphalt shows through a little)
# roughness: paint a touch smoother
import bpy
def _f211():
    MASK='/workspace/nj-scenes/montclair-state/data/ws211_access_lot_paint_mask.png'
    X0,X1,Y0,Y1=-256.0,-214.0,-88.0,-62.0
    m=bpy.data.materials['fn_lot_asphalt']; nt=m.node_tree; N=nt.nodes; L=nt.links
    if 'ws211_paint_white' in N: print('F211 already applied'); return
    def col(mn,fb):
        pm=bpy.data.materials.get(mn)
        try: return tuple(pm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value)
        except Exception: return fb
    CB=col('WS76_paint_blue_accessible',(0.02,0.12,0.45,1)); CW=col('WS76_paint_white_faded',(0.75,0.75,0.72,1))
    import json
    TL=json.load(open(globals().get('TILEJSON','/workspace/nj-scenes/montclair-state/data/ws211_mask_tiles.json')))
    geo=N.new('ShaderNodeNewGeometry'); geo.name='ws211_geo'
    sep=N.new('ShaderNodeSeparateXYZ'); sep.name='ws211_sep'; L.new(geo.outputs['Position'],sep.inputs[0])
    def lin(inp,a,b,nm):
        s=N.new('ShaderNodeMath'); s.name=nm; s.operation='MULTIPLY_ADD'; L.new(inp,s.inputs[0]); s.inputs[1].default_value=1/(b-a); s.inputs[2].default_value=-a/(b-a); return s
    acc=None
    for k,(nm,tx0,tx1,ty0,ty1) in enumerate(TL):
        img=bpy.data.images.get(nm) or bpy.data.images.load('/workspace/nj-scenes/montclair-state/data/'+nm); img.colorspace_settings.name='Non-Color'; img.pack()
        u=lin(sep.outputs['X'],tx0,tx1,'ws211_u%d'%k); v=lin(sep.outputs['Y'],ty0,ty1,'ws211_v%d'%k)
        cmb=N.new('ShaderNodeCombineXYZ'); cmb.name='ws211_uv%d'%k; L.new(u.outputs[0],cmb.inputs['X']); L.new(v.outputs[0],cmb.inputs['Y'])
        tex=N.new('ShaderNodeTexImage'); tex.name='ws211_mask%d'%k; tex.image=img; tex.extension='CLIP'; tex.interpolation='Linear'; L.new(cmb.outputs[0],tex.inputs['Vector'])
        if acc is None: acc=tex.outputs['Color']
        else:
            mm=N.new('ShaderNodeMix'); mm.name='ws211_max%d'%k; mm.data_type='RGBA'; mm.blend_type='LIGHTEN'; mm.inputs['Factor'].default_value=1.0
            L.new(acc,mm.inputs['A']); L.new(tex.outputs['Color'],mm.inputs['B']); acc=mm.outputs['Result']
    bsdf=N['Principled BSDF']; dk=N['WS75_darken']
    sc=N.new('ShaderNodeSeparateColor'); sc.name='ws211_msep'; L.new(acc,sc.inputs[0])
    def mul(inp,k,nm):
        s=N.new('ShaderNodeMath'); s.name=nm; s.operation='MULTIPLY'; L.new(inp,s.inputs[0]); s.inputs[1].default_value=k; return s
    def thr(inp,nm):
        r=N.new('ShaderNodeMapRange'); r.name=nm; r.clamp=True; L.new(inp,r.inputs['Value']); r.inputs['From Min'].default_value=0.3; r.inputs['From Max'].default_value=0.7; return r
    tg=thr(sc.outputs['Green'],'ws211_thr_g'); tr=thr(sc.outputs['Red'],'ws211_thr_r')
    fb=mul(tg.outputs['Result'],0.9,'ws211_fb'); fw=mul(tr.outputs['Result'],0.92,'ws211_fw')
    src=dk.outputs[0]
    mb=N.new('ShaderNodeMix'); mb.name='ws211_paint_blue'; mb.data_type='RGBA'; mb.blend_type='MIX'
    L.new(fb.outputs[0],mb.inputs['Factor']); L.new(src,mb.inputs['A']); mb.inputs['B'].default_value=CB
    mw=N.new('ShaderNodeMix'); mw.name='ws211_paint_white'; mw.data_type='RGBA'; mw.blend_type='MIX'
    L.new(fw.outputs[0],mw.inputs['Factor']); L.new(mb.outputs['Result'],mw.inputs['A']); mw.inputs['B'].default_value=CW
    L.new(mw.outputs['Result'],bsdf.inputs['Base Color'])
    mx=N.new('ShaderNodeMath'); mx.name='ws211_pmax'; mx.operation='MAXIMUM'; L.new(tr.outputs['Result'],mx.inputs[0]); L.new(tg.outputs['Result'],mx.inputs[1])
    rl=bsdf.inputs['Roughness'].links
    if rl:
        rsrc=rl[0].from_socket
        mr=N.new('ShaderNodeMix'); mr.name='ws211_paint_rough'; mr.data_type='FLOAT'
        L.new(mx.outputs[0],mr.inputs['Factor']); L.new(rsrc,mr.inputs['A']); mr.inputs['B'].default_value=0.6; L.new(mr.outputs['Result'],bsdf.inputs['Roughness'])
    print('F211 mask material applied; blue',[round(c,3) for c in CB],'white',[round(c,3) for c in CW],flush=True)
_f211()
del _f211

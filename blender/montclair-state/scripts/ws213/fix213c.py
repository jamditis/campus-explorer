# ws213c: zebra walkway (WS76) + lot-entrance crosswalk bars (WS204) -> world-XY mask in fn_lot_asphalt and KY_college_ave_asphalt_UNVERIFIED; then delete the draped objects
import bpy, json
def _add(matname,col,rough=0.6):
    m=bpy.data.materials[matname]; N=m.node_tree.nodes; L=m.node_tree.links
    if 'ws213z_paint' in N: print('F213 z already',matname); return
    TL=json.load(open('/workspace/nj-scenes/montclair-state/data/ws213z_mask_tiles.json'))
    bsdf=[n for n in N if n.type=='BSDF_PRINCIPLED'][0]
    geo=N.new('ShaderNodeNewGeometry'); geo.name='ws213z_geo'; sep=N.new('ShaderNodeSeparateXYZ'); sep.name='ws213z_sep'; L.new(geo.outputs['Position'],sep.inputs[0])
    def lin(inp,a,b,nm):
        s=N.new('ShaderNodeMath'); s.name=nm; s.operation='MULTIPLY_ADD'; L.new(inp,s.inputs[0]); s.inputs[1].default_value=1/(b-a); s.inputs[2].default_value=-a/(b-a); return s
    acc=None
    for k,(nm,tx0,tx1,ty0,ty1) in enumerate(TL):
        img=bpy.data.images.get(nm) or bpy.data.images.load('/workspace/nj-scenes/montclair-state/data/'+nm); img.colorspace_settings.name='Non-Color'
        if not img.packed_file: img.pack()
        u=lin(sep.outputs['X'],tx0,tx1,'ws213z_u%d'%k); v=lin(sep.outputs['Y'],ty0,ty1,'ws213z_v%d'%k)
        cmb=N.new('ShaderNodeCombineXYZ'); cmb.name='ws213z_uv%d'%k; L.new(u.outputs[0],cmb.inputs['X']); L.new(v.outputs[0],cmb.inputs['Y'])
        tex=N.new('ShaderNodeTexImage'); tex.name='ws213z_mask%d'%k; tex.image=img; tex.extension='CLIP'; tex.interpolation='Linear'; L.new(cmb.outputs[0],tex.inputs['Vector'])
        if acc is None: acc=tex.outputs['Color']
        else:
            mm=N.new('ShaderNodeMix'); mm.name='ws213z_max%d'%k; mm.data_type='RGBA'; mm.blend_type='LIGHTEN'; mm.inputs['Factor'].default_value=1.0
            L.new(acc,mm.inputs['A']); L.new(tex.outputs['Color'],mm.inputs['B']); acc=mm.outputs['Result']
    sc=N.new('ShaderNodeSeparateColor'); sc.name='ws213z_msep'; L.new(acc,sc.inputs[0])
    r=N.new('ShaderNodeMapRange'); r.name='ws213z_thr'; r.clamp=True; L.new(sc.outputs['Red'],r.inputs['Value']); r.inputs['From Min'].default_value=0.3; r.inputs['From Max'].default_value=0.7
    f=N.new('ShaderNodeMath'); f.name='ws213z_f'; f.operation='MULTIPLY'; L.new(r.outputs['Result'],f.inputs[0]); f.inputs[1].default_value=0.92
    bl=bsdf.inputs['Base Color'].links
    mw=N.new('ShaderNodeMix'); mw.name='ws213z_paint'; mw.data_type='RGBA'; mw.blend_type='MIX'; L.new(f.outputs[0],mw.inputs['Factor'])
    if bl: L.new(bl[0].from_socket,mw.inputs['A'])
    else: mw.inputs['A'].default_value=bsdf.inputs['Base Color'].default_value
    mw.inputs['B'].default_value=col; L.new(mw.outputs['Result'],bsdf.inputs['Base Color'])
    rl=bsdf.inputs['Roughness'].links; mr=N.new('ShaderNodeMix'); mr.name='ws213z_rough'; mr.data_type='FLOAT'; L.new(r.outputs['Result'],mr.inputs['Factor'])
    if rl: L.new(rl[0].from_socket,mr.inputs['A'])
    else: mr.inputs['A'].default_value=bsdf.inputs['Roughness'].default_value
    mr.inputs['B'].default_value=rough; L.new(mr.outputs['Result'],bsdf.inputs['Roughness'])
    print('F213 z mask ->',matname,[round(c,3) for c in col],flush=True)
def _col(mn,fb):
    pm=bpy.data.materials.get(mn)
    try: return tuple([n for n in pm.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0].inputs['Base Color'].default_value)
    except Exception: return fb
CWZ=_col('WS76_paint_white_faded',(0.58,0.58,0.54,1)); CEY=_col('ey_crosswalk_paint',CWZ)
_add('fn_lot_asphalt',CWZ); _add('KY_college_ave_asphalt_UNVERIFIED',CEY)
for n in ('WS76_lot_zebra_walkway_paint_ortho2020_UNVERIFIED','WS204_lot_entrance_crosswalk_paint_ortho2020_UNVERIFIED_bars'):
    o=bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o); print('F213 deleted',n,flush=True)

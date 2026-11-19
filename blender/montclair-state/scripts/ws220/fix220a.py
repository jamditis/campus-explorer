# ws220: SF_Lot38 draped stall stripes (faces were flipped, normals down) -> world-XY paint mask in SF_asphalt_worn_UNVERIFIED (Joe 9:41 AM paint-mask decision); draped object deleted.
import bpy, json
TL=json.load(open('/workspace/nj-scenes/montclair-state/data/ws220_mask_tiles.json'))
m=bpy.data.materials['SF_asphalt_worn_UNVERIFIED']; N=m.node_tree.nodes; L=m.node_tree.links
if 'ws220p_geo' in N: raise SystemExit('F220A already')
bsdf=[n for n in N if n.type=='BSDF_PRINCIPLED'][0]
geo=N.new('ShaderNodeNewGeometry'); geo.name='ws220p_geo'; xyz=N.new('ShaderNodeSeparateXYZ'); xyz.name='ws220p_sep'; L.new(geo.outputs['Position'],xyz.inputs[0])
def lin(inp,a,b,nm):
    s=N.new('ShaderNodeMath'); s.name=nm; s.operation='MULTIPLY_ADD'; L.new(inp,s.inputs[0]); s.inputs[1].default_value=1/(b-a); s.inputs[2].default_value=-a/(b-a); return s
for key in ('c',):
    T=[t for t in TL if t[0]==key]
    if not T: continue
    acc=None; col=tuple(T[0][7])
    for k,(_,fn,x0,x1,y0,y1,nm,c) in enumerate(T):
        img=bpy.data.images.get(fn) or bpy.data.images.load('/workspace/nj-scenes/montclair-state/data/'+fn); img.colorspace_settings.name='Non-Color'
        if not img.packed_file: img.pack()
        u=lin(xyz.outputs['X'],x0,x1,'ws220p%s_u%d'%(key,k)); v=lin(xyz.outputs['Y'],y0,y1,'ws220p%s_v%d'%(key,k))
        cmb=N.new('ShaderNodeCombineXYZ'); L.new(u.outputs[0],cmb.inputs['X']); L.new(v.outputs[0],cmb.inputs['Y'])
        tex=N.new('ShaderNodeTexImage'); tex.name='ws220p%s_mask%d'%(key,k); tex.image=img; tex.extension='CLIP'; tex.interpolation='Linear'; L.new(cmb.outputs[0],tex.inputs['Vector'])
        if acc is None: acc=tex.outputs['Color']
        else:
            mm=N.new('ShaderNodeMix'); mm.data_type='RGBA'; mm.blend_type='LIGHTEN'; mm.inputs['Factor'].default_value=1.0
            L.new(acc,mm.inputs['A']); L.new(tex.outputs['Color'],mm.inputs['B']); acc=mm.outputs['Result']
    sc=N.new('ShaderNodeSeparateColor'); L.new(acc,sc.inputs[0])
    r=N.new('ShaderNodeMapRange'); r.clamp=True; L.new(sc.outputs['Red'],r.inputs['Value']); r.inputs['From Min'].default_value=0.3; r.inputs['From Max'].default_value=0.7
    f=N.new('ShaderNodeMath'); f.operation='MULTIPLY'; L.new(r.outputs['Result'],f.inputs[0]); f.inputs[1].default_value=0.85
    bl=bsdf.inputs['Base Color'].links
    mw=N.new('ShaderNodeMix'); mw.name='ws220p%s_paint'%key; mw.data_type='RGBA'; mw.blend_type='MIX'; L.new(f.outputs[0],mw.inputs['Factor'])
    if bl: L.new(bl[0].from_socket,mw.inputs['A'])
    else: mw.inputs['A'].default_value=bsdf.inputs['Base Color'].default_value
    mw.inputs['B'].default_value=col; L.new(mw.outputs['Result'],bsdf.inputs['Base Color'])
    rl=bsdf.inputs['Roughness'].links; mr=N.new('ShaderNodeMix'); mr.data_type='FLOAT'; L.new(r.outputs['Result'],mr.inputs['Factor'])
    if rl: L.new(rl[0].from_socket,mr.inputs['A'])
    else: mr.inputs['A'].default_value=bsdf.inputs['Roughness'].default_value
    mr.inputs['B'].default_value=0.6; L.new(mr.outputs['Result'],bsdf.inputs['Roughness'])
    print('F220A chain',key,len(T),'tiles colour',[round(x,2) for x in col],flush=True)
for t in TL:
    o=bpy.data.objects.get(t[6])
    if o: me=o.data; bpy.data.objects.remove(o); print('F220A deleted',t[6][:50],flush=True)

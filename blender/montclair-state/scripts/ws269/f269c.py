# ws269c (Codex review on PR #103, AGENTS.md rule 7): the ws269a paint strips become a world-XY paint mask in the paving's asphalt.
# The WS268 paving gets its own copy of the Roads_OSM material (so other roads are untouched); mask tiles data/ws269_mask_tiles.json
# (mkmask269.py, 3 cm/px, packed) mixed into Base Color (paint colour = es_rhd_stall_paint_worn) and Roughness; the strip object is deleted.
import bpy, json
TAG='F269C'; OB=bpy.data.objects
pav=OB['WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED']
src=pav.data.materials[0]
if src.name.startswith('WS269_'): raise SystemExit('F269C already applied')
m=src.copy(); m.name='WS269_CollegeAve_Lot33_asphalt_painted'; pav.data.materials[0]=m
N=m.node_tree.nodes; L=m.node_tree.links
bsdf=[n for n in N if n.type=='BSDF_PRINCIPLED'][0]
def _col(mn,fb):
    pm=bpy.data.materials.get(mn)
    try: return tuple([n for n in pm.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0].inputs['Base Color'].default_value)
    except Exception: return fb
CW=_col('es_rhd_stall_paint_worn',(0.62,0.62,0.58,1))
TL=json.load(open('/workspace/nj-scenes/montclair-state/data/ws269_mask_tiles.json'))
geo=N.new('ShaderNodeNewGeometry'); geo.name='ws269_geo'; sep=N.new('ShaderNodeSeparateXYZ'); sep.name='ws269_sep'; L.new(geo.outputs['Position'],sep.inputs[0])
def lin(inp,a,b,nm):
    s=N.new('ShaderNodeMath'); s.name=nm; s.operation='MULTIPLY_ADD'; L.new(inp,s.inputs[0]); s.inputs[1].default_value=1/(b-a); s.inputs[2].default_value=-a/(b-a); return s
acc=None
for k,(nm,tx0,tx1,ty0,ty1) in enumerate(TL):
    img=bpy.data.images.get(nm) or bpy.data.images.load('//data/'+nm); img.colorspace_settings.name='Non-Color'
    if not img.packed_file: img.pack()
    u=lin(sep.outputs['X'],tx0,tx1,'ws269_u%d'%k); v=lin(sep.outputs['Y'],ty0,ty1,'ws269_v%d'%k)
    cmb=N.new('ShaderNodeCombineXYZ'); cmb.name='ws269_uv%d'%k; L.new(u.outputs[0],cmb.inputs['X']); L.new(v.outputs[0],cmb.inputs['Y'])
    tex=N.new('ShaderNodeTexImage'); tex.name='ws269_mask%d'%k; tex.image=img; tex.extension='CLIP'; tex.interpolation='Linear'; L.new(cmb.outputs[0],tex.inputs['Vector'])
    if acc is None: acc=tex.outputs['Color']
    else:
        mm=N.new('ShaderNodeMix'); mm.name='ws269_max%d'%k; mm.data_type='RGBA'; mm.blend_type='LIGHTEN'; mm.inputs['Factor'].default_value=1.0
        L.new(acc,mm.inputs['A']); L.new(tex.outputs['Color'],mm.inputs['B']); acc=mm.outputs['Result']
sc=N.new('ShaderNodeSeparateColor'); sc.name='ws269_msep'; L.new(acc,sc.inputs[0])
r=N.new('ShaderNodeMapRange'); r.name='ws269_thr'; r.clamp=True; L.new(sc.outputs['Red'],r.inputs['Value']); r.inputs['From Min'].default_value=0.25; r.inputs['From Max'].default_value=0.75
f=N.new('ShaderNodeMath'); f.name='ws269_f'; f.operation='MULTIPLY'; L.new(r.outputs['Result'],f.inputs[0]); f.inputs[1].default_value=0.9
bl=bsdf.inputs['Base Color'].links
mw=N.new('ShaderNodeMix'); mw.name='ws269_paint'; mw.data_type='RGBA'; mw.blend_type='MIX'; L.new(f.outputs[0],mw.inputs['Factor'])
if bl: L.new(bl[0].from_socket,mw.inputs['A'])
else: mw.inputs['A'].default_value=bsdf.inputs['Base Color'].default_value
mw.inputs['B'].default_value=CW; L.new(mw.outputs['Result'],bsdf.inputs['Base Color'])
rl=bsdf.inputs['Roughness'].links; mr=N.new('ShaderNodeMix'); mr.name='ws269_rough'; mr.data_type='FLOAT'; L.new(r.outputs['Result'],mr.inputs['Factor'])
if rl: L.new(rl[0].from_socket,mr.inputs['A'])
else: mr.inputs['A'].default_value=bsdf.inputs['Roughness'].default_value
mr.inputs['B'].default_value=0.6; L.new(mr.outputs['Result'],bsdf.inputs['Roughness'])
print(TAG,'material',src.name,'->',m.name,'paint',[round(c,3) for c in CW],'tiles',len(TL),'base-colour linked',bool(bl),flush=True)
o=OB.get('WS269_W72b_CollegeAve_Lot33_paint_ortho2020_UNVERIFIED')
if o: me=o.data; OB.remove(o); bpy.data.meshes.remove(me); print(TAG,'deleted paint strips',flush=True)

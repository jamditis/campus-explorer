# ws274b (merge208 CHAIN, on ws274a): rebuild the N curb/gutter with f274a v2 (straight smoothed line, curb cut at the police S walk end,
# College Ave curb material WS27_curb_concrete_UNVERIFIED instead of the tan OQ paving tone), give the ws269 island curb the same
# material, and paint the turn arrow + yellow hatch into the WS269 asphalt mask (mkmask274.py tiles; AGENTS.md rule 7).
import bpy, json
TAG='F274B'; OB=bpy.data.objects
for n in ('WS274_CollegeAve_N_curb_ortho2020_UNVERIFIED','WS274_CollegeAve_N_gutter_pan_UNVERIFIED'):
    o=OB.get(n)
    if o: me=o.data; OB.remove(o); bpy.data.meshes.remove(me)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws274/f274a.py').read())
cm=bpy.data.materials.get('WS27_curb_concrete_UNVERIFIED')
ic=OB.get('WS269_W72b_Lot33_tree_island_curb_ortho2020_UNVERIFIED')
if ic and cm: ic.data.materials[0]=cm; print(TAG,'island curb ->',cm.name,flush=True)
m=bpy.data.materials['WS269_CollegeAve_Lot33_asphalt_painted']; N=m.node_tree.nodes; L=m.node_tree.links
T=json.load(open('/workspace/nj-scenes/montclair-state/data/ws274_mask_tiles.json'))
for nm,tx0,tx1,ty0,ty1,old in T['white']:
    img=bpy.data.images.load('//data/'+nm); img.colorspace_settings.name='Non-Color'; img.pack()
    k=0
    for nd in N:
        if nd.type=='TEX_IMAGE' and nd.image and nd.image.name.startswith(old): nd.image=img; k+=1
    print(TAG,'white tile',old,'->',nm,'nodes',k,flush=True)
if 'ws274_yel_tex' not in N:
    nm,tx0,tx1,ty0,ty1=T['yellow'][0]
    img=bpy.data.images.load('//data/'+nm); img.colorspace_settings.name='Non-Color'; img.pack()
    sep=N['ws269_sep']
    def lin(inp,a,b,nn):
        s=N.new('ShaderNodeMath'); s.name=nn; s.operation='MULTIPLY_ADD'; L.new(inp,s.inputs[0]); s.inputs[1].default_value=1/(b-a); s.inputs[2].default_value=-a/(b-a); return s
    u=lin(sep.outputs['X'],tx0,tx1,'ws274_u'); v=lin(sep.outputs['Y'],ty0,ty1,'ws274_v')
    cmb=N.new('ShaderNodeCombineXYZ'); cmb.name='ws274_uv'; L.new(u.outputs[0],cmb.inputs['X']); L.new(v.outputs[0],cmb.inputs['Y'])
    tex=N.new('ShaderNodeTexImage'); tex.name='ws274_yel_tex'; tex.image=img; tex.extension='CLIP'; tex.interpolation='Linear'; L.new(cmb.outputs[0],tex.inputs['Vector'])
    sc=N.new('ShaderNodeSeparateColor'); sc.name='ws274_ysep'; L.new(tex.outputs['Color'],sc.inputs[0])
    r=N.new('ShaderNodeMapRange'); r.name='ws274_ythr'; r.clamp=True; L.new(sc.outputs['Red'],r.inputs['Value']); r.inputs['From Min'].default_value=0.25; r.inputs['From Max'].default_value=0.75
    f=N.new('ShaderNodeMath'); f.name='ws274_yf'; f.operation='MULTIPLY'; L.new(r.outputs['Result'],f.inputs[0]); f.inputs[1].default_value=0.85
    bsdf=[n for n in N if n.type=='BSDF_PRINCIPLED'][0]
    pw=N['ws269_paint']; my=N.new('ShaderNodeMix'); my.name='ws274_yellow'; my.data_type='RGBA'; my.blend_type='MIX'
    L.new(f.outputs[0],my.inputs['Factor']); L.new(pw.outputs['Result'],my.inputs['A']); my.inputs['B'].default_value=(0.50,0.40,0.09,1.0)
    L.new(my.outputs['Result'],bsdf.inputs['Base Color'])
    pr=N['ws269_rough']; mr=N.new('ShaderNodeMix'); mr.name='ws274_yrough'; mr.data_type='FLOAT'; L.new(r.outputs['Result'],mr.inputs['Factor'])
    L.new(pr.outputs['Result'],mr.inputs['A']); mr.inputs['B'].default_value=0.6; L.new(mr.outputs['Result'],bsdf.inputs['Roughness'])
    print(TAG,'yellow hatch mask added',nm,flush=True)

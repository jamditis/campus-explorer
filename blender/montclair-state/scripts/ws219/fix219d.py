# ws219 draped paint -> mask: the RHD SE College Ave crosswalk (ey_rhd_se_crosswalks, 6 draped slabs that read as thick,
# tilted plates at eye level) becomes part of the world-XY paint mask already in KY_college_ave_asphalt_UNVERIFIED
# (ws213z chain, ey_crosswalk_paint colour). New tile LIGHTEN-merged into the chain; the draped object is deleted.
import bpy, json
m=bpy.data.materials['KY_college_ave_asphalt_UNVERIFIED']; N=m.node_tree.nodes; L=m.node_tree.links
if 'ws219z_mask0' in N: raise SystemExit('F219D already')
sep=N['ws213z_msep']; src=sep.inputs[0].links[0].from_socket
geo=N['ws213z_geo']; xyz=N['ws213z_sep']
def lin(inp,a,b,nm):
    s=N.new('ShaderNodeMath'); s.name=nm; s.operation='MULTIPLY_ADD'; L.new(inp,s.inputs[0]); s.inputs[1].default_value=1/(b-a); s.inputs[2].default_value=-a/(b-a); return s
for k,(nm,tx0,tx1,ty0,ty1) in enumerate(json.load(open('/workspace/nj-scenes/montclair-state/data/ws219z_mask_tiles.json'))):
    img=bpy.data.images.get(nm) or bpy.data.images.load('/workspace/nj-scenes/montclair-state/data/'+nm); img.colorspace_settings.name='Non-Color'
    if not img.packed_file: img.pack()
    u=lin(xyz.outputs['X'],tx0,tx1,'ws219z_u%d'%k); v=lin(xyz.outputs['Y'],ty0,ty1,'ws219z_v%d'%k)
    cmb=N.new('ShaderNodeCombineXYZ'); cmb.name='ws219z_uv%d'%k; L.new(u.outputs[0],cmb.inputs['X']); L.new(v.outputs[0],cmb.inputs['Y'])
    tex=N.new('ShaderNodeTexImage'); tex.name='ws219z_mask%d'%k; tex.image=img; tex.extension='CLIP'; tex.interpolation='Linear'; L.new(cmb.outputs[0],tex.inputs['Vector'])
    mm=N.new('ShaderNodeMix'); mm.name='ws219z_max%d'%k; mm.data_type='RGBA'; mm.blend_type='LIGHTEN'; mm.inputs['Factor'].default_value=1.0
    L.new(src,mm.inputs['A']); L.new(tex.outputs['Color'],mm.inputs['B']); src=mm.outputs['Result']
L.new(src,sep.inputs[0])
o=bpy.data.objects['ey_rhd_se_crosswalks']; me=o.data; bpy.data.objects.remove(o)
if me.users==0: bpy.data.meshes.remove(me)
print('F219D mask chained, ey_rhd_se_crosswalks deleted',flush=True)

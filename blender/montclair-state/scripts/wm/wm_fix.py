"""wm: leaf-litter continues off the LiDAR patches onto the coarse 3DEP skirt where OSM wood + 2017 LiDAR canopy continue
(south of the WJ ext, west of it, round the ravine). One packed world-XY mask image (data/wm/wm_litter_mask.png) now drives
litter in both the patch material and a skirt-local material copy, so the patch W/S edges no longer fade to a lawn halo.
Shared OW2 skirt material untouched (its other users QW/RZ2 unchanged)."""
import bpy, os, json
rep={}
IMG='/workspace/nj-scenes/montclair-state/data/wm/wm_litter_mask.png'
X0,Y0,SX,SY=120.,215.,200.,205.
old=bpy.data.images.get('WM_litter_mask')
if old: bpy.data.images.remove(old)
im=bpy.data.images.load(IMG); im.name='WM_litter_mask'
im.colorspace_settings.name='Non-Color'
if not im.packed_file: im.pack()
def mask_nodes(nt,pref):
    N=nt.nodes; L=nt.links
    g=N.new('ShaderNodeNewGeometry'); g.name=pref+'geo'
    mp=N.new('ShaderNodeMapping'); mp.name=pref+'map'; mp.vector_type='POINT'
    mp.inputs['Location'].default_value=(-X0/SX,-Y0/SY,0); mp.inputs['Scale'].default_value=(1/SX,1/SY,0)
    L.new(g.outputs['Position'],mp.inputs['Vector'])
    t=N.new('ShaderNodeTexImage'); t.name=pref+'mask'; t.image=im; t.extension='CLIP'; t.interpolation='Cubic'
    L.new(mp.outputs['Vector'],t.inputs['Vector']); return t
# 1) patch material: WK factor from the image instead of the per-vertex (edge-faded) wk_litter
pm=bpy.data.materials['WH_east_dorm_patch_tone_UNVERIFIED']; N=pm.node_tree.nodes; L=pm.node_tree.links
for n in [x for x in N if x.name.startswith('WM_')]: N.remove(n)
t=mask_nodes(pm.node_tree,'WM_')
fm=N['WK_fac_mr']
for l in list(fm.inputs['Value'].links): L.remove(l)
L.new(t.outputs['Color'],fm.inputs['Value'])
pm['wm_mat']=1
# 2) skirt-local copy with the same WK litter nodes
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; base=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']
old=bpy.data.materials.get('WM_skirt_litter_UNVERIFIED')
if old: old.name='WM_skirt_litter_OLD'
sm=base.copy(); sm.name='WM_skirt_litter_UNVERIFIED'
if old:
    for s_ in sk.material_slots:
        if s_.material==old: s_.material=sm
    bpy.data.materials.remove(old)
N=sm.node_tree.nodes; L=sm.node_tree.links
for n in [x for x in N if x.name.startswith(('WM_','WK_'))]: N.remove(n)
t=mask_nodes(sm.node_tree,'WM_')
src=N['Mix']; hz=N['EP_haze_mix']; hzin=[i for i in hz.inputs if i.is_linked and i.links[0].from_node==src][0]; srcout=hzin.links[0].from_socket
tc=N['EP_tc']; P=N['Principled BSDF']; pmN=pm.node_tree.nodes
def cp(name,typ):
    n=N.new(typ); n.name=name; o=pmN[name]
    for a in ('operation','interpolation_type','feature','data_type','use_clamp'):
        if hasattr(o,a): 
            try: setattr(n,a,getattr(o,a))
            except Exception: pass
    for i,(a,b) in enumerate(zip(o.inputs,n.inputs)):
        if hasattr(a,'default_value') and not a.is_linked:
            try: b.default_value=a.default_value
            except Exception: pass
    return n
n1=cp('WK_leaf_noise','ShaderNodeTexNoise'); n2=cp('WK_leaf_fine','ShaderNodeTexNoise')
L.new(tc.outputs['Object'],n1.inputs['Vector']); L.new(tc.outputs['Object'],n2.inputs['Vector'])
cr=N.new('ShaderNodeValToRGB'); cr.name='WK_litter_ramp'; oe=pmN['WK_litter_ramp'].color_ramp.elements; e=cr.color_ramp.elements
while len(e)<len(oe): e.new(0.5)
for a,b in zip(oe,e): b.position=a.position; b.color=a.color
mx=cp('WK_noise_mix','ShaderNodeMath'); f2=cp('WK_fine_w','ShaderNodeMath')
L.new(n1.outputs['Fac'],mx.inputs[0]); L.new(n2.outputs['Fac'],f2.inputs[0]); L.new(f2.outputs[0],mx.inputs[2])
fm=cp('WK_fac_mr','ShaderNodeMapRange'); L.new(t.outputs['Color'],fm.inputs['Value'])
fb=cp('WK_fac_break','ShaderNodeMath'); L.new(n1.outputs['Fac'],fb.inputs[0])
ff=cp('WK_fac','ShaderNodeMath'); L.new(fm.outputs['Result'],ff.inputs[0]); L.new(fb.outputs[0],ff.inputs[1])
mix=N.new('ShaderNodeMix'); mix.name='WK_litter_mix'; mix.data_type='RGBA'
L.new(ff.outputs[0],mix.inputs[0]); L.new(srcout,mix.inputs[6]); L.new(cr.outputs['Color'],mix.inputs[7]); L.new(mix.outputs[2],hzin)
v=cp('WK_vor','ShaderNodeTexVoronoi'); L.new(tc.outputs['Object'],v.inputs['Vector'])
vt=cp('WK_vor_tone','ShaderNodeMath'); L.new(v.outputs['Distance'],vt.inputs[0]); L.new(mx.outputs[0],vt.inputs[2]); L.new(vt.outputs[0],cr.inputs['Fac'])
h=cp('WK_bump_h','ShaderNodeMath'); L.new(v.outputs['Distance'],h.inputs[0]); L.new(ff.outputs[0],h.inputs[1])
b=cp('WK_bump','ShaderNodeBump'); nin=P.inputs['Normal'].links[0].from_socket
L.new(h.outputs[0],b.inputs['Height']); L.new(nin,b.inputs['Normal']); L.new(b.outputs['Normal'],P.inputs['Normal'])
rep['skirt_rough_linked']=P.inputs['Roughness'].is_linked
if not P.inputs['Roughness'].is_linked:
    rr=N.new('ShaderNodeMapRange'); rr.name='WK_rough'; L.new(ff.outputs[0],rr.inputs['Value'])
    rr.inputs['To Min'].default_value=P.inputs['Roughness'].default_value; rr.inputs['To Max'].default_value=0.95; L.new(rr.outputs['Result'],P.inputs['Roughness'])
sm['wm_mat']=1; sm['UNVERIFIED_wm']='wm: skirt-local copy of OW2 + wk leaf-litter nodes driven by WM_litter_mask (OSM wood + 2017 LiDAR canopy); colours UNVERIFIED'
# assign to skirt faces whose centre lies in the mask box (+12 m)
me=sk.data
if sm.name not in [s.material.name for s in sk.material_slots if s.material]: me.materials.append(sm)
si=[i for i,s in enumerate(sk.material_slots) if s.material==sm][0]
n=0
for p in me.polygons:
    c=p.center
    if X0-12<c.x<X0+SX+12 and Y0-12<c.y<Y0+SY+12: p.material_index=si; n+=1
rep['skirt_faces_assigned']=n; rep['slot']=si
sk['wm_obj']=1
# evaluated check: material indices survive the GN/boolean stack
dg=bpy.context.evaluated_depsgraph_get(); ev=sk.evaluated_get(dg).to_mesh()
rep['eval_faces_slot']=sum(1 for p in ev.polygons if p.material_index==si); rep['eval_faces']=len(ev.polygons)
sk.evaluated_get(dg).to_mesh_clear()
json.dump(rep,open('/workspace/nj-scenes/montclair-state/data/wm/fix_report.json','w'),indent=1); print('REP',rep)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

"""tag 20261022ep (RERUNNABLE, SAVE=1 env or --save; REVERT=1 removes). The 3DEP/NJ ortho context skirt (4 km square,
Context_skirt_ortho, 1k leaf-off ortho ~3.9 m/px) read as streaky grey water from CCOM's east lounge window:
at grazing view angles the 0.12 specular picked up a sky sheen and the leaf-off roofs/roads smeared into grey streaks.
Material-only change to Context_skirt_ortho (1 user):
 - specular 0.12 -> 0 and roughness 0.95 -> 1.0 (no sky sheen at grazing angles);
 - grazing-angle canopy: in real suburbs seen side-on from a ridge, street-tree crowns hide most roofs and roads,
   so where |N.I| is small (grazing) the ortho colour is mixed toward clumped canopy greens/olives
   (Noise on Object coords, ~14 m clumps, 2-colour variation); top-down/aerial views keep the ortho;
 - aerial-perspective haze by camera View Distance (same curve as eo carpet: 0 at 400 m -> 0.60 at 5.5 km);
 - small clump bump. All UNVERIFIED artistic; ortho data/positions untouched."""
import bpy, os, sys
SAVE=("--save" in sys.argv) or os.environ.get("SAVE")=="1"; REVERT=os.environ.get("REVERT")=="1"
mat=bpy.data.materials["Context_skirt_ortho"]; nt=mat.node_tree; N=nt.nodes; L=nt.links
b=next(n for n in N if n.type=='BSDF_PRINCIPLED'); src=N["ah_leafon"]
for n in [n for n in N if n.name.startswith("EP_")]: N.remove(n)
L.new(src.outputs[2],b.inputs['Base Color'])
for l in list(b.inputs['Normal'].links): L.remove(l)
if "ep_orig_spec" in mat:
    b.inputs['Specular IOR Level'].default_value=mat["ep_orig_spec"]; b.inputs['Roughness'].default_value=mat["ep_orig_rough"]
if not REVERT:
    mat["ep_orig_spec"]=b.inputs['Specular IOR Level'].default_value; mat["ep_orig_rough"]=b.inputs['Roughness'].default_value
    b.inputs['Specular IOR Level'].default_value=0.0; b.inputs['Roughness'].default_value=1.0
    def nn(t,name): n=N.new(t); n.name="EP_"+name; return n
    geo=nn('ShaderNodeNewGeometry','geo')
    dot=nn('ShaderNodeVectorMath','dot'); dot.operation='DOT_PRODUCT'
    L.new(geo.outputs['Normal'],dot.inputs[0]); L.new(geo.outputs['Incoming'],dot.inputs[1])
    ab=nn('ShaderNodeMath','abs'); ab.operation='ABSOLUTE'; L.new(dot.outputs['Value'],ab.inputs[0])
    gz=nn('ShaderNodeMapRange','graze'); gz.interpolation_type='SMOOTHSTEP'
    gz.inputs['From Min'].default_value=float(os.environ.get("EP_G0","0.32")); gz.inputs['From Max'].default_value=float(os.environ.get("EP_G1","0.06"))
    gz.inputs['To Min'].default_value=0.0; gz.inputs['To Max'].default_value=float(os.environ.get("EP_COVER","0.85"))
    L.new(ab.outputs[0],gz.inputs['Value'])
    tc=nn('ShaderNodeTexCoord','tc')
    nz=nn('ShaderNodeTexNoise','clump'); nz.inputs['Scale'].default_value=0.07; nz.inputs['Detail'].default_value=4.0; nz.inputs['Roughness'].default_value=0.6
    L.new(tc.outputs['Object'],nz.inputs['Vector'])
    rp=nn('ShaderNodeMapRange','clump_mr'); rp.interpolation_type='SMOOTHSTEP'
    rp.inputs['From Min'].default_value=0.40; rp.inputs['From Max'].default_value=0.56
    L.new(nz.outputs['Fac'],rp.inputs['Value'])
    nz2=nn('ShaderNodeTexNoise','tint'); nz2.inputs['Scale'].default_value=0.012; nz2.inputs['Detail'].default_value=2.0
    L.new(tc.outputs['Object'],nz2.inputs['Vector'])
    cc=nn('ShaderNodeMix','canopy_col'); cc.data_type='RGBA'
    L.new(nz2.outputs['Fac'],cc.inputs['Factor'])
    cc.inputs[6].default_value=(0.055,0.085,0.035,1.0); cc.inputs[7].default_value=(0.15,0.14,0.055,1.0)
    # coverage = graze * (0.35 + 0.65*clump) so clumps read but gaps aren't bare
    cm=nn('ShaderNodeMapRange','clump_cov'); cm.inputs['To Min'].default_value=0.35; cm.inputs['To Max'].default_value=1.0
    L.new(rp.outputs[0],cm.inputs['Value'])
    cov=nn('ShaderNodeMath','cov'); cov.operation='MULTIPLY'; L.new(gz.outputs[0],cov.inputs[0]); L.new(cm.outputs[0],cov.inputs[1])
    mx=nn('ShaderNodeMix','canopy_mix'); mx.data_type='RGBA'
    L.new(cov.outputs[0],mx.inputs['Factor']); L.new(src.outputs[2],mx.inputs[6]); L.new(cc.outputs[2],mx.inputs[7])
    cam=nn('ShaderNodeCameraData','cam')
    hz=nn('ShaderNodeMapRange','haze_mr'); hz.interpolation_type='SMOOTHSTEP'
    hz.inputs['From Min'].default_value=400.0; hz.inputs['From Max'].default_value=5500.0; hz.inputs['To Max'].default_value=0.60
    L.new(cam.outputs['View Distance'],hz.inputs['Value'])
    hm=nn('ShaderNodeMix','haze_mix'); hm.data_type='RGBA'
    L.new(hz.outputs[0],hm.inputs['Factor']); L.new(mx.outputs[2],hm.inputs[6]); hm.inputs[7].default_value=(0.40,0.46,0.52,1.0)
    L.new(hm.outputs[2],b.inputs['Base Color'])
    bh=nn('ShaderNodeMath','bump_h'); bh.operation='MULTIPLY'; L.new(rp.outputs[0],bh.inputs[0]); L.new(gz.outputs[0],bh.inputs[1])
    bp=nn('ShaderNodeBump','bump'); bp.inputs['Strength'].default_value=0.35; bp.inputs['Distance'].default_value=4.0
    L.new(bh.outputs[0],bp.inputs['Height']); L.new(bp.outputs['Normal'],b.inputs['Normal'])
    mat["ep_grazing_canopy"]="no spec + grazing-angle clumped canopy + distance haze, 20261022ep (UNVERIFIED artistic)"
else:
    for k in ("ep_grazing_canopy","ep_orig_spec","ep_orig_rough"):
        if k in mat: del mat[k]
print("EP_MAT","reverted" if REVERT else "ok","users",mat.users,"spec",b.inputs['Specular IOR Level'].default_value)
if SAVE: bpy.ops.wm.save_mainfile(); print("SAVED")

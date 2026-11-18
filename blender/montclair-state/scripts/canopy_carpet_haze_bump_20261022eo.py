"""tag 20261022eo (RERUNNABLE, SAVE=1 env or --save; REVERT=1 removes). Far canopy carpet (ai/bl, 450 m-8 km) seen through
CCOM's east lounge window read as a field of bright, faceted green balls at eye level.
Material-only change to MID_canopy_carpet_leaf_ai (used only by the carpet crown protos):
 - aerial perspective: base colour mixed toward a pale blue-grey haze by camera View Distance
   (0 at 400 m -> 0.60 at 5.5 km, smoothstep), so the carpet recedes like real distant woodland;
 - leaf-clump bump (Noise on instance Object coords, scale 2.2, detail 5) to break the low-poly facets.
Season (summer vs October) unchanged - still Joe's call. Positions/sizes untouched. All UNVERIFIED artistic."""
import bpy, os, sys
SAVE=("--save" in sys.argv) or os.environ.get("SAVE")=="1"; REVERT=os.environ.get("REVERT")=="1"
mat=bpy.data.materials["MID_canopy_carpet_leaf_ai"]; nt=mat.node_tree; N=nt.nodes; L=nt.links
b=next(n for n in N if n.type=='BSDF_PRINCIPLED'); hsv=N["BL_hsv"]
for n in [n for n in N if n.name.startswith("EO_")]: N.remove(n)
L.new(hsv.outputs['Color'],b.inputs['Base Color'])
for l in list(b.inputs['Normal'].links): L.remove(l)
if not REVERT:
    cam=N.new('ShaderNodeCameraData'); cam.name="EO_cam"
    mr=N.new('ShaderNodeMapRange'); mr.name="EO_haze_mr"; mr.interpolation_type='SMOOTHSTEP'
    mr.inputs['From Min'].default_value=400.0; mr.inputs['From Max'].default_value=5500.0
    mr.inputs['To Min'].default_value=0.0; mr.inputs['To Max'].default_value=0.60
    L.new(cam.outputs['View Distance'],mr.inputs['Value'])
    mx=N.new('ShaderNodeMix'); mx.name="EO_haze_mix"; mx.data_type='RGBA'
    L.new(mr.outputs[0],mx.inputs['Factor']); L.new(hsv.outputs['Color'],mx.inputs[6])
    mx.inputs[7].default_value=(0.40,0.46,0.52,1.0)
    L.new(mx.outputs[2],b.inputs['Base Color'])
    tc=N.new('ShaderNodeTexCoord'); tc.name="EO_tc"
    nz=N.new('ShaderNodeTexNoise'); nz.name="EO_noise"; nz.inputs['Scale'].default_value=2.2; nz.inputs['Detail'].default_value=5.0; nz.inputs['Roughness'].default_value=0.62
    L.new(tc.outputs['Object'],nz.inputs['Vector'])
    bp=N.new('ShaderNodeBump'); bp.name="EO_bump"; bp.inputs['Strength'].default_value=0.55; bp.inputs['Distance'].default_value=0.4
    L.new(nz.outputs['Fac'],bp.inputs['Height']); L.new(bp.outputs['Normal'],b.inputs['Normal'])
    mat["eo_haze_bump"]="aerial-perspective haze by view distance + leaf-clump bump, 20261022eo (UNVERIFIED artistic)"
else:
    if "eo_haze_bump" in mat: del mat["eo_haze_bump"]
print("EO_MAT", "reverted" if REVERT else "ok", "users", mat.users)
if SAVE: bpy.ops.wm.save_mainfile(); print("SAVED")

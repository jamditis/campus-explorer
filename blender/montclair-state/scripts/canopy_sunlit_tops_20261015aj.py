"""tag 20261015aj (RERUNNABLE, --save). Sunlit-top tint on the canopy carpet leaf material: upward-facing
crown faces blend up to 35% toward a warm sunlit olive, so the carpet reads less flat/dark vs Joe's lab-window
photo. Shading-only approximation; colour season (summer vs October) still open for Joe."""
import bpy, sys
SAVE = "--save" in sys.argv
m = bpy.data.materials["MID_canopy_carpet_leaf_ai"]; nt = m.node_tree; N = nt.nodes; L = nt.links
for n in [n for n in N if n.name.startswith("AJ_")]: N.remove(n)
b = next(n for n in N if n.type == "BSDF_PRINCIPLED")
lk = b.inputs["Base Color"].links
src = lk[0].from_socket if lk else None
geo = N.new("ShaderNodeNewGeometry"); geo.name = "AJ_geo"
sep = N.new("ShaderNodeSeparateXYZ"); sep.name = "AJ_sep"
mr = N.new("ShaderNodeMapRange"); mr.name = "AJ_map"
mr.inputs["From Min"].default_value = 0.35; mr.inputs["From Max"].default_value = 0.95
mr.inputs["To Min"].default_value = 0.0; mr.inputs["To Max"].default_value = 0.35
mx = N.new("ShaderNodeMix"); mx.name = "AJ_mix"; mx.data_type = "RGBA"; mx.blend_type = "MIX"
mx.inputs[7].default_value = (0.30, 0.38, 0.11, 1.0)  # B: sunlit olive (linear)
L.new(geo.outputs["Normal"], sep.inputs[0]); L.new(sep.outputs["Z"], mr.inputs["Value"])
L.new(mr.outputs["Result"], mx.inputs["Factor"])
if src: L.new(src, mx.inputs[6])
else: mx.inputs[6].default_value = b.inputs["Base Color"].default_value
L.new(mx.outputs[2], b.inputs["Base Color"])
print("SUNLIT_TOPS ok src", src.node.name if src else None)
if SAVE: bpy.ops.wm.save_mainfile(); print("SAVED")

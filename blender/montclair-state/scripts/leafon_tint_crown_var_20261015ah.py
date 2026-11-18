"""tag 20261015ah step 5 (RERUNNABLE, --save).
(a) Skirt ortho (data/skirt_ortho_1k.jpg) is LEAF-OFF imagery (grey-brown); the scene is October leaf-on.
    Add a mild leaf-on multiply tint after the HSV node (olive (0.62,0.80,0.50), fac 0.30). Approximation, UNVERIFIED tone.
(b) Street-tree crowns: per-instance colour variation via Object Info Random -> 3-stop ramp of olive/green
    variants (still within the ac neon-fix range). Shared material, no new meshes."""
import bpy, sys
m = bpy.data.materials["Context_skirt_ortho"]; nt = m.node_tree; L = nt.links
hsv = nt.nodes["Hue/Saturation/Value"]
bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
if "ah_leafon" in nt.nodes: nt.nodes.remove(nt.nodes["ah_leafon"])
mix = nt.nodes.new("ShaderNodeMix"); mix.name = "ah_leafon"; mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
mix.inputs["Factor"].default_value = 0.30
mix.inputs[7].default_value = (0.62, 0.80, 0.50, 1.0)  # B colour
L.new(hsv.outputs["Color"], mix.inputs[6])
L.new(mix.outputs[2], bsdf.inputs["Base Color"])
m["ah_leafon"] = "multiply (0.62,0.80,0.50) fac 0.30"
cm = bpy.data.materials["MID_street_tree_olive_20261015ag"]; ct = cm.node_tree
cb = next(n for n in ct.nodes if n.type == "BSDF_PRINCIPLED")
for nm in ("ah_oi", "ah_ramp"):
    if nm in ct.nodes: ct.nodes.remove(ct.nodes[nm])
oi = ct.nodes.new("ShaderNodeObjectInfo"); oi.name = "ah_oi"
rp = ct.nodes.new("ShaderNodeValToRGB"); rp.name = "ah_ramp"
e = rp.color_ramp.elements
e[0].position = 0.0; e[0].color = (0.040, 0.075, 0.032, 1)
e[1].position = 1.0; e[1].color = (0.075, 0.095, 0.040, 1)
mid = e.new(0.55); mid.color = (0.050, 0.090, 0.045, 1)
ct.links.new(oi.outputs["Random"], rp.inputs["Fac"])
ct.links.new(rp.outputs["Color"], cb.inputs["Base Color"])
print("leafon + crown var linked", flush=True)
if "--save" in sys.argv:
    bpy.ops.wm.save_mainfile(); print("SAVED step5", flush=True)

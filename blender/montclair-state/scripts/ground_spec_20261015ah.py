"""tag 20261015ah step 3: eye-level ground read pale blue-white even after the tone ramp -> grazing-angle
specular sky reflection on the ortho ground (Principled Specular IOR Level 0.5 default, rough 0.95).
Grass/soil is low-spec: skirt 0.5 -> 0.12, farfield 0.5 -> 0.20. Node values only (non-destructive)."""
import bpy
for mn, lv in (("Context_skirt_ortho", 0.12), ("BD_farfield_ortho_haze", 0.20)):
    m = bpy.data.materials[mn]
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    print("SPEC", mn, b.inputs["Specular IOR Level"].default_value, "->", lv)
    m["ah_spec_prev"] = b.inputs["Specular IOR Level"].default_value
    b.inputs["Specular IOR Level"].default_value = lv
bpy.ops.wm.save_mainfile(); print("SAVED spec")

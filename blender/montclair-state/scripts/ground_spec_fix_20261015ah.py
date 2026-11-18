"""ah step 4: farfield Specular IOR Level was already 0.0 (step 3 wrongly set 0.2) -> restore 0.0. Skirt stays 0.12."""
import bpy
m = bpy.data.materials["BD_farfield_ortho_haze"]
b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
b.inputs["Specular IOR Level"].default_value = 0.0
m["ah_spec_prev"] = 0.0
bpy.ops.wm.save_mainfile(); print("SAVED farfield spec 0.0")

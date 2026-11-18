"""tag 20261015aj: darken the inner skirt ortho (r <= 800 m start of the ah ramp) V 0.85 -> 0.72 so the
leaf-off ortho between carpet crowns stops reading snow-pale in close views. Node value only. --save to write."""
import bpy, sys
m = bpy.data.materials["Context_skirt_ortho"]; nt = m.node_tree
n = nt.nodes["ah_mrV"]; print("before", n.inputs["From Min"].default_value, n.inputs["From Max"].default_value, n.inputs["To Min"].default_value, n.inputs["To Max"].default_value)
n.inputs["To Min"].default_value = 0.72
m["aj_tone"] = "r 800->1600 m: V 0.72->0.42 (aj; was 0.85->0.42)"
print("SKIRT_TONE aj set")
if "--save" in sys.argv: bpy.ops.wm.save_mainfile(); print("SAVED")

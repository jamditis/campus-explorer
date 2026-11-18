import bpy
nt=bpy.data.materials["Context_skirt_ortho"].node_tree
nt.nodes["ah_mrV"].inputs["To Max"].default_value=0.42
nt.nodes["ah_mrS"].inputs["To Max"].default_value=1.22
bpy.data.materials["Context_skirt_ortho"]["ah_tone"]="r 800->1600 m: V 0.85->0.42, S 1.0->1.22 (ah2)"
bpy.ops.wm.save_mainfile(); print("SAVED tone2")

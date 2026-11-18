"""tag 20261014ad: flat-roof membrane read near-white under sun in close-up -> modestly darker greys (RERUNNABLE, saves)."""
import bpy
cr = bpy.data.materials["HouseProxy_FlatRoof_membrane_20261014ad"].node_tree.nodes["AD_ramp"].color_ramp
for e, c in zip(cr.elements, [(0.17,0.17,0.17),(0.24,0.24,0.23),(0.13,0.13,0.14),(0.30,0.29,0.28),(0.16,0.15,0.14),(0.21,0.20,0.19)]):
    e.color = c + (1.0,)
print("MEMBRANE darker"); bpy.ops.wm.save_mainfile(); print("SAVED")

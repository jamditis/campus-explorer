"""tag 20261015ae self-review fix (RERUNNABLE, --save): first ae WIPs showed the house proxies as near-white boxes
under the clear-sky sun (siding 0.42-0.58, roofs rendering pale). Darker, slightly more varied NJ suburban palettes on
the shared _20261014ad proto materials (affects ad + ae houses). Colours UNVERIFIED (plausible, not surveyed)."""
import bpy, sys
P = {
 "HouseProxy_Siding_Tan_20261014ad": [(0.42,0.37,0.28),(0.50,0.48,0.43),(0.34,0.33,0.29),(0.46,0.40,0.31),(0.36,0.38,0.40),(0.40,0.36,0.24),(0.30,0.34,0.27)],
 "HouseProxy_Siding_Grey_20261014ad": [(0.28,0.30,0.33),(0.44,0.45,0.44),(0.25,0.30,0.33),(0.48,0.47,0.44),(0.32,0.30,0.27),(0.33,0.38,0.43),(0.30,0.34,0.27)],
 "HouseProxy_Roof_Asphalt_20261014ad": [(0.06,0.06,0.07),(0.10,0.09,0.09),(0.13,0.09,0.06),(0.08,0.07,0.065),(0.12,0.12,0.13),(0.10,0.06,0.05)],
 "HouseProxy_Roof_Brown_20261014ad": [(0.13,0.09,0.06),(0.08,0.07,0.065),(0.12,0.12,0.13),(0.10,0.06,0.05),(0.06,0.06,0.07),(0.10,0.09,0.09)],
}
for mn, pal in P.items():
    m = bpy.data.materials[mn]; cr = m.node_tree.nodes["AD_ramp"].color_ramp
    els = cr.elements
    while len(els) > 1: els.remove(els[-1])
    els[0].position = 0.0; els[0].color = pal[0] + (1.0,)
    for i, c in enumerate(pal[1:], 1):
        e = els.new(i / len(pal)); e.color = c + (1.0,)
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"); b.inputs["Roughness"].default_value = 0.9
    print("TONE", mn, len(pal))
t = bpy.data.materials["HouseProxy_Trim_White_20261014ad"]
next(n for n in t.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.58, 0.58, 0.55, 1.0)
if "--save" in sys.argv: bpy.ops.wm.save_mainfile(); print("SAVED")

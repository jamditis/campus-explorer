# ws240 self-review: with f240a's metallic 0.35 the near-black bar still rendered tan/brown in the RHD SE close-up (probe240g:
# the hit IS the bar with WS240_clearance_bar_dark_steel) — the metallic share mirrors the warm sunlit soffit/sky. Painted
# steel is a dielectric: metallic 0, roughness 0.6, base stays near-black.
import bpy
m=bpy.data.materials['WS240_clearance_bar_dark_steel']; b=m.node_tree.nodes['Principled BSDF']
b.inputs['Metallic'].default_value=0.0; b.inputs['Roughness'].default_value=0.6
if 'Specular IOR Level' in b.inputs: b.inputs['Specular IOR Level'].default_value=0.3
print('F240D bar material dielectric',flush=True)

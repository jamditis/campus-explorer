# ws203 W13e: the remaining wavy dark line across the W-eye foreground is FACET shading on the coarse (0.9 m, staggered-row) WS163 S-drive
# mesh: flat-shaded triangles change slope 7 % -> 5 % along a zig-zag of the staggered rows. Designer call: a draped asphalt drive is a smooth
# surface -> smooth-shade the drive (geometry unchanged).
import bpy
o=[x for x in bpy.data.objects if x.name.startswith('WS163_Lot3_aisle_S_drive')][0]
n0=sum(p.use_smooth for p in o.data.polygons)
for p in o.data.polygons: p.use_smooth=True
o.data.update(); print('F203e drive smooth was',n0,'/',len(o.data.polygons),'now all; mods',[m.type for m in o.modifiers],flush=True)

# ws207 W28: faint light/dark tone patch where the ws206 CCOM walk edge strip (WS206_CCOM_walk_E_edge_straight_fill...) meets
# Footpaths_OSM at the walk bend (~(11.9,-45.6)). Both use Paving_concrete, whose texture runs on OBJECT coordinates, and the
# strip was smooth-shaded while the walk is flat-shaded. Fix: give the strip the walk's object transform (world geometry kept,
# so the concrete noise/joints line up across the joint) and flat shading like the walk.
import bpy
def ob(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
STRP=ob('WS206_CCOM_walk_E_edge_straight_fill'); FP=ob('Footpaths_OSM')
print('F207d strip origin',tuple(round(c,3) for c in STRP.matrix_world.translation),'walk origin',tuple(round(c,3) for c in FP.matrix_world.translation),flush=True)
M=FP.matrix_world.inverted()@STRP.matrix_world
STRP.data.transform(M); STRP.matrix_world=FP.matrix_world.copy()
for p in STRP.data.polygons: p.use_smooth=False
STRP.data.update(); print('F207d strip re-based to walk transform, flat shaded',len(STRP.data.polygons),flush=True)

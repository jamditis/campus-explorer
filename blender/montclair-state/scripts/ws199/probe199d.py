import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
N=['WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS94_lot_slit_filler_asphalt_UNVERIFIED','WS76_lot_stall_paint_blue_accessible_ortho2020_UNVERIFIED','WS196_lot_accessible_ISA_symbol_paint_UNVERIFIED','WS81_lot_seam_underlay_asphalt']
T={}
for n in N:
    o=bpy.data.objects[n]; mw=o.matrix_world
    T[n]=BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
AS=BVHTree.FromPolygons(*(lambda V,F:(V,F))([],[]))
def z(t,x,y):
    h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else None
for cx,cy in ((-237.8,-80.7),):
  print('P199 square',cx,cy)
  for y in np.arange(cy-1.4,cy+1.41,0.2):
    row=[]
    for x in np.arange(cx-1.4,cx+1.41,0.2):
      za=max([q for q in (z(T[n],x,y) for n in N[:3]) if q is not None] or [np.nan])
      zb=z(T[N[3]],x,y); zi=z(T[N[4]],x,y); zu=z(T[N[5]],x,y)
      row.append('%+.0f/%s/%s'%((za-126)*1000 if za==za else -999, '%+.0f'%((zb-za)*1000) if zb else '.', '%+.0f'%((zi-za)*1000) if zi else '.'))
    print('P199 y%.1f '%y+' '.join(row),flush=True)

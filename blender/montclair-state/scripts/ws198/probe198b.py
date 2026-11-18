import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
AS=['WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS94_lot_slit_filler_asphalt_UNVERIFIED']
V=[];F=[]
for n in AS:
    o=bpy.data.objects[n]; mw=o.matrix_world; b=len(V)
    V+=[mw@v.co for v in o.data.vertices]; F+=[tuple(b+i for i in p.vertices) for p in o.data.polygons]
T=BVHTree.FromPolygons(V,F)
def zt(x,y):
    h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else None
out=[]
for x in np.arange(-244,-210,0.5):
  for y in np.arange(-90,-66,0.25):
    a=zt(x,y); b=zt(x,y+0.25); c=zt(x+0.5,y)
    if a and b and abs(b-a)>0.05: out.append((round(abs(b-a),3),x,y,'dy'))
    if a and c and abs(c-a)>0.06: out.append((round(abs(c-a),3),x,y,'dx'))
out.sort(reverse=True); print('P198b n',len(out),out[:25],flush=True)

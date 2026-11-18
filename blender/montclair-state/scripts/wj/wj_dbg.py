import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
O=bpy.data.objects; sc=bpy.context.scene
c=O['WE_CAM_closeup_stone_footway_junction_from_SE']; print('CAM',tuple(round(x,1) for x in c.location))
img=bpy.data.images['WJ_verge_mask']; W,H=img.size; px=np.array(img.pixels[:]).reshape(H,W,4)
# raycast through image centre rows of camera to ground
names=[o.name for o in O if o.type=='MESH' and o.name.startswith(('WV_','QS_footway_5466','QS_service_5466','QT_soil_edge_5466','WT_','RZ2_'))]
B={}
for n in names:
    o=O[n]; m=o.matrix_world; B[n]=BVHTree.FromPolygons([m@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
fr=c.data.view_frame(scene=sc); M=c.matrix_world
for fy in (0.25,0.4,0.55):
  for fx in (0.2,0.5,0.8):
    p=fr[2].lerp(fr[1],fx); q=fr[3].lerp(fr[0],fx); pt=p.lerp(q,fy)  # rough
    d=(M@pt-M.translation).normalized(); best=None
    for n,b in B.items():
        h=b.ray_cast(M.translation,d,500)
        if h[0] is not None and (best is None or h[3]<best[3]): best=(h[0],n,0,h[3])
    if best:
        x,y=best[0].x,best[0].y; i=int((x-116)/0.1); j=int((y-246)/0.1)
        val=px[j,i,:2] if 0<=i<W and 0<=j<H else None
        print('RAY',fx,fy,round(x,1),round(y,1),best[1][:30],val)

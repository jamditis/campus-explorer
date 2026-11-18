import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=bpy.data.objects['WS3_Cole_plaza_paving_20261109']
wv=[W.matrix_world@v.co for v in W.data.vertices]
WB=BVHTree.FromPolygons(wv,[list(f.vertices) for f in W.data.polygons])
def wz(x,y):
  h=WB.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else None
sx=-119.3
ys=[-50.6-i*0.05 for i in range(120)]
edge=next(y for y in ys if wz(sx,y) is not None)  # north edge of the Cole walk (first hit going south from the bed)
ez=wz(sx,edge-0.1)
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
sign=bpy.data.objects['WS4_Sign_Wayfinding_ColeHall_UNVERIFIED_POS']
sy=edge+0.75
# ground: scene ray (terrain/lawn) at the sign foot
dg=bpy.context.evaluated_depsgraph_get()
ok,loc,nor,idx,ob,mx=bpy.context.scene.ray_cast(dg,Vector((sx,sy,200)),Vector((0,0,-1)))
gz=loc.z if ok else ez-0.05
print('edge',round(edge,2),'walk z',round(ez,3),'ground hit',ob.name if ok else None,round(gz,3))
sign.location=(sx,sy,gz-0.10); sign.rotation_euler.z=-math.pi/2
print('SIGN',[round(v,2) for v in sign.location])
c=bpy.data.objects['WS5_CAM_closeup_cole_sign_on_east_walk']; c.name='WS5_CAM_closeup_cole_sign_from_W'
loc=Vector((-127.0,-52.6,ez+1.65)); tgt=Vector((sx,sy,gz+1.25))
c.location=loc; c.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); c.data.lens=30
bpy.ops.wm.save_mainfile(); print('SAVED')

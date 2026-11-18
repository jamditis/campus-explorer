import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=bpy.data.objects['WS3_Cole_plaza_paving_20261109']
wv=[W.matrix_world@v.co for v in W.data.vertices]
WB=BVHTree.FromPolygons(wv,[list(f.vertices) for f in W.data.polygons])
def wz(x,y):
  h=WB.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else None
for sx in (-95.0,-93.3,-91.0,-88.0):
  row=''.join('#' if wz(sx,-48-i*0.25) is not None else '.' for i in range(60))
  print('ROW',sx,row)
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
BED=bpy.data.objects['COLE_planting_beds_smooth_bu']; bv=[BED.matrix_world@v.co for v in BED.data.vertices]
BB2=BVHTree.FromPolygons(bv,[list(f.vertices) for f in BED.data.polygons])
sign=bpy.data.objects['WS4_Sign_Wayfinding_ColeHall_UNVERIFIED_POS']
sx,sy=-93.3,-58.85
h=BB2.ray_cast(Vector((sx,sy,300)),Vector((0,0,-1)))
print('bed hit',h[0])
gz=h[0].z if h[0] else None
w=wz(sx,-57.9); print('walk z',w)
if gz is None: gz=w-0.03
sign.location=(sx,sy,gz-0.10); sign.rotation_euler.z=-math.pi/2
print('SIGN',[round(x,2) for x in sign.location], sign.instance_type, sign.instance_collection.name if sign.instance_collection else None)
bpy.ops.wm.save_mainfile(); print('SAVED')

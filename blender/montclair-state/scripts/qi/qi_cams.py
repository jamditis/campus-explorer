# qi cameras for the east-edge re-grid WIPs. REVERT=1 removes them.
import bpy, os, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'
NAMES=['QI_CAM_oblique_east_edge_from_SW','QI_CAM_eye_east_edge_road_north','QI_CAM_eye_east_edge_from_NE','QI_CAM_closeup_east_edge_road_drape']
for n in NAMES:
    o=bpy.data.objects.get(n)
    if o: cd=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.cameras.remove(cd)
if not REV:
    dg=bpy.context.evaluated_depsgraph_get(); T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; bt=BVHTree.FromObject(T,dg)
    def g(x,y): return bt.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0].z
    R=bpy.data.objects['Roads_OSM'].evaluated_get(dg); M=R.matrix_world
    rv=[M@v.co for v in R.data.vertices]; rv=[v for v in rv if 170<=v.x<=215 and 10<=v.y<=90]
    rv.sort(key=lambda v:(v.y)); road=rv[len(rv)//3] if rv else Vector((190,40,g(190,40)))
    print('ROADPT',tuple(round(c,1) for c in road),len(rv))
    def cam(n,loc,tgt,lens):
        cd=bpy.data.cameras.new(n); cd.lens=lens; cd.clip_end=6000; o=bpy.data.objects.new(n,cd); bpy.context.scene.collection.objects.link(o)
        o.location=loc; d=Vector(tgt)-Vector(loc); o.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); o['qi']=1; return o
    cam(NAMES[0],(95,-110,g(95,-110)+110),(195,105,g(195,105)),30)
    x,y=road.x,road.y
    # eye camera moved at 11:34 AM (first spot was inside a tree crown): road vertex clear of tree bboxes, looking NNE downslope
    b=Vector((177.8772,111.0043,107.8213)); cam(NAMES[1],tuple(b),(b.x+25,b.y+60,b.z-6),28)
    cam(NAMES[2],(205,215,g(205,215)+1.7),(150,110,g(150,110)+1.0),28)
    cam(NAMES[3],(x-6,y-5,g(x-6,y-5)+2.4),(x+2,y+6,g(x+2,y+6)),35)
    print('QI cams added')

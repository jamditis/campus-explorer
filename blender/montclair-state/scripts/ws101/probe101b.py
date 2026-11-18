import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['Roads_OSM','Footpaths_OSM','UA_CollegeAve_spur_1557427669_UNVERIFIED','WS27_CollegeAve_carriageway_2020ortho','WS27_CollegeAve_curb_left_UNVERIFIED','WS27_CollegeAve_curb_right_UNVERIFIED','Terrain_LiDAR_DTM_1m']
with bpy.data.libraries.load(p) as (s,d): d.objects=names
sc=bpy.context.scene
for o in d.objects: sc.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); B=[]
for o in d.objects:
    e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); B.append((o.name,BVHTree.FromBMesh(bm))); bm.free(); e.to_mesh_clear()
TT=dict(B)['Terrain_LiDAR_DTM_1m']
def gz(x,y): return TT.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0].z
cd=bpy.data.cameras.new('c'); cam=bpy.data.objects.new('c',cd); sc.collection.objects.link(cam); sc.camera=cam; cd.lens=28
sc.render.resolution_x=1280; sc.render.resolution_y=720
loc=Vector((-217.5,-178,gz(-217.5,-178)+1.6)); tgt=Vector((-207,-112,gz(-207,-112)+0.6)); cam.location=loc
cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); bpy.context.view_layer.update()
fr=cd.view_frame(scene=sc); M=cam.matrix_world; TR,BR,BL,TL=[M@v for v in fr]
for lab,(u,v) in {'olive':(380/704,290/396),'olive2':(330/704,260/396),'darkleft':(150/704,320/396),'joint':(330/704,228/396)}.items():
    pt=TL.lerp(TR,u).lerp(BL.lerp(BR,u),v); dv=(pt-M.translation).normalized(); hits=[]
    for n,t in B:
        h=t.ray_cast(M.translation,dv,400)
        if h[0] is not None: hits.append((round(h[3],1),n[:45],tuple(round(c,2) for c in h[0])))
    hits.sort(); print('Q101',lab,hits[:3])

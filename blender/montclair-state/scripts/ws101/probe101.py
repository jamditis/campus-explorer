import bpy, json, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws101/probe_names.json'))+['Terrain_LiDAR_DTM_1m']
CAM='WS90_CAM_eye_left_curb_bend_from_S'
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in names if n in s.objects]
sc=bpy.context.scene
for o in d.objects:
    if o: sc.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
tb=None
B0={}
sc.render.resolution_x=1280; sc.render.resolution_y=720
B=[]
for o in d.objects:
    if not o or o.type!='MESH' or o.hide_render: continue
    e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); B.append((o.name,BVHTree.FromBMesh(bm))); bm.free(); e.to_mesh_clear()
TT=dict(B)['Terrain_LiDAR_DTM_1m']
def gz(x,y): return TT.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0].z
cd=bpy.data.cameras.new('c'); cam=bpy.data.objects.new('c',cd); sc.collection.objects.link(cam); sc.camera=cam; cd.lens=28
loc=Vector((-197.6,-104,gz(-197.6,-104)+1.6)); tgt=Vector((-203,-72,gz(-203,-72)+0.4)); cam.location=loc
cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); bpy.context.view_layer.update()
fr=cd.view_frame(scene=sc); M=cam.matrix_world; TR,BR,BL,TL=[M@v for v in fr]
for lab,(u,v) in {'white':(310/704,207/396),'slot':(590/704,245/396),'slot2':(585/704,232/396),'slot3':(595/704,262/396)}.items():
  for du in (-0.006,0,0.006):
    top=TL.lerp(TR,u+du); bot=BL.lerp(BR,u+du); pt=top.lerp(bot,v); dirv=(pt-M.translation).normalized()
    hits=[]
    for n,t in B:
        h=t.ray_cast(M.translation,dirv,400)
        if h[0] is not None: hits.append((h[3],n,tuple(round(c,2) for c in h[0])))
    hits.sort(); print('P101',lab,du,[ (round(a,1),b[:60],c) for a,b,c in hits[:3]])

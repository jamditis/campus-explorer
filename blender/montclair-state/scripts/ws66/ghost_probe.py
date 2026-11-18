import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to): to.collections=['Terrain']
col=to.collections[0]; bpy.context.scene.collection.children.link(col)
sc=bpy.context.scene; cam=bpy.data.objects.new('C',bpy.data.cameras.new('C')); sc.collection.objects.link(cam); sc.camera=cam; cam.data.lens=30
sc.render.resolution_x=704; sc.render.resolution_y=396
print('GP cam',tuple(round(v,1) for v in cam.location))
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
tt=bpy.data.objects['Terrain_LiDAR_DTM_1m'].evaluated_get(dg); mm=tt.to_mesh(); bm0=bmesh.new(); bm0.from_mesh(mm); bm0.transform(tt.matrix_world); T0=BVHTree.FromBMesh(bm0)
tz=T0.ray_cast(Vector((-224,16,300)),Vector((0,0,-1)))[0].z
cam.location=(-170,70,195); cam.rotation_euler=(Vector((-224,16,tz))-Vector(cam.location)).to_track_quat('-Z','Y').to_euler(); dg.update()
D=np.load('data/dtm_1m.npy')
Ts=[]
for o in col.all_objects:
    if o.type!='MESH' or o.hide_render: continue
    m=o.evaluated_get(dg).to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); Ts.append((o.name,BVHTree.FromBMesh(bm))); bm.free()
fr=cam.data.view_frame(scene=sc); M=cam.matrix_world; o0=M.translation
tr,br,bl,tl=[M@v for v in fr]
for py in range(30,200,20):
  for px in range(260,520,30):
    u=px/704; v=py/396
    p=tl+(tr-tl)*u+(bl-tl)*v; d=(p-o0).normalized()
    best=None
    for n,T in Ts:
        h,nn,i,dist=T.ray_cast(o0,d,5000)
        if h and (best is None or dist<best[0]): best=(dist,h,n)
    if best:
        h=best[1]; dz=h.z-D[int(round(h.y))+250,int(round(h.x))+250] if abs(h.x)<249 and abs(h.y)<249 else float('nan')
        print('GP',px,py,best[2][:28],round(h.x),round(h.y),round(h.z,1),'dDTM',round(dz,1))

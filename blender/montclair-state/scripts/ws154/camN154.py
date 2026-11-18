import bpy, os
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
exec(open(M+'scripts/ws152/facade152.py').read())
C=(W_N+W_S+E_N+E_S)/4; A=W_N; B=E_N; u=(B-A).normalized(); n=Vector((u.y,-u.x))
if ((A+B)/2-C).dot(n)<0: n=-n
mid=(A+B)/2; T=bpy.data.objects.get('Terrain_LiDAR_DTM_1m')
def gz(x,y,d):
    mi=T.matrix_world.inverted(); ok,loc,_,_=T.ray_cast(mi@Vector((x,y,300)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
    return (T.matrix_world@loc).z if ok else d
p2=mid+n*42+u*14; pos=Vector((p2.x,p2.y,163.0))
c=bpy.data.objects.new('WS154_CAM_oblique_Freeman_N_end_from_NE',bpy.data.cameras.new('WS154_CAM_oblique_Freeman_N_end_from_NE')); c.data.lens=24
c.location=pos; c.rotation_euler=(Vector((mid.x,mid.y,138))-pos).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.collection.objects.link(c)
print('CAMN pos',tuple(round(x,2) for x in pos))
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws154c_camN.blend',copy=True); print('SAVED_CAMN')

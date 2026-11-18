import bpy, mathutils
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['UV_CAM_eye_Freeman_N_entrance']; sc.camera=cam
sc.render.resolution_x=1280; sc.render.resolution_y=720
fr=cam.data.view_frame(scene=sc); M=cam.matrix_world
import collections
for v in [0.75,0.55,0.35,0.2]:
  row=[]
  for u in [0.05,0.2,0.35,0.5,0.6,0.7,0.8,0.9]:
    # frame corners: 0 tr,1 br,2 bl,3 tl
    tl,tr,bl=fr[3],fr[0],fr[2]
    p=tl+(tr-tl)*u+(bl-tl)*(1-v)
    d=(M@p - M.translation).normalized()
    hit,loc,n,i,o,mm=sc.ray_cast(dg,M.translation,d)
    row.append((u, o.name[:48] if hit else None, tuple(round(c,2) for c in loc) if hit else None))
  print('V',v); [print('  ',r) for r in row]

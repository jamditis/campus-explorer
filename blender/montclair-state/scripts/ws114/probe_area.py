import bpy, numpy as np
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
out=[]
for y in np.arange(-240,-229.9,0.5):
  for x in np.arange(-243,-227.9,0.5):
    h=sc.ray_cast(dg,Vector((x,y,135)),Vector((0,0,-1)),distance=40)
    if h[0]: out.append((x,y,h[1].z,h[4].name))
import pickle; pickle.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws114/probe_area.pkl','wb')); print('PR done',len(out))

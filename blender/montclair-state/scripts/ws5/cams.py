import bpy
from mathutils import Vector
CAMS={'WS5_CAM_oblique_cole_plaza_from_N_refA':((-99.5,-19.4,158.5),(-107,-52.5,136.0),30)}
def ensure(sc):
  for n,(loc,tgt,lens) in CAMS.items():
    c=bpy.data.objects.get(n)
    if not c:
      cd=bpy.data.cameras.new(n); c=bpy.data.objects.new(n,cd); sc.collection.objects.link(c)
    c.location=loc; c.data.lens=lens; c.data.clip_start=0.1; c.data.clip_end=3000
    dvec=Vector(tgt)-Vector(loc); c.rotation_euler=dvec.to_track_quat('-Z','Y').to_euler()

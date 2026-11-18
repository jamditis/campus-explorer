import bpy
from mathutils import Vector
sc=bpy.context.scene
pc=bpy.data.collections['WS4_Cole_walk_kit_20261109']
for n in ('WS4_Globe_lamp_x80_UNVERIFIED_POS','WS4_Globe_lamp_x64_UNVERIFIED_POS','WS4_Globe_lamp_x50_UNVERIFIED_POS'):
  bpy.data.objects.remove(bpy.data.objects[n])
rc=bpy.data.collections.new('WS4_retired_acorn_lamps_20261109'); sc.collection.children.link(rc)
acorns=[o for o in bpy.data.objects if o.name.startswith('Lamp_acorn') and o.parent is None and -92<o.location.x<-40 and -60<o.location.y<-46]
print('ACORNS',[(o.name,round(o.location.x,1),round(o.location.y,1)) for o in acorns])
L=bpy.data.collections['Lamp_Post_Globe_ColeWalk_wr3']
for a in acorns:
  e=bpy.data.objects.new('WS4_Globe_lamp_replaces_'+a.name,None); e.instance_type='COLLECTION'; e.instance_collection=L
  e.location=a.location.copy(); e.location.z-=0.03; pc.objects.link(e)
  for c in list(a.users_collection): c.objects.unlink(a)
  rc.objects.link(a)
  for ch in a.children:
    for c in list(ch.users_collection): c.objects.unlink(ch)
    rc.objects.link(ch)
bpy.context.view_layer.layer_collection.children[rc.name].exclude=True
s=bpy.data.objects['WS4_Sign_Wayfinding_ColeHall_UNVERIFIED_POS']; r=bpy.data.objects['WS4_RiverRock_strip_sign_bed_UNVERIFIED_POS']
xs=sorted(a.location.x for a in acorns)
# put sign midway between the two acorn positions nearest x=-77
best=-77.0
for i in range(len(xs)-1):
  if xs[i]<-74<xs[i+1] or xs[i]<-78<xs[i+1]: best=(xs[i]+xs[i+1])/2
dx=best-s.location.x; s.location.x+=dx; r.location.x+=dx
print('SIGN at',tuple(round(v,1) for v in s.location))
cam=bpy.data.objects['WS4_CAM_closeup_cole_sign_from_SW']; cam.name='WS4_CAM_closeup_cole_sign_from_SE'
t=s.location+Vector((0,0,1.25)); cp=s.location+Vector((3.8,-6.8,1.65)); cam.location=cp
cam.rotation_euler=(t-cp).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_mainfile(); print('SAVED')

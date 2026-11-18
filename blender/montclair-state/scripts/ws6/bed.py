import bpy
from mathutils import Vector
bed=bpy.data.objects['WS4_Planting_bed_mulch_at_Cole_sign_UNVERIFIED']
vs=[bed.matrix_world@v.co for v in bed.data.vertices]
cx=sum(v.x for v in vs)/len(vs); cy=sum(v.y for v in vs)/len(vs)
print('BED c',cx,cy,'x',min(v.x for v in vs),max(v.x for v in vs),'y',min(v.y for v in vs),max(v.y for v in vs))
col=bpy.data.collections.get('Shrub_Boxwood')
if not col:
  with bpy.data.libraries.load('/workspace/nj-scenes/assets/campus_assets.blend',link=True) as (s,d): d.collections=['Shrub_Boxwood']
  col=d.collections[0] if False else bpy.data.collections.get('Shrub_Boxwood')
print('COL',col, col.library if col else None)
kit=bpy.data.collections['WS6_Cole_gable_front_20261109']
mi=bed.matrix_world.inverted()
import random; random.seed(6)
pts=[(-1.15,0.15),(0.0,-0.1),(1.15,0.2)]
for k,(dx,dy) in enumerate(pts):
  x,y=cx+dx,cy+dy
  ok,loc,n,i=bed.ray_cast(mi@Vector((x,y,300)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
  z=(bed.matrix_world@loc).z if ok else None
  print('PT',k,x,y,z)
  if z is None: continue
  e=bpy.data.objects.new(f'WS6_Boxwood_in_ws4_sign_bed_{k}_UNVERIFIED',None)
  e.instance_type='COLLECTION'; e.instance_collection=col
  e.location=(x,y,z-0.03); e.rotation_euler=(0,0,random.uniform(0,6.28)); s=random.uniform(0.8,1.0); e.scale=(s,s,s)
  kit.objects.link(e)
# measure instance size
print('INSTDIM', [ (o.name,[round(v,2) for v in o.dimensions]) for o in col.all_objects][:3])
cd=bpy.data.cameras.new('WS6_CAM_closeup_ws4_bed_from_S'); cam=bpy.data.objects.new(cd.name,cd); kit.objects.link(cam)
cam.location=(cx-1.5,cy-7.5,135.0+1.6); cd.lens=32
cam.rotation_euler=(Vector((cx,cy,135.0))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_mainfile(); print('SAVED')

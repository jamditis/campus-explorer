import bpy
from collections import Counter
c=Counter()
for o in bpy.data.objects:
  n=o.name.lower()
  if any(k in n for k in ('shrub','azalea','boxwood','hedge','bush')):
    c[(o.type,o.instance_type,o.data.name if o.data else (o.instance_collection.name if o.instance_collection else None))]+=1
for k,v in c.most_common(25): print('SH',v,k)
for col in bpy.data.collections:
  if any(k in col.name.lower() for k in ('shrub','hedge','bush')): print('COL',col.name,col.library, len(col.all_objects), [ (o.name,o.type,[m.type for m in o.modifiers]) for o in col.all_objects][:4])
# examples of mesh shrubs near Cole
import mathutils
for o in bpy.data.objects:
  n=o.name.lower()
  if o.type=='MESH' and any(k in n for k in ('shrub','hedge','bush')):
    p=o.matrix_world.translation
    if abs(p.x+100)<120 and abs(p.y+50)<120: print('NEAR',o.name,[round(v,1) for v in p],[round(v,2) for v in o.dimensions],len(o.data.polygons),[s.material.name for s in o.material_slots if s.material][:2]); 
bed=bpy.data.objects['WS4_Planting_bed_mulch_at_Cole_sign_UNVERIFIED']
print('BED',[round(v,2) for v in bed.matrix_world.translation],[round(v,2) for v in bed.dimensions])
vs=[bed.matrix_world@v.co for v in bed.data.vertices]; print('BEDZ',min(v.z for v in vs),max(v.z for v in vs))
TZ=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; print('TZ mats',[s.material.name for s in TZ.material_slots if s.material])
w=bpy.data.objects['WS6_Cole_gable_arched_window_UNVERIFIED']; vs=[w.matrix_world@v.co for v in w.data.vertices]
print('WIN bbox x',min(v.x for v in vs),max(v.x for v in vs),'y',min(v.y for v in vs),max(v.y for v in vs),'z',min(v.z for v in vs),max(v.z for v in vs))
print('CAMS',[o.name for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith(('WS5','WS6','WS4'))])
for k in ('brick','paver','edging'):
  print(k,[m.name for m in bpy.data.materials if k in m.name.lower()][:12])

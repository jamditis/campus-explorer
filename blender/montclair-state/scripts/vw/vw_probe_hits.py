import bpy
from mathutils import Vector
cam=bpy.data.objects['TI_CAM_oblique_east_dorms_from_SW']
origin=cam.matrix_world.translation
# sample a grid of rays toward Bohn W tower face region
targets=[]
for z in (145,155,162):
  for y in (378,384,390):
    targets.append(Vector((204.7,y,z)))
  for y in (390,394,400):
    targets.append(Vector((231.0,y,z)))
dg=bpy.context.evaluated_depsgraph_get()
print('VW objs', [o.name for o in bpy.data.objects if o.get('vw_obj') and o.type=='MESH'])
for t in targets:
  direction=(t-origin).normalized()
  # scene ray cast via each candidate
  best=None
  for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    if not (o.name.startswith('TL_Bohn') or o.name.startswith('TK_Bohn_Hall_232') or o.name.startswith('TP_Bohn') or o.get('vw_obj')): continue
    e=o.evaluated_get(dg); iw=o.matrix_world.inverted()
    r=e.ray_cast(iw@origin,(iw.to_3x3()@direction).normalized())
    if r[0]:
      hit=o.matrix_world@r[1]; dist=(hit-origin).length
      if best is None or dist<best[0]:
        best=(dist,o.name,[round(x,2) for x in hit])
  print('tgt', [round(x,1) for x in t], '->', best)
# bounds of VW glass
o=bpy.data.objects.get('VW_Bohn_W_glass_UNVERIFIED')
if o:
  bb=[o.matrix_world@Vector(c) for c in o.bound_box]
  xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
  print('glass bbox', round(min(xs),1),round(max(xs),1), round(min(ys),1),round(max(ys),1), round(min(zs),1),round(max(zs),1), 'npoly', len(o.data.polygons))
o=bpy.data.objects.get('VW_Bohn_W_piers_bands_UNVERIFIED')
if o:
  bb=[o.matrix_world@Vector(c) for c in o.bound_box]
  xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
  print('piers bbox', round(min(xs),1),round(max(xs),1), round(min(ys),1),round(max(ys),1), round(min(zs),1),round(max(zs),1), 'npoly', len(o.data.polygons))

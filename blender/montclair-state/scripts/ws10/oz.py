import bpy
o=[x for x in bpy.data.objects if x.name.startswith('OZ_walk_joints_auto_GN')][0]; print('NAME',o.name)
print('OZ',o.data.name,len(o.data.polygons),[m.name for m in o.data.materials])
for m in o.modifiers:
  print('MOD',m.type,m.name)
  if m.type=='NODES':
    for k in m.keys(): 
      v=m[k]; print('  ',k, getattr(v,'name',v))
    for n in m.node_group.nodes:
      if n.type in('OBJECT_INFO','COLLECTION_INFO'): print('  NODE',n.type,[ (i.name,getattr(i,'default_value',None)) for i in n.inputs])
import bmesh
dg=bpy.context.evaluated_depsgraph_get()
from mathutils import Vector
sc=bpy.context.scene
# find surfaces under walk ignoring vegetation: cast repeatedly
for x in range(-82,-44,4):
 for y in (-57,-56,-55,-54,-53):
  orig=Vector((x,y,170)); hits=[]
  for i in range(8):
    r=sc.ray_cast(dg,orig,Vector((0,0,-1)))
    if not r[0]: break
    nm=r[4].name; ms=''
    try: ms=r[4].material_slots[r[4].data.polygons[r[3]].material_index].name if r[4].type=='MESH' and r[3]<len(r[4].data.polygons) else ''
    except Exception as e: ms='?'
    hits.append((nm[:24],ms[:24],round(r[1].z,2)))
    if nm.startswith('Terrain'): break
    orig=r[1]+Vector((0,0,-0.002))
  print('HIT',x,y,[h for h in hits if not h[0].startswith(('T_','gt_','cx_'))])

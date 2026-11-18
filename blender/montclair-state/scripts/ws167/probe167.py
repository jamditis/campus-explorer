import bpy, numpy as np
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; print('MODS',[m.name for m in sk.modifiers][-6:],flush=True)
from mathutils.bvhtree import BVHTree
se=sk.evaluated_get(dg); me=se.to_mesh(); mw=sk.matrix_world
T=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[p.vertices for p in me.polygons]); se.to_mesh_clear()
for y in range(-164,-206,-4):
  row=[]
  for x in range(-372,-294,4):
    r=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1))); h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
    row.append('%d:%s@%.2f/sk%.2f'%(x,(r[4].name[:22] if r[0] else '-'),r[1].z if r[0] else 0,h[0].z if h[0] else 0))
  print('Y',y,' | '.join(row),flush=True)


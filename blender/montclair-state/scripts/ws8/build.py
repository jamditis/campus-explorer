import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
# 1. Joe 3:37 PM: plaza looked charcoal only because it was in shadow in aerial A.
# Sunlit estimate = shadowed plaza * (sunlit walk / shadowed walk) per channel -> sRGB ~(175,171,171),
# ~0.80x the sunlit walk concrete in sRGB (~0.61x linear). WS3 concrete ramp 0.44-0.58 -> plaza 0.27-0.36.
m=bpy.data.materials['WS5_Charcoal_pavers_plaza']
for n in m.node_tree.nodes:
  if n.type=='VALTORGB':
    n.color_ramp.elements[0].color=(0.262,0.258,0.252,1); n.color_ramp.elements[1].color=(0.362,0.357,0.350,1)
  if n.type=='MIX' and n.data_type=='RGBA':
    n.inputs['B'].default_value=(0.17,0.167,0.162,1)
m.name='WS8_Grey_pavers_plaza_sunlit_sampled'
# 2. walk tip poking out of the mulch W of the plaza (ws5-ws7 NEXT c)
bed=bpy.data.objects['COLE_planting_beds_smooth_bu']
bb=bmesh.new(); bb.from_mesh(bed.data); bb.transform(bed.matrix_world); bvh=BVHTree.FromBMesh(bb)
w=bpy.data.objects['WS3_Cole_plaza_paving_20261109']; mw=w.matrix_world
bm=bmesh.new(); bm.from_mesh(w.data); bm.faces.ensure_lookup_table()
kill=[]
for f in bm.faces:
  c=mw@f.calc_center_median()
  if (Vector((c.x,c.y))-Vector((-119,-57.5))).length>6: continue
  loc,nn,i,d=bvh.ray_cast(Vector((c.x,c.y,c.z+3)),Vector((0,0,-1)))
  if loc is None:
    loc,nn,i,d=bvh.ray_cast(Vector((c.x,c.y,c.z-3)),Vector((0,0,1)))
  if loc is not None and abs(loc.z-c.z)<0.25: kill.append(f)
print('KILL',len(kill),[f.index for f in kill][:40])
bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(w.data); bm.free(); w.data.update()
bpy.ops.wm.save_mainfile()
print('SAVED')

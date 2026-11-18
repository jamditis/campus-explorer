import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    ev=o.evaluated_get(dg); me=ev.to_mesh(); bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); ev.to_mesh_clear(); return t
RB=bvh(bpy.data.objects['WS27_CollegeAve_carriageway_2020ortho'])
TB=bvh(bpy.data.objects['Terrain_LiDAR_DTM_1m'])
prof=[]
for y in range(-158,-60,3):
  row=[]
  for x in range(-248,-196,1):
    r=RB.ray_cast(Vector((x,y,175)),Vector((0,0,-1)))
    if not r[0]: continue
    t=TB.ray_cast(Vector((x,y,175)),Vector((0,0,-1)))
    row.append((x,round(r[0].z,2),round((t[0].z if t[0] else 0)-r[0].z,2)))
  if row:
    mid=row[len(row)//2]
    prof.append((y,mid[0],mid[1],max(d for _,_,d in row)))
for p in prof: print('y',p[0],'x',p[1],'roadz',p[2],'max terrain-road',p[3])
# grass instances on road
from collections import Counter
c=Counter(); ex={}
for inst in dg.object_instances:
    if not inst.is_instance: continue
    p=inst.matrix_world.translation
    if -248<p.x<-196 and -158<p.y<-60:
        r=RB.ray_cast(Vector((p.x,p.y,p.z+3)),Vector((0,0,-1)),6)
        if r[0] and abs(p.z-r[0].z)<1.0:
            n=inst.parent.name if inst.parent else '?'; c[n]+=1; ex.setdefault(n,(round(p.x,1),round(p.y,1)))
print('instances on road',c.most_common(10),ex)

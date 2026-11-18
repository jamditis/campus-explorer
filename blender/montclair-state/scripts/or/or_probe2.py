import bpy
from mathutils import Vector
m=bpy.data.materials['Wall_stucco_mission']
print('NODES',[n.type+':'+n.name for n in m.node_tree.nodes])
w=bpy.data.objects['Center for Computing and Information Science walls']
vs=[w.matrix_world@v.co for v in w.data.vertices]
mn=Vector((min(v.x for v in vs),min(v.y for v in vs),min(v.z for v in vs))); mx=Vector((max(v.x for v in vs),max(v.y for v in vs),max(v.z for v in vs)))
print('CCIS bbox',mn,mx)
import collections
cnt=collections.Counter()
for o in bpy.data.objects:
    if o.type not in('MESH','EMPTY'): continue
    p=o.matrix_world.translation
    if o.type=='MESH' and len(o.data.vertices):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; p=sum(bb,Vector())/8
    if mn.x-3<p.x<mx.x+3 and mn.y-3<p.y<mx.y+3:
        cnt[(o.name[:50], o.users_collection[0].name[:40] if o.users_collection else '')]+=1
for k,v in cnt.most_common(40): print(v,k)

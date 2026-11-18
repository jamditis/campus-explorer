import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
br=bpy.data.objects['WS11_Cole_SW_bed_walk_bridge_UNVERIFIED']
print('BR mats',[m.name for m in br.data.materials],len(br.data.vertices))
for o in bpy.data.objects:
    if o.name.startswith('OZ_walk_joints'):
        print('OZ',o.name,o.type,[m.name for m in getattr(o.data,'materials',[])],[ (m.type,m.name) for m in o.modifiers])
fo=bpy.data.objects['Footpaths_OSM']; print('FO mats',[s.material.name if s.material else None for s in fo.material_slots])
A=Vector((-86.4,-63.92,0)); B=Vector((-69.74,-68.43,0)); d=(B-A); d.z=0; d.normalize(); nrm=Vector((-d.y,d.x,0))
w=fo.matrix_world; from collections import Counter
c=Counter()
for p in fo.data.polygons:
    q=w@p.center; t=(Vector((q.x,q.y,0))-A).dot(d); s=(Vector((q.x,q.y,0))-A).dot(nrm)
    if abs(s)<3 and 10<t<30 and p.normal.z>0.7: c[(int(t), fo.material_slots[p.material_index].name)]+=1
for k in sorted(c): print('FOPOLY',k,c[k])
m=bpy.data.materials['WS4_Concrete_walk_broom_nogrid']
for n in m.node_tree.nodes:
    print('N',n.type,n.name,[(i.name,tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if not i.is_linked and hasattr(i,'default_value')][:6])
# end heights of bridge vs walk along axis
vs=[br.matrix_world@v.co for v in br.data.vertices]
ts=[(v-A).dot(d) for v in vs]; tmin,tmax=min(ts),max(ts); print('T range',tmin,tmax)

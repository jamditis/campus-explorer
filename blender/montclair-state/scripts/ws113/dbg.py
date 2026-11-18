import bpy
from mathutils import Vector
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; m=t.modifiers['WS113_paving_edge_grade']
print('P113 mod',m.node_group.name, m.show_viewport, m.show_render)
for n in m.node_group.nodes:
    if n.type=='PROXIMITY': print('P113 prox inputs',[ (i.name,i.is_linked) for i in n.inputs])
    if n.type=='SAMPLE_NEAREST_SURFACE': print('P113 sns',[(i.name,i.is_linked) for i in n.inputs if i.enabled])
    if n.type=='OBJECT_INFO': print('P113 oi',n.inputs['Object'].default_value)
dg=bpy.context.evaluated_depsgraph_get()
e=t.evaluated_get(dg); me=e.to_mesh()
import numpy as np
for i,v in enumerate(me.vertices):
    if -241<v.co.x<-234 and -245<v.co.y<-236:
        print('P113 v',round(v.co.x,1),round(v.co.y,1),'eval z %.3f orig %.3f'%(v.co.z,t.data.vertices[i].co.z) if i<len(t.data.vertices) else '')

import bpy
from mathutils import Vector
for n in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','WS60_terrain_edge_apron_LiDAR_to_skirt'):
    o=bpy.data.objects[n]; print('M68',n,[m.name for m in o.data.materials],[ (m.name,m.type,getattr(m,'node_group',None) and m.node_group.name, getattr(m,'object',None) and m.object.name) for m in o.modifiers], 'uv',[u.name for u in o.data.uv_layers])
    for m in o.data.materials[:2]:
        if m and m.node_tree: print('M68  nodes',m.name,[(nd.type,getattr(nd,'image',None) and nd.image.name) for nd in m.node_tree.nodes if nd.type in('TEX_IMAGE','TEX_COORD','UVMAP','ATTRIBUTE','MAPPING')])
dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['WS48_band_street_trees_OSM_lowLOD'];e=o.evaluated_get(dg)
c=0
for inst in dg.object_instances:
    if inst.is_instance and inst.parent and inst.parent.original.name.startswith('WS48'):
        p=inst.matrix_world.translation
        if -350<p.x<-240 and -140<p.y<45: c+=1; print('M68 tree',round(p.x,1),round(p.y,1),round(p.z,1))
print('M68 ws48 in domain',c)

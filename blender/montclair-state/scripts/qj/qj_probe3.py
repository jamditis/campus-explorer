import bpy
for n in ('Roads_OSM','Footpaths_OSM','OZ_walk_joints_auto_GN_UNVERIFIED','BD_farfield_3DEP_ortho'):
    o=bpy.data.objects[n]; print('OBJ',n,len(o.data.polygons),[(m.name,m.type,(m.node_group.name if m.type=='NODES' else '')) for m in o.modifiers], tuple(round(x,1) for x in o.dimensions))
    for m in o.modifiers:
        if m.type=='NODES':
            for nd in m.node_group.nodes:
                if nd.bl_idname=='GeometryNodeObjectInfo': print('   OI',m.name, nd.inputs['Object'].default_value and nd.inputs['Object'].default_value.name)
            for k,v in m.items():
                if hasattr(v,'name'): print('   SOCK',m.name,k,v.name)

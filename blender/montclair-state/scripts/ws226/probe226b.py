import bpy, sys, os
from mathutils import Vector
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for mn in ['QG_north_strip_LiDAR_patch','QH_east_fan_LiDAR_patch','QI_east_edge_LiDAR_patch']:
    m=t.modifiers[mn]; g=m.node_group
    print('P226 ==',mn,flush=True)
    for n in g.nodes:
        s=n.bl_idname+' '+n.name
        if n.bl_idname=='GeometryNodeObjectInfo':
            o=n.inputs[0].default_value; s+=' obj=%s'%(o.name if o else None)
            if o: 
                bb=[o.matrix_world@Vector(c) for c in o.bound_box]; s+=' bb x%.0f..%.0f y%.0f..%.0f z%.1f..%.1f nv%d'%(min(v.x for v in bb),max(v.x for v in bb),min(v.y for v in bb),max(v.y for v in bb),min(v.z for v in bb),max(v.z for v in bb),len(o.data.vertices) if o.type=='MESH' else -1)
                s+=' hide_r=%s'%o.hide_render
        for a in ('domain','mode','data_type','transform_space'):
            if hasattr(n,a): s+=' %s=%s'%(a,getattr(n,a))
        for i in n.inputs:
            if not i.is_linked and hasattr(i,'default_value') and i.type in ('VALUE','VECTOR','BOOLEAN','INT'):
                v=i.default_value; s+=' [%s=%s]'%(i.name, tuple(round(x,3) for x in v) if hasattr(v,'__len__') else v)
        print('P226  ',s,flush=True)
    for l in g.links: print('P226   L %s.%s -> %s.%s'%(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier),flush=True)
sys.stdout.flush(); os._exit(0)

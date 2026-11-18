import bpy
from collections import defaultdict
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for o in (sk,ter):
    print('OBJ',o.name,[m.name for m in o.modifiers],[ (s.link,s.material.name if s.material else None) for s in o.material_slots], len(o.data.vertices))
    for s in o.material_slots:
        if s.material and s.material.node_tree:
            for n in s.material.node_tree.nodes:
                ex=''
                if n.type=='TEX_IMAGE' and n.image: ex=n.image.name+' '+str(n.image.size[:])
                if n.type=='ATTRIBUTE': ex=n.attribute_name
                print('  N',n.name,n.type,ex,[ (l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in s.material.node_tree.links if l.from_node==n][:3])
for ob in bpy.data.collections['OR_skirt_base_course_20261031or'].objects:
    me=ob.data
    print('BC',ob.name,len(me.vertices),len(me.polygons),[a.name for a in me.attributes])

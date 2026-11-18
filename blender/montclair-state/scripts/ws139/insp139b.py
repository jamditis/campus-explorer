import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith('T_'):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; cx=sum(c.x for c in bb)/8; cy=sum(c.y for c in bb)/8
        if -185<cx<-80 and -310<cy<-255: print('TT',o.name,round(cx,1),round(cy,1),round(max(c.z for c in bb)-min(c.z for c in bb),1))
for c in ('Tree_prototypes','Trees_assets_LiDAR'):
    if c in bpy.data.collections: print('PC',c,[ (o.name,round(o.dimensions.z,1)) for o in bpy.data.collections[c].objects][:30])
for n in ('Footpaths_OSM','UA_footway_312845863_south_UNVERIFIED','WS136a_Skyline_W_walk_N_of_-248_OSM312845863_graded_2p3m_UNVERI'):
    o=[x for x in bpy.data.objects if x.name.startswith(n)][0]; mw=o.matrix_world
    for p in o.data.polygons:
        c=mw@p.center
        if -76<c.x<-66 and -207<c.y<-194: print('FP',o.name[:20],p.index,round(c.x,2),round(c.y,2),round(c.z,2),round(p.area,2),p.material_index)
o=bpy.data.objects['OZ_walk_joints_auto_GN_UNVERIFIED']
for m in o.modifiers:
    print('MOD',m.name,m.node_group.name if m.node_group else None,[ (k,getattr(m[k],'name',m[k])) for k in m.keys() if not k.endswith(('_use_attribute','_attribute_name'))][:6])

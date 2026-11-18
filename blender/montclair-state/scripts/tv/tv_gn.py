import bpy
O=bpy.data.objects['TJ_Webster_lawn_grass_points_UNVERIFIED']
for m in O.modifiers:
    print('MOD',m.name,m.type,getattr(m,'node_group',None) and m.node_group.name, m.show_render)
    if m.type=='NODES':
        for k,v in m.items(): print('  inp',k,v if not hasattr(v,'name') else v.name)
        for n in m.node_group.nodes:
            print('  N',n.bl_idname,n.name,[ (i.name, getattr(i,'default_value',None) if not i.is_linked else 'L') for i in n.inputs if i.name in ('Selection','Density','Distance','Target','Object','Value')][:4])
import mathutils
vs=O.data.vertices; print('n',len(vs), 'last',tuple(O.matrix_world@vs[-1].co))

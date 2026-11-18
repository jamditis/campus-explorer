import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.name.startswith(('WS110_','WS111_','WS112_','OZ_','T_SugarMaple_L1_0000')):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        print('P113',o.name,o.type,o.hide_render,[m.type+':'+(m.node_group.name if m.type=='NODES' and m.node_group else '') for m in o.modifiers],'x%.1f..%.1f y%.1f..%.1f z%.2f..%.2f'%(min(v.x for v in bb),max(v.x for v in bb),min(v.y for v in bb),max(v.y for v in bb),min(v.z for v in bb),max(v.z for v in bb)), 'loc',tuple(round(c,2) for c in o.location))
print('P113 terrain mw',bpy.data.objects['Terrain_LiDAR_DTM_1m'].matrix_world.to_translation())

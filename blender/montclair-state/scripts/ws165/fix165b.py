# ws165b: widen the WS165 tree crown to the LiDAR footprint (~14 m: x -305..-291, y -248..-230); ws165a came out 11.1 m (asset bbox
# in main differs from the subset probe). XY scale about the trunk base only; height (17.8 m) and lowest leaves (3.7 m) unchanged.
import bpy
from mathutils import Matrix, Vector
t=bpy.data.objects['WS165_tree_aisle_mouth_LiDAR2023_h18m_RedMaple_UNVERIFIEDspecies'] if 'WS165_tree_aisle_mouth_LiDAR2023_h18m_RedMaple_UNVERIFIEDspecies' in bpy.data.objects else [o for o in bpy.data.objects if o.name.startswith('WS165_tree')][0]
F=float(__import__('os').environ.get('TREE_F','1.26'))
p=Vector((-298.4,-241.0,0))
t.matrix_world=Matrix.Translation(p)@Matrix.Diagonal((F,F,1,1))@Matrix.Translation(-p)@t.matrix_world
bpy.context.view_layer.update()
bb=[t.matrix_world@Vector(c) for c in t.bound_box]
print('TREEB',t.name,'x',round(min(c.x for c in bb),1),round(max(c.x for c in bb),1),'y',round(min(c.y for c in bb),1),round(max(c.y for c in bb),1),flush=True)

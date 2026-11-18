import bpy
from mathutils import Vector
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data; names=[m.name if m else None for m in me.materials]
mi=names.index('WS82_Lawn_grandstand_no_ortho_UNVERIFIED')
fl=sum(1 for p in me.polygons if p.material_index==mi and not p.use_smooth)
print('WS83c terrain WS82 faces flat',fl,'of',sum(1 for p in me.polygons if p.material_index==mi),'mods',[m.type for m in T.modifiers],flush=True)
for p in me.polygons:
    if p.material_index==mi: p.use_smooth=True
cur=bpy.data.objects.get('WS81_terrain_W_edge_curtain_lawn_UNVERIFIED_grade')
if cur:
    print('WS83c curtain flat',sum(1 for p in cur.data.polygons if not p.use_smooth),flush=True)
    for p in cur.data.polygons: p.use_smooth=True
# who else is in the grandstand lawn box
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o==T: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[c.x for c in bb]; ys=[c.y for c in bb]
    if min(xs)<-228 and max(xs)>-256 and min(ys)<-120 and max(ys)>-150 and (max(xs)-min(xs))<400:
        print('WS83c OBJ',o.name,[m.name for m in o.data.materials if m][:3],'x %.0f..%.0f y %.0f..%.0f'%(min(xs),max(xs),min(ys),max(ys)),flush=True)
bpy.ops.wm.save_mainfile(); print('WS83c SAVED',flush=True)

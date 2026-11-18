import bpy
for cn in ['OI_Schmitt_entrance_pavilion_20261031oi','OI_Schmitt_wing_arcade_20261031oi']:
    c=bpy.data.collections[cn]
    for o in c.objects:
        bb=[o.matrix_world@__import__('mathutils').Vector(b) for b in o.bound_box]
        print(cn[:6],o.name,o.type,[m.name for m in o.data.materials] if hasattr(o.data,'materials') else '', len(o.data.polygons) if o.type=='MESH' else '', [round(min(v[i] for v in bb),2) for i in range(3)],[round(max(v[i] for v in bb),2) for i in range(3)])
for m in ['OH_Schmitt_door_glass_clear_UNVERIFIED','OI_Schmitt_pavilion_roof_tile_UNVERIFIED','OH_Schmitt_stucco_block_base_UNVERIFIED','OI_Schmitt_pier_block_plinth_UNVERIFIED']:
    mm=bpy.data.materials.get(m); print(m, mm and [(n.name,n.type) for n in mm.node_tree.nodes])
r=bpy.data.objects['Schmitt Hall roof (LiDAR)']; print('roofmat',[m.name for m in r.data.materials])
for n in bpy.data.materials['Roof_tile_or_membrane'].node_tree.nodes:
    if n.type in('RGB','VALTORECOLOR','TEX_IMAGE'): print(' roofnode',n.name,n.type)
for o in bpy.data.objects:
    if 'Footpaths_OSM' in o.name or 'cheek' in o.name.lower(): print('path',o.name,len(o.data.polygons) if o.type=='MESH' else '')

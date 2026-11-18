import bpy
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']; print('TM71',len(o.data.vertices),[(m.name,m.type,m.show_render) for m in o.modifiers])

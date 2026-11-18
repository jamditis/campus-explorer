import bpy
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
print('MODS',[(m.name,m.type,m.show_render) for m in t.modifiers])
p=bpy.data.objects['QI_east_edge_delete_probe']
print('PROBE',p.hide_render,p.hide_viewport,p.hide_get(),p.visible_camera,p.display_type,[c.name for c in p.users_collection])
import bmesh
me=t.data; L=[]
for e in me.edges:
    a=me.vertices[e.vertices[0]].co; b=me.vertices[e.vertices[1]].co
    if 92<a.x<142 and -82<a.y<-58: L.append((a-b).length)
import statistics
print('EDGES',len(L),statistics.median(L) if L else None,max(L) if L else None)

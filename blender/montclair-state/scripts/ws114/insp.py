import bpy, numpy as np
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
o=O('WS112_CollegeAve_S_E_walk_N_brick'); me=o.data; mw=o.matrix_world
print('I114',o.name,len(me.vertices),len(me.polygons),[m.name for m in o.modifiers],[m.name for m in me.materials], tuple(mw.translation))
for i,v in enumerate(me.vertices):
    c=mw@v.co; print('V',i,'%.2f %.2f %.3f'%tuple(c))
for f in me.polygons[:200]:
    print('F',f.index,list(f.vertices),f.material_index,'%.2f'%f.normal.z)
for n in ('WS113_paving_tops_proxy',):
    p=bpy.data.objects[n]; print('I114 proxy',len(p.data.polygons))
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; print('I114 terrain mods',[(m.name,m.type) for m in t.modifiers])
for o in bpy.data.objects:
    if o.name.startswith(('WS113','WS110_ground','WS111_CollegeAve_S_E','Footpaths')): print('OBJ',o.name,len(o.data.polygons) if o.type=='MESH' else '',[m.name for m in o.modifiers])

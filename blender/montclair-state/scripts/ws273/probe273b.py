# ws273 probe B (NO SAVE): material map (face centres, 1 m cells) of the visible ground meshes around the Sprague grandstand lawn.
import bpy, os, numpy as np
from mathutils import Vector
TAG='P273B'; BX=(-290.0,-226.0,-136.0,-100.0)
NAMES=['Terrain_LiDAR_DTM_1m','WS68_RHD_ground_northDTM','WS81_terrain_W_edge_curtain_lawn_UNVERIFIED_grade','WS60_terrain_edge_apron_LiDAR_to_skirt']
G={}; KEY={}
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not any(o.name.startswith(n) for n in NAMES): continue
    mw=o.matrix_world
    for p in o.data.polygons:
        c=mw@p.center
        if BX[0]<c.x<BX[1] and BX[2]<c.y<BX[3]:
            ms=o.material_slots[p.material_index].material if o.material_slots else None
            k=(o.name[:4],ms.name if ms else None)
            if k not in KEY: KEY[k]=chr(65+len(KEY))
            cell=(int(np.floor(c.x)),int(np.floor(c.y)))
            if cell not in G or c.z>G[cell][1]: G[cell]=(KEY[k],c.z)
for k,v in KEY.items(): print(TAG,'KEY',v,k,flush=True)
print(TAG,'x0',BX[0],'cols 1 m')
for y in range(int(BX[3])-1,int(BX[2])-1,-1):
    print(TAG,f'{y:5d} '+''.join(G.get((x,y),('.',0))[0] for x in range(int(BX[0]),int(BX[1]))),flush=True)
for o in bpy.data.materials:
    if o.name in ('WS82_Lawn_grandstand_no_ortho_UNVERIFIED','COLE_lawn_post2020_bs','Ground_ortho_grass','Lawn_Varied_Oct_local_fade','WS68_Ground_ortho_grass_north2020'):
        print(TAG,'MAT',o.name,'users',o.users,'nodes',[n.bl_idname+':'+n.name for n in o.node_tree.nodes][:14] if o.use_nodes else None,flush=True)
os._exit(0)

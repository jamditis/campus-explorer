import bpy, numpy as np, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; bt=BVHTree.FromObject(T,dg)
P=bpy.data.objects.get('QI_east_edge_LiDAR_terrain_patch'); bp=BVHTree.FromObject(P,dg) if P else None
D=np.load('north/data/grid_1m.npz')['dtm_filled']; H=np.zeros((70,70))
for j,y in enumerate(np.arange(230.5,300,1.0)):
    for i,x in enumerate(np.arange(150.5,220,1.0)):
        h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
        H[j,i]=np.nan if h is None else h.z-D[int(math.floor(y))+260,int(math.floor(x))+600]
for j in range(0,70,5):
    print('DEVROW y=%4d'%(j+230),' '.join('%4.0f'%np.nanmax(np.abs(H[j:j+5,i:i+5])) if not np.all(np.isnan(H[j:j+5,i:i+5])) else '   .' for i in range(0,70,5)))
for o in bpy.data.objects:
    if not o.name.startswith('T_LondonPlane') or o.hide_render: continue
    x,y,z=o.matrix_world.translation
    if not(140<=x<=250 and -40<=y<=255): continue
    h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]; inp=bp is not None and bp.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0] is not None
    if h and z-h.z<-1: print('TREE',o.name,round(x),round(y),round(z,1),round(h.z,1),'D',round(float(D[int(y)+260,min(int(x),219)+600]),1),'inpatch',inp)

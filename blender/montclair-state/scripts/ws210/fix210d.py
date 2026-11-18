# ws210: the rest of the white 'old footway line' (WS3_Concrete_panels_sawcut sliver faces on Terrain, bs_orig_mat 0) between the
# fix210a box and the stretch ws82b already returned to lawn (~(-240,-124.7)->(-230,-118)). Same call as ws82b: no OSM way, no paving
# in the 2020 ortho -> lawn (mat 2 COLE_lawn_post2020_bs). Material only.
import bpy, numpy as np
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data; mw=np.array(T.matrix_world)
pc=np.zeros(len(me.polygons)*3); me.polygons.foreach_get('center',pc); pc=pc.reshape(-1,3)
P=np.c_[pc,np.ones(len(pc))]@mw.T; x,y=P[:,0],P[:,1]
m=np.zeros(len(me.polygons),dtype=np.int32); me.polygons.foreach_get('material_index',m)
om=np.zeros(len(me.polygons),dtype=np.int32); me.attributes['bs_orig_mat'].data.foreach_get('value',om)
sel=(m==3)&(om==0)&(x>-232)&(x<-212)&(y>-121)&(y<-106)
print('F210d mat3->2',int(sel.sum()),flush=True)
m[sel]=2; me.polygons.foreach_set('material_index',m); me.update()

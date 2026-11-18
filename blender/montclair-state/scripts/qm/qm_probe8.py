import bpy, numpy as np
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.evaluated_get(dg).data
n=len(me.polygons); c=np.zeros(n*3); me.polygons.foreach_get('center',c); c=c.reshape(-1,3)
a=np.zeros(n); me.polygons.foreach_get('area',a)
m=(c[:,0]>105)&(c[:,0]<150)&(c[:,1]>140)&(c[:,1]<185)
print('faces in box',m.sum(),'area pct', np.percentile(a[m],[5,50,95,100]).round(2))
big=np.nonzero(m&(a>2))[0]; print('big',len(big), [(tuple(c[i].round(1)),round(a[i],1)) for i in big[:15]])
for md in T.modifiers: print(md.name, md.show_render)

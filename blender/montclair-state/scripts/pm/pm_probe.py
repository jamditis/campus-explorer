import bpy, numpy as np
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']
m=r.data; mw=np.array(r.matrix_world)
print('mods',[x.name for x in r.modifiers],'slots',[s.material.name if s.material else None for s in r.material_slots])
n=len(m.vertices); co=np.zeros(n*3); m.vertices.foreach_get('co',co); co=co.reshape(-1,3)
co=co@mw[:3,:3].T+mw[:3,3]
mi=np.zeros(len(m.polygons),dtype=int); m.polygons.foreach_get('material_index',mi)
nz=np.zeros(len(m.polygons)*3); m.polygons.foreach_get('normal',nz); nz=nz.reshape(-1,3)[:,2]
print('verts',n,'faces',len(m.polygons),'slot hist',np.bincount(mi))
print('bbox',co.min(0),co.max(0))
print('z hist',np.histogram(co[:,2],bins=15))
for s in range(mi.max()+1):
    sel=mi==s
    if sel.any(): print('slot',s,sel.sum(),'nz mean',nz[sel].mean(), 'nz<0.97',(nz[sel]<0.97).sum())

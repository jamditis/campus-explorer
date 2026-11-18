import bpy, numpy as np, json
R='/workspace/nj-scenes/montclair-state'
sc=bpy.context.scene
ters=[o for o in sc.objects if o.type=='MESH' and o.name.startswith('Terrain')]
print('terrains',[(o.name,len(o.data.vertices)) for o in ters])
X0,X1,Y0,Y1=-250,250,-250,400; S=1.0
W=int((X1-X0)/S); H=int((Y1-Y0)/S)
img=np.zeros((H,W,3),np.uint8)+30
for ter in ters:
    me=ter.data; n=len(me.vertices); co=np.zeros(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(ter.matrix_world); co=co@M[:3,:3].T+M[:3,3]
    ne=len(me.edges); ed=np.zeros(ne*2,dtype=np.int64); me.edges.foreach_get('vertices',ed); ed=ed.reshape(-1,2)
    a,b=ed[:,0],ed[:,1]; L=np.linalg.norm(co[a,:2]-co[b,:2],axis=1)+1e-6; s=np.abs(co[a,2]-co[b,2])/L
    m=(co[a]+co[b])/2
    px=((m[:,0]-X0)/S).astype(int); py=((Y1-m[:,1])/S).astype(int); ok=(px>=0)&(px<W)&(py>=0)&(py<H)
    v=np.clip(s/1.0,0,1)
    col=np.stack([255*v,255*(1-v)*0.6,40+0*v],1).astype(np.uint8)
    for i in np.nonzero(ok)[0][np.argsort(v[ok])]: img[py[i],px[i]]=col[i]
np.save(R+'/data/ws29/slope_img.npy',img)

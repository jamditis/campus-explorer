import bpy, numpy as np
o=[x for x in bpy.data.objects if x.name.startswith('WS163_Lot3_aisle_S_drive')][0]; me=o.data; mw=o.matrix_world
m=o.material_slots[0].material
for n in m.node_tree.nodes:
    print('U203 node',n.type,n.name,getattr(n,'image',None) and n.image.filepath, getattr(n,'uv_map',None) if n.type=='UVMAP' else '',flush=True)
print('U203 uvlayers',[l.name for l in me.uv_layers])
uv=me.uv_layers.active.data
pts=[]
for p in me.polygons:
    for li in p.loop_indices:
        v=mw@me.vertices[me.loops[li].vertex_index].co
        if -309<v.x<-304 and -243<v.y<-237: pts.append((v.x,v.y,uv[li].uv[0],uv[li].uv[1]))
P=np.array(pts); print('U203 n',len(P))
# fit affine x,y -> u,v
A=np.c_[P[:,0],P[:,1],np.ones(len(P))]
cu=np.linalg.lstsq(A,P[:,2],rcond=None)[0]; cv=np.linalg.lstsq(A,P[:,3],rcond=None)[0]
print('U203 cu',cu.tolist(),'cv',cv.tolist(),'res',float(np.abs(A@cu-P[:,2]).max()))

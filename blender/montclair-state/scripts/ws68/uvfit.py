import bpy,numpy as np
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']; m=o.data; uv=m.uv_layers['ortho'].data; A=[];U=[]
for pi in range(0,len(m.polygons),97):
    p=m.polygons[pi]
    for li in p.loop_indices:
        c=o.matrix_world@m.vertices[m.loops[li].vertex_index].co; A.append((c.x,c.y,1)); U.append(tuple(uv[li].uv))
A=np.array(A);U=np.array(U)
cu=np.linalg.lstsq(A,U[:,0],rcond=None)[0]; cv=np.linalg.lstsq(A,U[:,1],rcond=None)[0]
print('U68',cu,cv,np.abs(A@cu-U[:,0]).max())
for x in (-350,-250,250): print('U68 x',x,'u',cu[0]*x+cu[2])
im=bpy.data.images['ortho2020.png']; print('U68 img',im.size[:], im.filepath)
mat=bpy.data.materials['Ground_ortho_grass']
for n in mat.node_tree.nodes:
    if n.type=='TEX_IMAGE': print('U68 ext',n.image.name,n.extension)

import bpy, numpy as np
o=bpy.data.objects['PA_north_strip_lawn_smooth_UNVERIFIED']; dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); m=e.to_mesh()
a=m.attributes['ortho']; print('UV',a.domain,a.data_type,len(a.data)); v=np.zeros(len(a.data)*2); a.data.foreach_get('vector',v); v=v.reshape(-1,2); print('UV stats',v.min(0),v.max(0),v[:3])
T=bpy.data.objects['Terrain_LiDAR_DTM_1m'].data; b=T.attributes['ortho']; w=np.zeros(len(b.data)*2); b.data.foreach_get('vector',w); w=w.reshape(-1,2); print('UV terr',w.min(0),w.max(0))
mat=T.materials[0]
for n in mat.node_tree.nodes:
    if n.type=='TEX_IMAGE': print('UV img',n.image and n.image.filepath, n.extension, [l.from_node.type+':'+l.from_socket.name for l in n.inputs[0].links])

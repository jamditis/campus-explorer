# ws229 W53e: Ground_ortho_grass mapping + terrain UVs in the SE regrid vs untouched faces (affine fit uv=f(x,y))
import bpy,sys,numpy as np
mat=bpy.data.materials['Ground_ortho_grass']
for n in mat.node_tree.nodes:
    extra=''
    if n.bl_idname=='ShaderNodeTexImage': extra=(n.image.name if n.image else None, n.image.size[:] if n.image else None)
    if n.bl_idname=='ShaderNodeUVMap': extra=n.uv_map
    if n.bl_idname=='ShaderNodeAttribute': extra=n.attribute_name
    print('P229F node',n.bl_idname,n.name,extra,[ (i.name,[l.from_node.name for l in i.links]) for i in n.inputs if i.is_linked][:4],flush=True)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
print('P229F uv layers',[(u.name,u.active_render) for u in me.uv_layers],flush=True)
uv=me.uv_layers.active.data
X=[];U=[];R=[]
for p in me.polygons:
    c=p.center
    for li in p.loop_indices:
        v=me.vertices[me.loops[li].vertex_index].co
        rec=(v.x,v.y,uv[li].uv[0],uv[li].uv[1])
        if 140<c.x<246 and -249<c.y<-60: R.append(rec)
        elif (0<c.x<140 and -249<c.y<-60): X.append(rec)
X=np.array(X);R=np.array(R)
M=np.c_[X[:,0],X[:,1],np.ones(len(X))]
cu,_,_,_=np.linalg.lstsq(M,X[:,2],rcond=None);cv,_,_,_=np.linalg.lstsq(M,X[:,3],rcond=None)
print('P229F fit outside n',len(X),'cu',cu,'cv',cv,'res', np.abs(M@cu-X[:,2]).max(), np.abs(M@cv-X[:,3]).max(),flush=True)
MR=np.c_[R[:,0],R[:,1],np.ones(len(R))]
eu=np.abs(MR@cu-R[:,2]);ev=np.abs(MR@cv-R[:,3])
print('P229F SE region loops',len(R),'uv err pct',np.percentile(eu,[50,90,99,100]).round(4),np.percentile(ev,[50,90,99,100]).round(4),'uv range',R[:,2].min(),R[:,2].max(),R[:,3].min(),R[:,3].max(),flush=True)
bad=R[(eu>0.002)|(ev>0.002)]
print('P229F bad loops',len(bad),'x',bad[:,0].min() if len(bad) else None,bad[:,0].max() if len(bad) else None,'y',bad[:,1].min() if len(bad) else None,bad[:,1].max() if len(bad) else None,flush=True)
sys.stdout.flush(); import os; os._exit(0)

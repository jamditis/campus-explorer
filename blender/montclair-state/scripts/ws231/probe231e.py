import bpy,os,sys,numpy as np
M='/workspace/nj-scenes/montclair-state/'
P=np.load(M+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy')
def p3(x,y):
    gx=x+280-0.5; gy=y+280-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    return float(P[i,j]*(1-fx)*(1-fy)+P[i,j+1]*fx*(1-fy)+P[i+1,j]*(1-fx)*fy+P[i+1,j+1]*fx*fy)
N=['Terrain_LiDAR_DTM_1m','QG_north_strip_LiDAR_terrain_patch','QH_east_fan_LiDAR_terrain_patch','QI_east_edge_LiDAR_terrain_patch']
with bpy.data.libraries.load(M+'montclair_state.blend',link=False) as (src,dst): dst.objects=[n for n in N if n in src.objects]+[n for n in src.objects if n.startswith('PB_') or 'helper' in n.lower()][:0]
for o in dst.objects:
    W=o.matrix_world; c=0
    for v in o.data.vertices:
        w=W@v.co
        if 148<w.x<172 and 238<w.y<252:
            c+=1
            if w.z-p3(w.x,w.y)<-0.3 or (c<=3): print('P231E',o.name[:12],round(w.x,1),round(w.y,1),round(w.z,2),round(w.z-p3(w.x,w.y),2),flush=True)
    print('P231E',o.name,'count',c,flush=True)
sys.stdout.flush(); os._exit(0)

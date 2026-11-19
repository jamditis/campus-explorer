import bpy,os,sys,numpy as np
M='/workspace/nj-scenes/montclair-state/'
P=np.load(M+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy')
def p3(x,y):
    gx=x+280-0.5; gy=y+280-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    return float(P[i,j]*(1-fx)*(1-fy)+P[i,j+1]*fx*(1-fy)+P[i+1,j]*(1-fx)*fy+P[i+1,j+1]*fx*fy)
with bpy.data.libraries.load(M+'montclair_state_ws231a.blend',link=False) as (src,dst): dst.objects=['WS60_terrain_edge_apron_LiDAR_to_skirt']
o=dst.objects[0]; W=o.matrix_world
for v in o.data.vertices:
    w=W@v.co
    if 145<w.x<250 and 244<w.y<270: print('P231F',round(w.x,1),round(w.y,1),round(w.z,2),round(w.z-p3(w.x,w.y),2),flush=True)
sys.stdout.flush(); os._exit(0)

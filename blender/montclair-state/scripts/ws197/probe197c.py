import bpy,numpy as np
from mathutils import Vector
t=np.array((0.969,-0.249));t/=np.linalg.norm(t);u=np.array((-t[1],t[0]));o0=np.array((-247.80,-69.47))
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=np.array([tuple(o.matrix_world@Vector(c)) for c in o.bound_box])
    if bb[:,0].max()<-232 or bb[:,0].min()>-205 or bb[:,1].max()<-92 or bb[:,1].min()>-70 or bb[:,2].min()>129: continue
    if len(o.data.vertices)>300000: print('P197c BIG',o.name,len(o.data.vertices)); continue
    P=np.empty(len(o.data.vertices)*3); o.data.vertices.foreach_get('co',P); P=P.reshape(-1,3)
    M=np.array(o.matrix_world); P=P@M[:3,:3].T+M[:3,3]
    Q=P[:,:2]-o0; s=Q@t; d=Q@u; m=(s>26)&(s<38)&(d>-13)&(d<-2)&(P[:,2]<129)
    if m.sum(): print('P197c',o.name,int(m.sum()),'z %.2f..%.2f'%(P[m,2].min(),P[m,2].max()),[x.name for x in o.data.materials if x][:3],flush=True)

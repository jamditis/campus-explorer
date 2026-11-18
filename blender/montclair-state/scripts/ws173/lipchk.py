import bpy, numpy as np
o=bpy.data.objects['WS163_walk_back_lawn_lip_S_UNVERIFIED']; mw=o.matrix_world; me=o.data
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
print('LIP nverts',len(me.vertices),'nfaces',len(me.polygons))
bad=0
for p in me.polygons:
    n=(mw.to_3x3()@p.normal).normalized(); c=mw@p.center
    if abs(n.z)<0.6:
        d=np.array((c.x,c.y))-A; bad+=1
        if bad<25: print('LIP steep',p.index,round(n.z,2),'s',round(float(d@N),2),'t',round(float(d@T),2),'z',round(c.z,2),[round((mw@me.vertices[v].co).z,2) for v in p.vertices])
print('LIP steep total',bad)
# vertex rows
vs=np.array([tuple(mw@v.co) for v in me.vertices]); d=vs[:,:2]-A; s=d@N; t=d@T
m=(t>-64)&(t<-59)
for i in np.argsort(t[m]): print('V',round(float(t[m][i]),2),round(float(s[m][i]),2),round(float(vs[m][i,2]),3))

import bpy, numpy as np
dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['Center for Computing and Information Science roof (LiDAR)']; me=o.evaluated_get(dg).data
P=[];Nz=[];A=[]
for p in me.polygons:
    c=p.center; P.append(tuple(c)); Nz.append(p.normal.z); A.append(p.area)
P=np.array(P);Nz=np.array(Nz);A=np.array(A)
t=0.4*P[:,0]+0.92*P[:,1]; n=0.92*P[:,0]-0.4*P[:,1]
for lo,hi,nl,nh in [(200,215.8,-83.5,-54),(222.7,236,-76,-54),(196,201,-60,-53)]:
    s=(t>lo)&(t<hi)&(n>nl)&(n<nh)
    z=P[s,2]; print('zone',lo,hi,nl,nh,'faces',s.sum(),'area',A[s].sum().round(1))
    h,e=np.histogram(z,bins=np.arange(137,157,1)); print('  zhist',list(zip(e[:-1].astype(int),h)))
    print('  steep(|nz|<0.5)',(abs(Nz[s])<0.5).sum(),'flat',(abs(Nz[s])>0.9).sum())
    # per n-band mean z
    for b in range(int(nl),int(nh),3):
        ss=s&(n>=b)&(n<b+3)
        if ss.any(): print('   n',b,'zmean',P[ss,2].mean().round(2),'zmin',P[ss,2].min().round(2),'zmax',P[ss,2].max().round(2),ss.sum())

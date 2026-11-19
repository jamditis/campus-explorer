# ws229 W53e: robust global ortho UV mapping (fit on central original terrain) and SE-region deviation map
import bpy,sys,numpy as np,collections
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data; uv=me.uv_layers['ortho'].data
n=len(me.loops); lv=np.zeros(n,dtype=np.int64); me.loops.foreach_get('vertex_index',lv)
co=np.zeros(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
U=np.zeros(n*2); uv.foreach_get('uv',U); U=U.reshape(-1,2); P=co[lv]
for name,(x0,x1,y0,y1) in {'central':(-200,0,-150,150),'NE':(0,140,0,240),'SW':(-240,-100,-240,-100)}.items():
    s=(P[:,0]>x0)&(P[:,0]<x1)&(P[:,1]>y0)&(P[:,1]<y1); M=np.c_[P[s,0],P[s,1],np.ones(s.sum())]
    cu=np.linalg.lstsq(M,U[s,0],rcond=None)[0]; cv=np.linalg.lstsq(M,U[s,1],rcond=None)[0]
    print('P229G fit',name,s.sum(),cu.round(7),cv.round(7),'res99',np.percentile(np.abs(M@cu-U[s,0]),99).round(5),np.percentile(np.abs(M@cv-U[s,1]),99).round(5),flush=True)
    if name=='central': CU,CV=cu,cv
E=np.hypot(np.c_[P[:,0],P[:,1],np.ones(n)]@CU-U[:,0], np.c_[P[:,0],P[:,1],np.ones(n)]@CV-U[:,1])*510
bad=E>2.0
c=collections.Counter(zip((P[bad,0]//25*25).astype(int),(P[bad,1]//25*25).astype(int)))
print('P229G loops off >2 m',bad.sum(),'of',n,flush=True)
print('P229G cells',sorted(c.items()),flush=True)
se=(P[:,0]>140)&(P[:,1]<-60)
print('P229G SE off m pct',np.percentile(E[se],[10,50,90,99]).round(1),flush=True)
np.save('/tmp/uvmap229.npy',np.r_[CU,CV])
sys.stdout.flush(); import os; os._exit(0)

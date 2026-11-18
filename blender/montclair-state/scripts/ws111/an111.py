import bpy,numpy as np
A=np.array([-244.8,-239.3]);B=np.array([-256.1,-271.6]);d=(B-A)/np.linalg.norm(B-A);n=np.array([d[1],-d[0]])
def P(o):
    co=np.array([o.matrix_world@v.co for v in o.data.vertices]); s=(co[:,0]-A[0])*d[0]+(co[:,1]-A[1])*d[1]; t=(co[:,0]-A[0])*n[0]+(co[:,1]-A[1])*n[1]; return co,s,t
for nm in bpy.data.objects.keys():
    if not any(k in nm for k in ('curb','carriageway','sidewalk','verge','to_NormalAve')): continue
    o=bpy.data.objects[nm]; co,s,t=P(o)
    m=(s>-6)&(s<14)
    print('A111',nm[:60],'n',m.sum(),'s',round(s[m].min(),2) if m.any() else None,round(s[m].max(),2) if m.any() else None)
    if 'WS102_CollegeAve_S_curb' in nm or 'WS110_CollegeAve_S_end_curb' in nm:
        mm=m&(s<3)
        for i in np.argsort(s[mm])[:]: 
            j=np.where(mm)[0][i]; print('  V',round(s[j],3),round(t[j],3),round(co[j,2],3))

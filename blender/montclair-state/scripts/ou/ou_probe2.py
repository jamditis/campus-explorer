import bpy
from mathutils import Vector
ob=bpy.data.objects['OR_base_course_Center for Environmental and Life Sciences wa']; me=ob.data; W=ob.matrix_world
B=[]
for b in range(len(me.vertices)//8):
    P=[W@me.vertices[i].co for i in range(8*b,8*b+8)]
    best=max(((P[j]-P[i]).to_2d().length,(P[j]-P[i]).to_2d()) for i in range(8) for j in range(i+1,8))
    u=best[1].normalized(); n=Vector((-u.y,u.x))
    us=[p.to_2d().dot(u) for p in P]; ns=[p.to_2d().dot(n) for p in P]
    B.append((u,n,min(us),max(us),min(ns),max(ns),best[0]))
for i in range(min(25,len(B)-1)):
    A=B[i]; C=B[i+1]; ang=A[0].angle(C[0]); 
    Cn=None
    print(i,'len %.2f th %.3f ang %.4f'%(A[6],A[5]-A[4],ang))
# general: any pair with ang<0.01 and close
cnt=0
for i in range(len(B)):
    for j in range(i+1,len(B)):
        A=B[i];C=B[j]
        if abs(A[0].dot(C[0]))<0.9995: continue
        # C's verts in A frame
        P=[W@me.vertices[k].co for k in range(8*j,8*j+8)]
        cu=[p.to_2d().dot(A[0]) for p in P]; cn=[p.to_2d().dot(A[1]) for p in P]
        lo=max(A[2],min(cu)); hi=min(A[3],max(cu))
        if hi>lo-0.01 and abs(min(cn)-A[4])<0.2:
            cnt+=1
            if cnt<12: print('PAIR',i,j,'ov %.3f dn %.4f %.4f'%(hi-lo,min(cn)-A[4],max(cn)-A[5]))
print('PAIRS',cnt,len(B))

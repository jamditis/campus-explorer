# qc: shared helper - find the Calcia wall faces that still hold a full-width shader-painted window (the qb_corner 'kept' set)
import bpy, math, json
from mathutils import Vector
def qc_find():
    o=bpy.data.objects['Calcia Hall walls']; me=o.data; mw=o.matrix_world
    uv=me.uv_layers['facade'].data; WT=float(o.get('win_top',99))
    UP,ULO,UHI,VOF,VP,VLO,VHI=2.4,0.75,1.65,0.1,4.4,0.6,3.8
    cen=sum((mw@v.co for v in me.vertices),Vector())/len(me.vertices)
    out=[]
    for p in me.polygons:
        if abs(p.normal.z)>0.3 or p.area<0.02 or p.material_index!=0: continue
        L=list(p.loop_indices); us=[uv[l].uv[0] for l in L]; vv=[uv[l].uv[1] for l in L]
        a,b=min(us),max(us); v0=max(min(vv),0.8); v1=min(max(vv),WT)
        if v1-v0<0.03: continue
        cols=[k for k in range(int((a-UHI)//UP)-1,int((b-ULO)//UP)+2) if a<=ULO+k*UP+0.01 and b>=UHI+k*UP-0.01]
        if not cols: continue
        rows=[]
        for js in range(-1,10):
            L0=max(VOF+VLO+js*VP,0.8); H0=min(VOF+VHI+js*VP,WT)
            if H0-L0<0.03: continue
            lo=max(v0,L0); hi=min(v1,H0)
            if hi-lo>0.03: rows.append((js,round(L0,3),round(H0,3),round(lo,3),round(hi,3)))
        if not rows: continue
        P=[mw@me.vertices[me.loops[l].vertex_index].co for l in L]; U=[uv[l].uv.copy() for l in L]
        best=None
        for i in range(len(L)):
            for j in range(i+1,len(L)):
                for k in range(j+1,len(L)):
                    A=(U[j]-U[i]); B=(U[k]-U[i]); det=A.x*B.y-A.y*B.x
                    if best is None or abs(det)>abs(best[0]): best=(det,i,j,k)
        # least-squares affine UV->3D over ALL corners (the best-triangle fit of pr/ps is wrong on skewed 8-corner cells)
        import numpy as np
        Uc=sum(U,Vector((0,0)))/len(U); Pc=sum(P,Vector())/len(P)
        M=np.array([[q.x-Uc.x,q.y-Uc.y] for q in U]); Y=np.array([list(q-Pc) for q in P])
        X,res,rk,sv=np.linalg.lstsq(M,Y,rcond=None); Wu=Vector(X[0]); Wv=Vector(X[1]); i=0
        R=max(((Pc+Wu*(U[t].x-Uc.x)+Wv*(U[t].y-Uc.y))-P[t]).length for t in range(len(P)))
        n=(mw.to_3x3()@p.normal); n.z=0; n.normalize()
        if ((mw@p.center)-cen).dot(n)<0: n=-n
        out.append(dict(idx=p.index,cols=cols,rows=rows,umin=a,umax=b,vmin=min(vv),vmax=max(vv),P0=Pc,U0=Uc.copy(),res=R,UV=[q.copy() for q in U],Wu=Wu,Wv=Wv,n=n,area=p.area,nv=len(L),c=mw@p.center))
    return out,WT

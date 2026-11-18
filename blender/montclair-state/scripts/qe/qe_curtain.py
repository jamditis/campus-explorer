# qe: flat stucco walls in front of the LiDAR roof's wrinkled vertical drapes (CCIS main bar above the lower east part and above the south annex),
# with windows. Runs inside qe_ccis.py context (needs col, box/quad helpers via exec). UNVERIFIED.
import math, numpy as np
fsall=[p for p in R.data.polygons if p.material_index==3]
def ang(p):
    n=R.matrix_world.to_3x3()@p.normal
    return None if abs(n.z)>0.7 else math.degrees(math.atan2(n.y,n.x))
groups={'east':(lambda a:-40<=a<=40, lambda c:True),'south':(lambda a:-170<=a<=-80, lambda c:c.y<200.5)}
cw=[]
for gname,(f,g) in groups.items():
    fs=[p for p in fsall if ang(p) is not None and f(ang(p)) and g(R.matrix_world@p.center)]
    if len(fs)<5: continue
    P=np.array([[ (R.matrix_world@p.center).x,(R.matrix_world@p.center).y] for p in fs]); Wt=np.array([p.area for p in fs])
    c=(P*Wt[:,None]).sum(0)/Wt.sum(); Q=P-c; C=(Q*Wt[:,None]).T@Q; ev,evec=np.linalg.eigh(C); d=evec[:,1]
    nrm=np.array([d[1],-d[0]]); cv=Vector((c[0],c[1]))
    ra=roof_at(cv+Vector(nrm)*3); rb=roof_at(cv-Vector(nrm)*3)
    if ra is not None and rb is not None and ra>rb: nrm=-nrm
    vids=set(i for p in fs for i in p.vertices)
    V=np.array([[ (R.matrix_world@R.data.vertices[i].co).x,(R.matrix_world@R.data.vertices[i].co).y] for i in vids])
    sd=(V-c)@nrm; along=(V-c)@d
    VZ=[(float((np.array([(R.matrix_world@R.data.vertices[i].co).x,(R.matrix_world@R.data.vertices[i].co).y])-c)@d),(R.matrix_world@R.data.vertices[i].co).z) for i in vids]
    off=float(np.percentile(sd,97))+0.08; u0,u1=float(along.min()),float(along.max())
    print('QE_CURTAIN',gname,len(fs),'c',c.round(2),'d',d.round(3),'n',nrm.round(3),'sd p3/p50/p97',np.percentile(sd,[3,50,97]).round(2),'u',round(u0,1),round(u1,1))
    if off-float(np.percentile(sd,3))>4.0: print('QE_CURTAIN skip spread'); continue
    D=Vector((d[0],d[1])); N2=Vector((nrm[0],nrm[1])); t=Vector((d[0],d[1],0)); n=Vector((nrm[0],nrm[1],0))
    def inside(q):
        r=False; m=len(poly)
        for a_ in range(m):
            A_,B_=poly[a_],poly[(a_+1)%m]
            if (A_.y>q.y)!=(B_.y>q.y) and q.x<(B_.x-A_.x)*(q.y-A_.y)/(B_.y-A_.y)+A_.x: r=not r
        return r
    while not inside(cv+D*u0+N2*(off+0.3)) and u0<u1: u0+=0.25
    while not inside(cv+D*u1+N2*(off+0.3)) and u1>u0: u1-=0.25
    us=list(np.arange(u0,u1+0.01,1.0))
    if us[-1]<u1: us.append(u1)
    bot=[];top=[]
    for u in us:
        p=cv+D*u+N2*off
        lo=roof_at(p+N2*1.2); hs=[h_ for h_ in (roof_at(p-N2*k_) for k_ in (1.0,2.0,3.0,4.0,5.0)) if h_]; hi=(max(hs)-0.08) if hs else None
        cz=[z_ for (a_,z_) in VZ if abs(a_-u)<1.5]
        if hi and cz: hi=min(hi,max(cz)+0.1)
        bot.append((lo if lo else 145.6)-0.25); top.append(hi if hi else 153.0)
    # wall strip mesh
    bm2=bmesh.new(); vb=[];vt=[]
    for u,zb,zt in zip(us,bot,top):
        p=cv+D*u+N2*off; vb.append(bm2.verts.new((p.x,p.y,zb))); vt.append(bm2.verts.new((p.x,p.y,max(zt,zb+0.5))))
    for k in range(len(us)-1): bm2.faces.new((vb[k],vb[k+1],vt[k+1],vt[k]))
    bmesh.ops.recalc_face_normals(bm2,faces=bm2.faces)
    me2=bpy.data.meshes.new('QE_CCIS_drape_cover_wall_'+gname); bm2.to_mesh(me2); bm2.free(); me2.materials.append(nw)
    for pl in me2.polygons:
        if Vector((pl.normal.x,pl.normal.y,0)).dot(n)<0: pl.flip()
    ob2=bpy.data.objects.new('QE_CCIS_drape_cover_wall_%s_UNVERIFIED'%gname,me2); ob2['qe']=1; col.objects.link(ob2); cw.append(ob2)
    # windows on it
    L=u1-u0; k=max(1,int((L-1.6)//SP)); o0=(L-(k-1)*SP)/2
    nw_=0
    for j in range(k):
        u=u0+o0+j*SP; i0=min(range(len(us)),key=lambda q:abs(us[q]-u)); zb=bot[i0]+0.25; zt=min(top[max(0,i0-1):i0+2])
        p=cv+D*u+N2*(off+0.002)
        for s in range(5):
            sill=zb+1.0+s*ST
            if sill+WH>zt-0.8: break
            window(p,t,n,sill,WW,WH); nw_+=1
    print('QE_CURTAIN windows',gname,nw_)
    if os.environ.get('TESTCAM')=='1' and gname=='south':
        q=cv+N2*28; cd_=bpy.data.cameras.new('QE_CAM_test_curtain'); cd_.lens=35; cc=bpy.data.objects.new('QE_CAM_test_curtain',cd_); cc['qe']=1; col.objects.link(cc)
        cc.location=(q.x,q.y,152); cc.rotation_euler=(Vector((cv.x,cv.y,148))-Vector((q.x,q.y,152))).to_track_quat('-Z','Y').to_euler()
        print('QE_testcam',[(round(u,1),round(b,2),round(t_,2)) for u,b,t_ in zip(us,bot,top)])

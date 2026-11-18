# nt furniture library (Oct 30 2026, session nt): one-piece moulded shell chair (dished seat + wrapped back, 7 mm shell) on splayed tube legs.
# Local frame as nr: floor z=0, sitter faces -X, back on +X. Generic design, UNVERIFIED (no photo of the CCOM cafe chairs).
import bmesh, mathutils, math
V=mathutils.Vector
def _cr(p0,p1,p2,p3,t):
    t2=t*t;t3=t2*t
    return 0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t2+(-p0+3*p1-3*p2+p3)*t3)
def _profile(H,n):
    C=[V(p) for p in ((-0.26,H-0.06),(-0.225,H-0.028),(-0.19,H-0.002),(-0.05,H-0.016),(0.10,H-0.010),(0.185,H+0.035),(0.215,H+0.16),(0.245,H+0.30),(0.265,H+0.41),(0.27,H+0.45))]
    pts=[]
    segs=len(C)-3
    for s in range(segs):
        for k in range(n):
            pts.append(_cr(C[s],C[s+1],C[s+2],C[s+3],k/n))
    pts.append(C[-2]); return pts
def shell_chair(bm,H=0.45,nu=14,nv=5,thick=0.007):
    """mi0 = shell (seat/back colour), mi1 = charcoal tube, mi2 = black glide"""
    P=_profile(H,nv); N=len(P); rows=[]
    for i,p in enumerate(P):
        a=P[max(i-1,0)]; b=P[min(i+1,N-1)]; t=(b-a).normalized(); nrm=V((-t.y,t.x))   # inward (up on seat, -X on back)
        f=i/(N-1)
        hw=0.225-0.025*math.sin(math.pi*min(1,max(0,(f-0.35)/0.4)))     # waist narrowing between seat and back
        cup=0.022 if f<0.45 else 0.022+0.04*min(1,(f-0.45)/0.3)         # side rise: dished seat, wrapped back
        row=[]
        for j in range(nu+1):
            u=-1+2*j/nu; q=p+nrm*(cup*u*u)
            row.append(bm.verts.new((q.x,u*hw,q.y)))
        rows.append(row)
    fs=[]
    for i in range(N-1):
        for j in range(nu): fs.append(bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j])))
    for f in fs: f.material_index=0
    bmesh.ops.recalc_face_normals(bm,faces=fs)
    r=bmesh.ops.solidify(bm,geom=fs,thickness=thick)
    for f in r['geom']:
        if isinstance(f,bmesh.types.BMFace): f.material_index=0
    # legs: 4 splayed tubes from a small under-seat frame + glides; rear legs also brace the back
    def tube(p0,p1,rr,mi,seg=10):
        p0=V(p0);p1=V(p1);d=p1-p0;L=d.length
        res=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=rr,radius2=rr,depth=L)
        q=V((0,0,1)).rotation_difference(d.normalized()); M=mathutils.Matrix.Translation((p0+p1)/2)@q.to_matrix().to_4x4()
        bmesh.ops.transform(bm,matrix=M,verts=res['verts'])
        for f_ in {f_ for v in res['verts'] for f_ in v.link_faces}: f_.material_index=mi
    zt=H-0.03
    for x in (-0.15,0.13):
        for y in (-0.15,0.15):
            b=(x*1.25,y*1.22,0.012)
            tube((x,y,zt),b,0.0095,1); tube((b[0],b[1],0.0),(b[0],b[1],0.013),0.012,2,8)
    tube((-0.15,-0.15,zt),(-0.15,0.15,zt),0.008,1); tube((0.13,-0.15,zt),(0.13,0.15,zt),0.008,1)   # under-seat cross rails (mount plate)
    tube((-0.15,-0.15,zt),(0.13,-0.15,zt),0.008,1); tube((-0.15,0.15,zt),(0.13,0.15,zt),0.008,1)
    for f in bm.faces: f.smooth=True

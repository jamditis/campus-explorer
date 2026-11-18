# ws214a W36: WS70 S-berm W tip -> straight end at the WS69 curb end + L curb return with rounded nose,
# asphalt under-fill patch (KY material, 6 mm under the max adjacent paving) over the trimmed tip + curb-end gap,
# WS204 lowered 15 mm where it lies under KY (coincident seam, KY wins).
import bpy, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next((o for o in bpy.data.objects if o.name.startswith(p)),None)
B=ob('WS70_gap_strip_grass_berms'); C=ob('WS69_CollegeAve_gap_strip_curbs'); KY=ob('KY_college_ave_carriageway_asphalt'); W4=ob('WS204_CollegeAve_lot_entrance_asphalt'); W67=ob('WS67_CollegeAve_gap_asphalt')
if not all([B,C,KY,W4,W67]) or ob('WS214_'): print('F214 skip',[x is None for x in (B,C,KY,W4,W67)],flush=True)
else:
    P0=Vector((-255.49,-56.44)); d=Vector((3.0,-1.64)).normalized(); n=Vector((-d.y,d.x))  # n points N (lane side)
    if n.y<0: n=-n
    st=lambda x,y:((Vector((x,y))-P0).dot(d),(Vector((x,y))-P0).dot(n))
    xy=lambda s,t:P0+d*s+n*t
    S0=0.0  # curb end (s of the curb W end face)
    def bvh(o): M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
    TP=[bvh(o) for o in (KY,W4,W67)]
    def pz(x,y,TT=TP):
        best=None
        for t in TT:
            h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300)
            if h[0] is not None and (best is None or h[0].z>best): best=h[0].z
        return best
    # --- 1 berm tip: verts of the S berm W of the curb end -> onto the end line s=-0.15 (behind the return curb)
    me=B.data; M=B.matrix_world; Mi=M.inverted(); Wv=[M@v.co for v in me.vertices]
    SE=-0.10; mv=[]; rg=[]
    # asphalt plane around the tip (KY/WS204 samples outside the berm), least squares z=a+bx+cy
    import numpy as np
    TBb=bvh(B); A=[]
    for i in range(-12,13):
        for j in range(-12,13):
            x=-256.0+0.25*i; y=-57.3+0.25*j
            if TBb.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300)[0] is not None: continue
            z=pz(x,y)
            if z is not None: A.append((1,x,y,z))
    A=np.array(A); cf=np.linalg.lstsq(A[:,:3],A[:,3],rcond=None)[0]
    ap=lambda x,y: cf[0]+cf[1]*x+cf[2]*y
    qc=xy(0.4,0.075); CZ=pz(qc.x,qc.y,[bvh(C)])
    tips=[st(w.x,w.y)[1] for w in Wv]
    TM=min(t for (w,t) in zip(Wv,tips) if t>-4 and -1.5<st(w.x,w.y)[0]<1.5)
    for i,w in enumerate(Wv):
        s,t=st(w.x,w.y)
        if t<0.05 and t>-4 and -1.5<s<1.5:
            rg.append(i)
            if s<0.15: mv.append(i)
    for i in rg:
        w=Wv[i]; s,t=st(w.x,w.y)
        p=xy(SE,t) if i in mv else Vector((w.x,w.y))
        u=min(max(t/TM,0),1); f=1-u*u*(3-2*u)
        pc=xy(min(s,0.2),0.0)
        ar=pz(p.x,p.y); ar=ar if ar is not None else ap(p.x,p.y)
        zn=ar+0.01+max(CZ-0.01-ap(pc.x,pc.y)-0.01,0)*f
        wb=min(max((s-0.7)/0.8,0),1); z=zn*(1-wb)+w.z*wb
        a=pz(p.x,p.y); z=max(z,(a if a is not None else z)+0.01)
        me.vertices[i].co=Mi@Vector((p.x,p.y,z))
    nse=0
    for i,w in enumerate(Wv):
        if i in rg: continue
        s_,t_=st(w.x,w.y)
        if -4<t_<-1.6 and 1.5<=s_<8:
            a=pz(w.x,w.y)
            if a is not None and w.z<a+0.008: me.vertices[i].co=Mi@Vector((w.x,w.y,a+0.008)); nse+=1
    print('F214 S-edge lifted',nse,flush=True)
    print('F214 plane',[round(c,4) for c in cf],'CZ',round(CZ,3),'TM',round(TM,2),'regraded',len(rg),flush=True)
    me.update()
    tmin=min([st(Wv[i].x,Wv[i].y)[1] for i in mv]+[0])
    # --- 2 curb return along s in [SE-0.15,SE], t from tmin to 0.15, rounded outer corner r=0.3 at the lane side
    R=0.30; pts=[]
    # outer outline (W/N face), from S end up, round corner, then E along the curb N face to s=0.25 (overlaps the old curb end)
    cx,cy=SE-0.15+R,0.15-R
    nst=max(2,int((cy-tmin)/0.2))
    for k in range(nst): pts.append((SE-0.15,tmin+(cy-tmin)*k/nst))
    for k in range(0,9):
        a=math.pi-k*(math.pi/2)/8; pts.append((cx+R*math.cos(a),cy+R*math.sin(a)))
    pts.append((0.02,0.15)); pts.append((0.02,0.0)); pts.append((SE,0.0))
    for k in range(1,nst+1): pts.append((SE,0.0+(tmin-0.0)*k/nst))
    TB=[bvh(B)]
    qc=xy(0.4,0.075); CZ=pz(qc.x,qc.y,[bvh(C)])
    def topz(s,t):
        p=xy(s,t); a=pz(p.x,p.y) or 125.0
        if t>=-0.02: return CZ if CZ else a+0.15
        q=xy(SE+0.05,t); b=pz(q.x,q.y,TB)
        z=max((b if b is not None else a)+0.01,a+0.02)
        k=min(1.0,max(0.0,(t-tmin)/0.5)); return a+0.012+(z-a-0.012)*k
    bm=bmesh.new(); top=[]; bot=[]
    for s,t in pts:
        p=xy(s,t); zt=topz(s,t); a=pz(p.x,p.y) or zt-0.15
        top.append(bm.verts.new((p.x,p.y,zt))); bot.append(bm.verts.new((p.x,p.y,min(a,zt)-0.05)))
    N=len(pts)
    try: bm.faces.new(top)
    except Exception as e: print('F214 topface',e)
    for i in range(N):
        j=(i+1)%N
        try: bm.faces.new((bot[i],bot[j],top[j],top[i]))
        except Exception: pass
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    cm=bpy.data.meshes.new('WS214_curb_nose'); bm.to_mesh(cm); bm.free()
    co=bpy.data.objects.new('WS214_WS69_berm_tip_curb_return_nose_ortho2020_UNVERIFIED',cm); cm.materials.append(C.data.materials[0])
    for c in C.users_collection: c.objects.link(co)
    # --- 3 under-fill asphalt patch (0.2 m grid in s,t) s -2.6..0.5, t tmin-0.8..1.2
    bm=bmesh.new(); G={}; ss=[-2.6+0.2*i for i in range(16)]; tt=[tmin-0.8+0.2*j for j in range(int((1.2-tmin+0.8)/0.2)+1)]
    samp=[]
    for s in ss:
        for t in tt:
            p=xy(s,t); a=pz(p.x,p.y); 
            if a is not None: samp.append((p.x,p.y,a))
    for i,s in enumerate(ss):
        for j,t in enumerate(tt):
            p=xy(s,t); a=pz(p.x,p.y)
            if a is None:
                ws=[(1/((p.x-x)**2+(p.y-y)**2+1e-4),z) for x,y,z in samp if (p.x-x)**2+(p.y-y)**2<1.0]
                a=sum(w*z for w,z in ws)/sum(w for w,z in ws) if ws else 125.0
            G[i,j]=bm.verts.new((p.x,p.y,a-0.006))
    for i in range(len(ss)-1):
        for j in range(len(tt)-1): bm.faces.new((G[i,j],G[i+1,j],G[i+1,j+1],G[i,j+1]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    for f in bm.faces:
        if f.normal.z<0: f.normal_flip()
    pm=bpy.data.meshes.new('WS214_fill'); bm.to_mesh(pm); bm.free()
    po=bpy.data.objects.new('WS214_berm_tip_gap_asphalt_underfill_ortho2020',pm); pm.materials.append(KY.data.materials[0])
    for c in KY.users_collection: c.objects.link(po)
    # --- 4 WS204 under KY: lower 15 mm (only within the W36 box)
    tk=bvh(KY); me=W4.data; M=W4.matrix_world; Mi=M.inverted(); nl=0
    for v in me.vertices:
        w=M@v.co
        if not (-262<w.x<-250 and -62<w.y<-55): continue
        h=tk.ray_cast(Vector((w.x,w.y,200)),Vector((0,0,-1)),300)
        if h[0] is not None and abs(h[0].z-w.z)<0.03: w.z=h[0].z-0.015; v.co=Mi@w; nl+=1
    me.update()
    print('F214 a moved berm',len(mv),'tmin',round(tmin,2),'curb pts',N,'fill',len(ss)*len(tt),'WS204 lowered',nl,flush=True)

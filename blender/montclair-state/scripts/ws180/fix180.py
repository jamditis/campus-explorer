# ws180: UNIFY #87 follow-up to fix179 (run right after fix179 in the same session). Review of the ws180a subset close-up showed
# (a) a sawtooth of old WS110 S-curb faces left at the foot of the E return (fix179 deletes by face centroid only),
# (b) a dark notch at the W return/pole: fix179 built the return curbs with the 0.15 m width offset along t, which is ZERO width
#     where the arc is tangent to Normal Ave, and the old 15 cm Normal Ave curb met the 1.5 cm ramp landing with a vertical step.
# Fix: snap every remaining old curb/walk/lip vertex that lies inside the new asphalt footprint onto the footprint boundary (along t),
# drop the old Normal Ave curb top to the ramp-landing height over 1.5 m before each tangent point (curb ramp transition),
# and rebuild both return curbs with the 0.15 m width along the true outward normal and a continuous reveal profile
# (landing 0.015 across the walk band, eased to the LiDAR reveal (E 0.15 / W 0.05) over the next 1.0 m south).
import bpy, bmesh, math, numpy as np
from mathutils import Vector
def boundary_t(s,t):
    f=sf(t)
    if t<=0.5*(TW+TE):
        cs=f-RW
        if s>=cs: return TW+math.sqrt(max(RW*RW-(s-cs)**2,0.0))
        return wedge(s)
    else:
        cs=f-RE
        if s>=cs: return TE-math.sqrt(max(RE*RE-(s-cs)**2,0.0))
        return EEDGE
ns=0
for p in ('WS110_NormalAve_curb_W11p3','WS110_NormalAve_sidewalk_ws85','WS175_WS110_walk_back_lawn_lip_S'):
    for o in obs(p):
        mw=o.matrix_world; mi=mw.inverted(); k=0
        for v in o.data.vertices:
            w=mw@v.co; s,t=st(w.x,w.y)
            if s>-5: continue
            if not (inside(s,t) or ('curb' not in p and TW<t<TE and sf(t)-3.6<s<sf(t)-0.05)): continue   # also pull the walk/lip corner rows out to the arc (paved landing, no lawn wedge)
            tb=boundary_t(s,t)
            for _ in range(3): tb=boundary_t(s,tb)
            x,y=xy(s,tb); w.x,w.y=x,y; v.co=mi@w; k+=1
        o.data.update(); ns+=k
        print('FIX180 snapped',o.name[:60],k,flush=True)
# old Normal Ave curb: delete the 2.05 m segments that touch the mouth (they crossed the return arcs diagonally -> sawtooth / notch);
# the new return curbs continue along Normal Ave back to the last kept station as a curb-ramp transition (old reveal -> 0.015 landing).
J={}
for o in obs('WS110_NormalAve_curb_W11p3'):
    mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data); kill=[]
    for fc in bm.faces:
        hit=False
        for v in fc.verts:
            w=mw@v.co; s,t=st(w.x,w.y)
            if TW+0.1<t<TE+0.1 and sf(t)-1.0<s<sf(t)+0.5: hit=True   # W: keep the 1.27-3.32 segment (outside the arc), ramp its top instead
        if hit: kill.append(fc)
    bmesh.ops.delete(bm,geom=kill,context='FACES')
    for v in bm.verts:
        w=mw@v.co; s,t=st(w.x,w.y)
        if not (sf(t)-1.0<s<sf(t)+0.5) or not (TW-4<t<TE+4): continue
        side='W' if t<0.5*(TW+TE) else 'E'
        if side is None: continue
        J.setdefault(side,[]).append((t,s-sf(t),w.z))
    tjw=max([x[0] for x in J.get('W',[])] or [None])
    nlw=0
    if tjw is not None:
        for v in bm.verts:
            w=mw@v.co; s,t=st(w.x,w.y)
            if abs(t-tjw)<0.05 and sf(t)-1.0<s<sf(t)+0.5:
                zg=top(ROAD,*xy(sf(t)+0.25,t)) or w.z
                if w.z>zg+0.03: w.z=zg+0.019; v.co=mw.inverted()@w; nlw+=1
        J['W']=[(a,b,(min(c,max(x[2] for x in J['W'] if abs(x[0]-tjw)<0.05 and x[2]<c+1)) if abs(a-tjw)<0.05 else c)) for a,b,c in J['W']]
    print('FIX180 W joint top verts lowered to landing',nlw,flush=True)
    bm.to_mesh(o.data); o.data.update(); bm.free()
    print('FIX180 old curb faces deleted',len(kill),flush=True)
JT={}
for side,L in J.items():
    tj=max(x[0] for x in L) if side=='W' else min(x[0] for x in L)
    pts=[x for x in L if abs(x[0]-tj)<0.05]; JT[side]=(tj,min(x[1] for x in pts),max(x[1] for x in pts),max(x[2] for x in pts))
    print('FIX180 joint',side,'t %.2f front %.2f back %.2f top %.3f'%(tj,max(x[1] for x in pts),min(x[1] for x in pts),max(x[2] for x in pts)),flush=True)
def gut(t):
    z=top(ROAD,*xy(sf(t)+0.25,t)); return z if z is not None else zroad(sf(t)+0.1,min(max(t,TW),TE))
for o in [o for o in OB if o.name.startswith('WS179_CollegeAve_S_leg_curb_')]: OB.remove(o)
for side,rev in (('W',0.05),('E',0.15)):
    tj,back,front,ztop=JT[side]; tt=TW if side=='W' else TE
    if side=='W': ztop=gut(tj)+0.015
    n=max(int(abs(tt-tj)/0.25),2); tail=[]
    for k in range(n):
        t=tj+(tt-tj)*k/n; u=k/n; uu=u*u*(3-2*u)
        tail.append((sf(t)+front*(1-u),t,'tail',(ztop-gut(tj))*(1-uu)+0.015*uu))
    P=tail+[(s,t,'ret',None) for s,t in edge_pts(side)]
    XY=[np.array(xy(s,t)) for s,t,_,_ in P]; bm=bmesh.new(); rows=[]; W=front-back
    for k,(s,t,kind,rt) in enumerate(P):
        a=XY[max(k-1,0)]; b=XY[min(k+1,len(XY)-1)]; tg=(b-a); tg/=np.linalg.norm(tg); nrm=np.array([-tg[1],tg[0]])
        q=XY[k]+nrm*0.3; sq,tq=st(*q)
        if inside(sq,tq) or sq>sf(tq): nrm=-nrm
        if kind=='tail': r=rt; zb=gut(t)
        else:
            dd=sf(t)-s
            if dd<2.1: r=0.015
            elif dd<3.1: u=(dd-2.1); u=u*u*(3-2*u); r=0.015+(rev-0.015)*u
            else: r=rev
            zb=zroad(s,t)+0.004
        pa=XY[k]; pb=XY[k]+nrm*W
        rows.append([bm.verts.new((pa[0],pa[1],zb-0.25)),bm.verts.new((pa[0],pa[1],zb+r)),bm.verts.new((pb[0],pb[1],zb+r)),bm.verts.new((pb[0],pb[1],zb-0.25))])
    for a,b in zip(rows[:-1],rows[1:]):
        for k in range(3): bm.faces.new((a[k],a[k+1],b[k+1],b[k]))
    bm.faces.new(rows[0]); bm.faces.new(rows[-1][::-1])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    link('WS179_CollegeAve_S_leg_curb_%s_reveal%dcm_ramped_LiDAR2023_UNVERIFIED'%(side,round(rev*100)),bm,conc)
print('FIX180 curbs rebuilt (normals, ramp transitions, end caps)',flush=True)
# carriageway rebuild: fix179 clipped the 0.25 m grid by face centroid -> a staircase edge inside the return arcs (dark teeth at the
# E return foot) and its N row sat 0.3 m into the WS110 gutter a few mm proud (dark seam line). Rebuild: faces with centroid inside
# the footprint grown by 0.2 m (the staircase now hides under the 0.30 m curbs), first row tucked 1 cm under the WS110 carriageway.
old=[o for o in OB if o.name.startswith('WS179_CollegeAve_S_leg_carriageway')]
for o in old: OB.remove(o)
ss=np.concatenate([[sf(TE)+0.10],np.arange(sf(TE)-0.10,S_END-0.2-1e-6,-G)]); bm=bmesh.new(); V={}
for i,s in enumerate(ss):
    for j,t in enumerate(ts):
        x,y=xy(s,t); z=zroad(min(s,sf(t)-0.05),t)+0.004
        if s>sf(t)-0.07: z=gut(min(max(t,TW),TE)) if False else (top(ROAD,x,y) or z)-0.010
        V[i,j]=bm.verts.new((x,y,z))
nf=0
for i in range(len(ss)-1):
    for j in range(len(ts)-1):
        c=(0.5*(ss[i]+ss[i+1]),0.5*(ts[j]+ts[j+1]))
        if inside(c[0],c[1],pad=0.2) or (i==0 and TW-0.2<c[1]<TE+0.2): bm.faces.new((V[i,j],V[i,j+1],V[i+1,j+1],V[i+1,j])); nf+=1
for v in [v for v in bm.verts if not v.link_faces]: bm.verts.remove(v)
car=link('WS179_CollegeAve_S_leg_carriageway_OSM232846669_LiDAR2023_UNVERIFIEDreturns',bm,asph); print('FIX180 carriageway rebuilt faces',nf,flush=True)
CAR=bvh([car]); ng=0
for p in ('WS110_ground_patch','WS175_WS110_walk_back_lawn_lip_S','WS163_ground_patch_W','WS172_frontyards','WS163_walk_back_lawn_lip_S'):
    for o in obs(p):
        mw=o.matrix_world; mi=mw.inverted(); k=0
        for v in o.data.vertices:
            w=mw@v.co; s,t=st(w.x,w.y)
            if not inside(s,t,pad=0.6): continue
            zt=top(CAR,w.x,w.y)
            if zt is None: continue
            if w.z>zt-0.05: w.z=zt-0.05; v.co=mi@w; k+=1
        o.data.update(); ng+=k
print('FIX180 ground pushed under',ng,flush=True)

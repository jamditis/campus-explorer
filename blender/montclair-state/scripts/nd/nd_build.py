# Session nd (Oct 30 2026 ~6:30 AM ET): NJ PBS studio follow-up (Joe's Oct 29 10:45 PM correction). ALL UNVERIFIED.
# 1) gaffer tape strips across the my floor camera cables where the cross-aisles (desk U <-> set) cross them, tented over each cable
# 2) a few worn/lifted tape ends (curled corner + scuffed lighter tape material)
# 3) DMX terminator plug at the far end of each grid DMX run (nc)
import bpy, bmesh, math, os, json
from mathutils import Vector
MODE=os.environ.get('ND_MODE','TEST'); SES='nd'; COLN='MS_CCOM_newsroom_studio_detail6_20261030nd'
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012; Z=Vector((0,0,1))
def P(u,t,z): return d*u+n*(C0+T0+t)+Vector((0,0,z))
def UT(v): return v.dot(d), v.dot(n)-(C0+T0)
O=bpy.data.objects; mats=bpy.data.materials; sc=bpy.context.scene
def mat(name,col,rough=0.6,metal=0.0):
    m=mats.get(name)
    if m: return m
    m=mats.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*col,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    m['msu_tag_session']=SES; m['status']='UNVERIFIED'; return m
M_TAPE=mat('ND_gaffer_tape_black_matte_UNVERIFIED',(0.025,0.025,0.027),0.85)
M_WORN=mat('ND_gaffer_tape_black_worn_scuffed_UNVERIFIED',(0.075,0.072,0.07),0.92)
M_TERM=mat('ND_dmx_terminator_body_black_UNVERIFIED',(0.02,0.02,0.022),0.4)
M_RED=mat('ND_dmx_terminator_red_band_UNVERIFIED',(0.5,0.02,0.02),0.5)
M_MET=mat('ND_dmx_terminator_xlr_shell_steel_UNVERIFIED',(0.7,0.7,0.72),0.3,0.9)
col=bpy.data.collections.get(COLN)
if col is None: col=bpy.data.collections.new(COLN); sc.collection.children.link(col)
col['msu_tag_session']=SES
SRC="Joe correction Oct 29 10:45 PM (studio exists); tape/terminators typical broadcast practice, no photo -> UNVERIFIED"
def newobj(name,bm,mlist,shadow=True):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mlist: me.materials.append(m)
    o=bpy.data.objects.new(name,me); col.objects.link(o)
    o['msu_tag_session']=SES; o['status']='UNVERIFIED'; o['source']=SRC
    if not shadow: o.visible_shadow=False
    return o
# ---- cable centrelines: same Catmull-Rom as scripts/my/my_build.py ----
UA=-18.04+0.35; ZF=137.41; TM=-9.8
def cr(p0,p1,p2,p3,s):
    s2,s3=s*s,s*s*s
    return 0.5*((2*p1)+(-p0+p2)*s+(2*p0-5*p1+4*p2-p3)*s2+(-p0+3*p1-3*p2+p3)*s3)
def pts(ctrl):
    ctrl=[Vector((u,t,0)) for u,t in ctrl]; ctrl=[ctrl[0]]+ctrl+[ctrl[-1]]; out=[]
    for i in range(1,len(ctrl)-2):
        for k in range(16): out.append(cr(ctrl[i-1],ctrl[i],ctrl[i+1],ctrl[i+2],k/16))
    out.append(ctrl[-2]); return out
cables=[]; pu=UA+6.3
for i,t in enumerate((-4.6,-6.2,-7.8)):
    ue=UA+6.75+i*0.16
    cables.append((pts([(pu+0.30,t),(pu+0.55,t-0.25),(ue,t-0.6),(ue-0.05,(t-0.6+TM)/2),(ue,TM+0.35)]),0.0065))
cables.append((pts([(UA+7.4,-2.9),(UA+7.15,-3.4),(UA+7.1,-4.0),(UA+7.0,-5.4),(UA+7.15,-7.0),(UA+7.2,TM+0.38)]),0.0055))
def cross_u(pl,tc):
    for a,b in zip(pl,pl[1:]):
        if (a.y-tc)*(b.y-tc)<=0 and abs(b.y-a.y)>1e-9:
            s=(tc-a.y)/(b.y-a.y); return a.x+s*(b.x-a.x)
    return None
dg=bpy.context.evaluated_depsgraph_get(); CAB='CCOM newsroom camera floor cables (my)'
OKF={'CCOM newsroom studio floor (raised access, mw)',CAB}
W=0.024; TH=0.0011; log=[]
def hgt(u,hits):
    h=0.0
    for uc,r in hits:
        dx=abs(u-uc)
        if dx<r: h=max(h,r+math.sqrt(r*r-dx*dx))
        elif dx<r+0.03: h=max(h,2*r*(1-(dx-r)/0.03)*0.85)
    return h
bmT=bmesh.new(); bmW=bmesh.new(); placed=0
def strip(bm,tc,u0,u1,hits,curl=None):
    """tape strip along u (perpendicular to the cables), width 2W in t, tented over each cable; curl=('lo'|'hi',len,lift) lifts one end"""
    N=max(8,int((u1-u0)/0.006)); top=[]; bot=[]
    for i in range(N+1):
        u=u0+(u1-u0)*i/N; z=ZF+0.0008+hgt(u,hits)
        if curl:
            end,ln,lift=curl; e=(u-u0) if end=='lo' else (u1-u)
            if e<ln: z+=lift*((ln-e)/ln)**2
        top.append([bm.verts.new(P(u,tc+s*W,z+TH)) for s in (-1,1)]); bot.append([bm.verts.new(P(u,tc+s*W,z)) for s in (-1,1)])
    for i in range(N):
        a,b=top[i],top[i+1]; bm.faces.new([a[0],b[0],b[1],a[1]])
        a,b=bot[i],bot[i+1]; bm.faces.new([a[1],b[1],b[0],a[0]])
        bm.faces.new([bot[i][0],bot[i+1][0],top[i+1][0],top[i][0]]); bm.faces.new([top[i][1],top[i+1][1],bot[i+1][1],bot[i][1]])
    bm.faces.new([bot[0][0],top[0][0],top[0][1],bot[0][1]]); bm.faces.new([bot[N][1],top[N][1],top[N][0],bot[N][0]])
def clear(tc,u0,u1):
    for i in range(int((u1-u0)/0.03)+1):
        u=u0+(u1-u0)*i/int((u1-u0)/0.03)
        for s in (-1,0,1):
            q=P(u,tc+s*W,0); hit,loc,nor,idx,ob,mtx=sc.ray_cast(dg,Vector((q.x,q.y,137.95)),Vector((0,0,-1)))
            if not hit or ob.name not in OKF: return ob.name if hit else 'nohit'
    return None
# cross-aisle positions (t) between the U desk west end and the set: avoid the mz cable ramp (t ~ -8.4..-9.4) and the pedestal bases
TCS=[-3.55,-5.35,-6.95]
worn=0
for tc in TCS:
    hits=[(u,r) for pl,r in cables for u in [cross_u(pl,tc)] if u is not None]
    if not hits: continue
    hits.sort(); u0=hits[0][0]-0.16; u1=hits[-1][0]+0.16
    bad=clear(tc,u0,u1)
    if bad: log.append(('SKIP',tc,bad)); continue
    # main strip; every second crossing gets a lifted/worn end, plus a short worn patch overlap
    if tc==-5.35:   # lifted, scuffed far end
        strip(bmT,tc,u0,u1-0.06,hits); strip(bmW,tc,u1-0.0605,u1,hits,curl=('hi',0.055,0.0075)); worn+=1
    elif tc==-6.95: # lifted, scuffed near end
        strip(bmW,tc,u0,u0+0.0605,hits,curl=('lo',0.05,0.006)); strip(bmT,tc,u0+0.06,u1,hits); worn+=1
    else:
        strip(bmT,tc,u0,u1,hits)
    placed+=1; log.append(('TAPE',tc,round(u0,2),round(u1,2),len(hits)))
# one extra worn, short double-wrap patch on the tripod cable near its start (scuffed, both ends flat)
tc=-4.45; hits=[(u,r) for pl,r in cables[3:] for u in [cross_u(pl,tc)] if u is not None]
if hits and not clear(tc,hits[0][0]-0.09,hits[0][0]+0.09):
    strip(bmW,tc,hits[0][0]-0.09,hits[0][0]+0.09,hits); log.append(('WORNPATCH',tc)); worn+=1
print('TAPELOG',log,'placed',placed,'worn',worn)
newobj('CCOM newsroom floor cable gaffer tape crossings (nd)',bmT,[M_TAPE],shadow=False)
newobj('CCOM newsroom floor cable gaffer tape worn lifted ends (nd)',bmW,[M_WORN],shadow=False)
# ---------- DMX terminators at the far end of each nc grid DMX run ----------
def tube(bm,pts_,r,k=10,mi=0):
    pts_=[Vector(p) for p in pts_]; rings=[]
    for i,p in enumerate(pts_):
        a=(pts_[min(i+1,len(pts_)-1)]-pts_[max(i-1,0)]).normalized(); ref=Z if abs(a.dot(Z))<0.9 else d
        x=a.cross(ref).normalized(); y=a.cross(x).normalized()
        rings.append([bm.verts.new(p+r*(math.cos(2*math.pi*j/k)*x+math.sin(2*math.pi*j/k)*y)) for j in range(k)])
    for A,B in zip(rings,rings[1:]):
        for j in range(k):
            f=bm.faces.new([A[j],A[(j+1)%k],B[(j+1)%k],B[j]]); f.material_index=mi; f.smooth=True
    for R in (rings[0],rings[-1][::-1]):
        f=bm.faces.new(R[::-1]); f.material_index=mi
sp=O['CCOM newsroom grid spots (mx, GN instances)']; spots=[UT(sp.matrix_world@v.co) for v in sp.data.vertices]
boxes=[(-14.19,-2.5),(-14.19,-5.0),(-14.19,-7.5),(-6.69,-2.5),(-6.69,-7.5)]
bmX=bmesh.new(); nterm=0; ul=-0.047; zl=145.515; ub=-14.19
for tb in sorted({b[1] for b in boxes}):
    on=sorted([s_ for s_ in spots if abs(s_[1]-tb)<0.1])
    if not on: continue
    hi=max(on[-1][0],ub)+0.30
    # nc run end dips to (hi, zl-0.02); the terminator plug hangs from it: XLR shell + body + red band + short strain relief
    e=P(hi,tb+ul,zl-0.02)
    tube(bmX,[e+Z*0.004,e-Z*0.012],0.0050,10,0)                      # strain relief over the cable end (overlaps it 4 mm)
    tube(bmX,[e-Z*0.012,e-Z*0.050],0.0095,12,0)                      # moulded body
    tube(bmX,[e-Z*0.030,e-Z*0.038],0.0099,12,1)                      # red 'TERM' band (0.4 mm proud)
    tube(bmX,[e-Z*0.050,e-Z*0.066],0.0090,12,2)                      # steel XLR shell
    nterm+=1
newobj('CCOM newsroom grid DMX terminators (nd)',bmX,[M_TERM,M_RED,M_MET])
print('TERM',nterm)
mt={'osm_id':'(main CCOM)','msu_building':'School of Communication and Media (CCOM)','msu_area':'NJ PBS newsroom studio','msu_layer':'interior_detail','msu_merge_role':'main_owned','msu_target_collection':'MSU_CCOM'}
for o in col.objects:
    for k,v in mt.items(): o[k]=v
sc['nd_note']="nd: collection %s (tape crossings, worn ends, DMX terminators); no swaps/hides"%COLN
print('NEWOBJ',len(col.objects),'TOTAL',len(O))
if MODE=='SAVE': bpy.ops.wm.save_mainfile(); print('SAVED')
else: bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(bpy.data.filepath),'_nd_test.blend'),copy=True); print('TESTSAVED')

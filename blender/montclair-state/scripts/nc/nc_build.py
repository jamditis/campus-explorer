# Session nc (Oct 30 2026 ~5:21 AM ET): NJ PBS studio follow-up (Joe's Oct 29 10:45 PM correction). ALL UNVERIFIED.
# 1) steel safety cables looped round the grid bar on all 18 grid spots (+ ferrule)
# 2) DMX daisy-chain run along each grid bar (opposite side to the nb power tails) with pigtails into each spot + DMX node + feed to ceiling
# 3) gaffer-tape spike marks on the studio floor (camera T-marks per pedestal/tripod, set-edge tape line, desk-front centre mark)
# 4) per-object clearer glass copy on 'CCOM newsroom south glass (mx)' only (softbox backs read grey through it); shared glass untouched
import bpy, bmesh, math, os, json
from mathutils import Vector
MODE=os.environ.get('NC_MODE','TEST'); SES='nc'; COLN='MS_CCOM_newsroom_studio_detail5_20261030nc'
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
Z=Vector((0,0,1))
def P(u,t,z): return d*u+n*(C0+T0+t)+Vector((0,0,z))
def UT(v): return v.dot(d), v.dot(n)-(C0+T0)
O=bpy.data.objects; mats=bpy.data.materials; sc=bpy.context.scene
def mat(name,col,rough=0.6,metal=0.0):
    m=mats.get(name)
    if m: return m
    m=mats.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*col,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    m['msu_tag_session']=SES; m['status']='UNVERIFIED'; return m
M_STEEL=mat('NC_safety_cable_galvanised_steel_UNVERIFIED',(0.85,0.85,0.86),0.25,0.6)
M_DMX=mat('NC_dmx_cable_black_UNVERIFIED',(0.018,0.016,0.02),0.45)
M_NODE=mat('NC_dmx_node_box_black_UNVERIFIED',(0.03,0.03,0.032),0.5,0.4)
TAPE={k:mat('NC_gaffer_tape_%s_UNVERIFIED'%k,c,0.75) for k,c in
      (('red',(0.55,0.03,0.025)),('blue',(0.02,0.10,0.45)),('green',(0.03,0.35,0.06)),('yellow',(0.75,0.55,0.02)),('white',(0.75,0.75,0.72)))}
col=bpy.data.collections.get(COLN)
if col is None:
    col=bpy.data.collections.new(COLN); sc.collection.children.link(col)
col['msu_tag_session']=SES
SRC="Joe correction Oct 29 10:45 PM (studio exists); rigging/tape typical broadcast practice, no photo -> UNVERIFIED"
def newobj(name,bm,mlist,shadow=True):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mlist: me.materials.append(m)
    o=bpy.data.objects.new(name,me); col.objects.link(o)
    o['msu_tag_session']=SES; o['status']='UNVERIFIED'; o['source']=SRC
    if not shadow: o.visible_shadow=False
    return o
def wbox(bm,c,ax,ay,hx,hy,z0,z1,mi=0):
    vs=[bm.verts.new(c+ax*sx*hx+ay*sy*hy+Z*(zz-c.z)) for zz in (z0,z1) for sy in (-1,1) for sx in (-1,1)]
    for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        bm.faces.new([vs[i] for i in f]).material_index=mi
def tube(bm,pts,r,k=6,mi=0,closed=False):
    pts=[Vector(p) for p in pts]; rings=[]; N=len(pts)
    for i,p in enumerate(pts):
        if closed: a=pts[(i+1)%N]-pts[(i-1)%N]
        else: a=pts[min(i+1,N-1)]-pts[max(i-1,0)]
        a.normalize(); ref=Z if abs(a.dot(Z))<0.9 else d
        x=a.cross(ref).normalized(); y=a.cross(x).normalized()
        rings.append([bm.verts.new(p+r*(math.cos(2*math.pi*j/k)*x+math.sin(2*math.pi*j/k)*y)) for j in range(k)])
    pairs=list(zip(rings,rings[1:]))+([(rings[-1],rings[0])] if closed else [])
    for A,B in pairs:
        for j in range(k):
            f=bm.faces.new([A[j],A[(j+1)%k],B[(j+1)%k],B[j]]); f.material_index=mi; f.smooth=True
    if not closed:
        for R in (rings[0],rings[-1][::-1]):
            f=bm.faces.new(R[::-1]); f.material_index=mi
sp=O['CCOM newsroom grid spots (mx, GN instances)']
spots=[UT(sp.matrix_world@v.co) for v in sp.data.vertices]
boxes=[(-14.19,-2.5),(-14.19,-5.0),(-14.19,-7.5),(-6.69,-2.5),(-6.69,-7.5)]
ZC=145.53
# ---------- 1. safety cables ----------
bmS=bmesh.new()
for (us,ts) in spots:
    bx=min([b for b in boxes if abs(b[1]-ts)<0.1], key=lambda b:abs(b[0]-us)); s=1 if bx[0]>us else -1
    uu=us-s*0.18                                                   # beside the can (can half-width ~0.13), opposite the power tail
    ring=[P(uu+0.006*math.sin(2*math.pi*k/16),ts+0.062*math.cos(2*math.pi*k/16),ZC+0.062*math.sin(2*math.pi*k/16)) for k in range(16)]
    tube(bmS,ring,0.003,6,0,closed=True)
    tube(bmS,[P(uu,ts,ZC-0.062),P(uu+s*0.02,ts+0.004,145.44),P(us-s*0.135,ts+0.006,145.405),P(us-s*0.122,ts+0.006,145.40)],0.0026,6,0)  # tail to the yoke lug, end buried in the can side
    c=P(uu,ts,ZC-0.062); tube(bmS,[c-Z*0.016,c+Z*0.004],0.0048,8,0)   # crimped ferrule at the loop bottom
newobj('CCOM newsroom grid spot safety cables (nc)',bmS,[M_STEEL])
# ---------- 2. DMX daisy chain ----------
bmD=bmesh.new(); bmN=bmesh.new()
for tb in sorted({b[1] for b in boxes}):
    on=sorted([s_ for s_ in spots if abs(s_[1]-tb)<0.1])
    if not on: continue
    ub=-14.19; ul=-0.047; zl=145.515
    lo=min(on[0][0],ub)-0.30; hi=max(on[-1][0],ub)+0.30
    tube(bmD,[P(lo,tb+ul,zl-0.02),P(lo+0.05,tb+ul,zl)]+[P(u,tb+ul,zl) for u in [lo+0.15+i*0.25 for i in range(int((hi-lo-0.3)/0.25))]]+[P(hi-0.05,tb+ul,zl),P(hi,tb+ul,zl-0.02)],0.0045,6,0)
    for (us,ts) in on:
        bx=min([b for b in boxes if abs(b[1]-ts)<0.1], key=lambda b:abs(b[0]-us)); s=1 if bx[0]>us else -1
        tube(bmD,[P(us-s*0.22,ts+ul,zl),P(us-s*0.20,ts+ul-0.01,145.47),P(us-s*0.15,ts-0.035,145.40),P(us-s*0.105,ts-0.03,145.38)],0.0035,6,0)
    # DMX node on the -t side of the bar at the u -14.19 hanger, fed from the ceiling
    wbox(bmN,P(ub+0.25,tb-0.095,0),d,n,0.10,0.03,145.44,145.53,0)
    tube(bmD,[P(ub+0.30,tb+ul,zl),P(ub+0.30,tb-0.07,145.50),P(ub+0.30,tb-0.085,145.49)],0.0035,6,0)
    tube(bmD,[P(ub+0.20,tb-0.095,145.52),P(ub+0.20,tb-0.095,146.35),P(ub+0.20,tb-0.095,146.41)],0.007,8,0)
    for zz in (145.70,146.00): wbox(bmN,P(ub+0.20,tb-0.095,0),d,n,0.012,0.012,zz,zz+0.02,1)
newobj('CCOM newsroom grid DMX daisy-chain run + pigtails (nc)',bmD,[M_DMX])
newobj('CCOM newsroom grid DMX nodes + cable clips (nc)',bmN,[M_NODE,M_STEEL])
# ---------- 3. gaffer tape on the floor / set riser (each piece seated by a down-ray onto the floor or riser top) ----------
dg=bpy.context.evaluated_depsgraph_get(); OK={'CCOM newsroom studio floor (raised access, mw)','CCOM newsroom set riser (mw)'}
W=0.024; bmT=bmesh.new(); placed=[0,0]
def seat(c,ax,ay,hx,hy,mi,lift=0.0):
    zs=[]
    for sx,sy in ((0,0),(-1,-1),(1,-1),(1,1),(-1,1)):
        q=c+ax*sx*hx+ay*sy*hy; hit,loc,nor,idx,ob,mtx=sc.ray_cast(dg,Vector((q.x,q.y,137.95)),Vector((0,0,-1)))
        if not hit or ob.name not in OK: placed[1]+=1; print('SKIP',mi,round(c.x,2),round(c.y,2),ob.name if hit else None); return False
        zs.append(loc.z)
    if max(zs)-min(zs)>0.003: placed[1]+=1; print('SKIPZ',mi,round(c.x,2),round(c.y,2),[round(z,3) for z in zs]); return False
    z=max(zs); wbox(bmT,Vector((c.x,c.y,z)),ax,ay,hx,hy,z+0.0012+lift,z+0.0028+lift,mi); placed[0]+=1; return True
desk=Vector((-17.42,-11.52,0))
bases=[((-17.96,-7.33),0),((-16.40,-7.70),1),((-14.85,-8.09),2),((-19.41,-5.90),3)]
for (bx_,by_),ci in bases:
    B=Vector((bx_,by_,0)); dr=(desk-B); dr.z=0; dr.normalize(); pr=Z.cross(dr)
    for off in (0.6,0.75,0.45,0.9):
        c=B+dr*off
        if seat(c,pr,dr,0.13,W,ci): seat(c-dr*(W+0.07),pr,dr,W,0.07,ci); break
    c=B-dr*0.62
    if seat(c,pr,dr,0.08,W,ci): seat(c,pr,dr,W,0.08,ci,0.0002)
# riser-top marks in front of the anchor desk: dashed white edge line 0.35 m out from the desk front + yellow centre cross
dk=O['CCOM newsroom anchor desk (mw)']; me=dk.data; mw=dk.matrix_world
# desk front direction = towards the cameras
cam=Vector((-16.4,-7.7,0)); fwd=cam-desk; fwd.z=0; fwd.normalize(); ax=Z.cross(fwd)
ext=[(mw@v.co-desk).dot(ax) for v in me.vertices]; fr=max((mw@v.co-desk).dot(fwd) for v in me.vertices)
u0,u1=min(ext),max(ext); print('DESK front',round(fr,2),'span',round(u0,2),round(u1,2))
base=desk+fwd*(fr+0.35)
for i in range(int((u1-u0)/0.55)+1):
    c=base+ax*(u0+0.25+i*0.55)
    if (c-base).dot(ax)<u1-0.2: seat(c,ax,fwd,0.20,W,4)
seat(base,ax,fwd,0.06,W,3); seat(base,ax,fwd,W,0.06,3,0.0002)
print('TAPE placed/skipped',placed)
newobj('CCOM newsroom floor gaffer-tape spike marks (nc)',bmT,[TAPE['red'],TAPE['blue'],TAPE['green'],TAPE['yellow'],TAPE['white']],shadow=False)
# ---------- 4. per-object clearer south glass ----------
swaps={}
o=O['CCOM newsroom south glass (mx)']; old='CCOM_atrium_glass_interior'; nm='NC_studio_south_glass_clearer_UNVERIFIED'
m=mats.get(nm)
if m is None:
    m=mats[old].copy(); m.name=nm; m['msu_tag_session']=SES
    b=[x for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED'][0].inputs
    b['Coat Weight'].default_value=0.25; b['Roughness'].default_value=0.05; b['Alpha'].default_value=0.10
for i,s in enumerate(o.material_slots):
    if s.material and s.material.name==old:
        s.link='DATA' if o.data.users==1 else 'OBJECT'; s.material=m; swaps.setdefault(o.name,[]).append((i,old))
sc['nc_swaps']=json.dumps(swaps)
sc['nc_note']="nc: collection %s; material slot swaps in scene['nc_swaps']"%COLN
print('NEWOBJ',len(col.objects),'TOTAL',len(O),'SWAPS',swaps)
if MODE=='SAVE': bpy.ops.wm.save_mainfile(); print('SAVED')
else: bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(bpy.data.filepath),'_nc_test.blend'),copy=True); print('TESTSAVED')

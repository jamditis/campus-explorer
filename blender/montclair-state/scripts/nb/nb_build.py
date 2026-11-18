# Session nb (Oct 30 2026 ~4:20 AM ET): NJ PBS studio follow-up (Joe's Oct 29 10:45 PM correction).
# 1) grid-spot power cables taped along the grid bars to connector strips + vertical cable drops to ceiling junction plates
# 2) lavalier mics (clip + capsule + cable to a belt pack) + IFB earpiece tubes on the 2 anchor placeholders
# 3) S eave-return barrel-tile stub (2 cut-end islands of the main course) clipped back to the return line (orig coords kept)
# 4) per-object material copies: clearer back-office glass fronts; black softbox shells/stands. All UNVERIFIED.
import bpy, bmesh, math, os, json
from mathutils import Vector, Matrix
MODE=os.environ.get('NB_MODE','TEST'); SES='nb'; COLN='MS_CCOM_newsroom_studio_detail4_20261030nb'
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
M_CAB=mats['MY_camera_cable_black_UNVERIFIED']
M_BOX=mat('NB_grid_connector_strip_black_UNVERIFIED',(0.025,0.025,0.027),0.5,0.5)
M_PLT=mat('NB_ceiling_junction_plate_grey_UNVERIFIED',(0.10,0.10,0.105),0.5,0.6)
M_LAV=mat('NB_lav_mic_clip_black_UNVERIFIED',(0.01,0.01,0.01),0.4,0.2)
M_PACK=mat('NB_lav_beltpack_grey_UNVERIFIED',(0.05,0.05,0.055),0.45,0.4)
M_IFB=mat('NB_ifb_earpiece_tube_clear_beige_UNVERIFIED',(0.55,0.48,0.40),0.25)
col=bpy.data.collections.get(COLN)
if col is None:
    col=bpy.data.collections.new(COLN); sc.collection.children.link(col)
col['msu_tag_session']=SES
SRC="Joe correction Oct 29 10:45 PM (studio exists); cable/mic kit typical broadcast practice, no photo -> UNVERIFIED"
def newobj(name,bm,mlist):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mlist: me.materials.append(m)
    o=bpy.data.objects.new(name,me); col.objects.link(o)
    o['msu_tag_session']=SES; o['status']='UNVERIFIED'; o['source']=SRC; return o
def wbox(bm,c,ax,ay,hx,hy,z0,z1,mi=0):
    vs=[bm.verts.new(c+ax*sx*hx+ay*sy*hy+Z*(zz-c.z)) for zz in (z0,z1) for sy in (-1,1) for sx in (-1,1)]
    for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        bm.faces.new([vs[i] for i in f]).material_index=mi
def tube(bm,pts,r,k=6,mi=0,smooth=True):
    pts=[Vector(p) for p in pts]; rings=[]
    for i,p in enumerate(pts):
        a=pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]; a.normalize()
        ref=Z if abs(a.dot(Z))<0.9 else d
        x=a.cross(ref).normalized(); y=a.cross(x).normalized()
        rings.append([bm.verts.new(p+r*(math.cos(2*math.pi*j/k)*x+math.sin(2*math.pi*j/k)*y)) for j in range(k)])
    for A,B in zip(rings,rings[1:]):
        for j in range(k):
            f=bm.faces.new([A[j],A[(j+1)%k],B[(j+1)%k],B[j]]); f.material_index=mi; f.smooth=smooth
    for R in (rings[0],rings[-1][::-1]):
        f=bm.faces.new(R[::-1]); f.material_index=mi
def sag(a,b,dz,k=6):
    a,b=Vector(a),Vector(b); return [a.lerp(b,i/k)-Z*dz*math.sin(math.pi*i/k) for i in range(k+1)]
# ---------- 1. spot cables + connector strips + ceiling drops ----------
sp=O['CCOM newsroom grid spots (mx, GN instances)']
spots=[UT(sp.matrix_world@v.co) for v in sp.data.vertices]
ZB0,ZB1=145.50,145.56; TS=0.047   # grid bar z range; cable centre offset from bar centreline (bar half-width 0.04)
boxes=[(-14.19,-2.5),(-14.19,-5.0),(-14.19,-7.5),(-6.69,-2.5),(-6.69,-7.5)]   # beside grid hangers (mw)
HB=0.30
bmC=bmesh.new(); bmB=bmesh.new()
lane={}
for (us,ts) in sorted(spots):
    bx=min([b for b in boxes if abs(b[1]-ts)<0.1], key=lambda b:abs(b[0]-us))
    s=1 if bx[0]>us else -1; key=(bx,s); j=lane.get(key,0); lane[key]=j+1
    zj=145.513+0.012*(j%4); tj=ts+TS+0.0
    a=P(us+s*0.112,ts+0.03,145.36)                  # out of the can's box-side face (can x +-0.11, z 145.18-145.50)
    m1=P(us+s*0.22,ts+0.05,145.30)
    m2=P(us+s*0.34,tj,zj)
    end=P(bx[0]-s*(HB-0.02),tj,zj)                    # ends 2 cm inside the strip end face
    tube(bmC,[a,m1,P(us+s*0.29,tj,145.40),m2,end],0.0055,6)
for (ub,tb) in boxes:
    wbox(bmB,P(ub,tb+0.075,0),d,n,HB,0.035,145.47,145.57,0)            # connector strip beside the bar (clear of the hanger)
    for k in range(6): wbox(bmB,P(ub-0.25+k*0.1,tb+0.111,0),d,n,0.02,0.002,145.50,145.54,1)  # outlet faces
    tube(bmC,[P(ub+0.03,tb+0.075,145.56),P(ub+0.03,tb+0.075,146.35),P(ub+0.03,tb+0.075,146.41)],0.011,8)   # cable drop (into ceiling)
    tube(bmC,[P(ub-0.03,tb+0.075,145.56),P(ub-0.03,tb+0.075,146.41)],0.008,6)
    wbox(bmB,P(ub,tb+0.075,0),d,n,0.10,0.07,146.36,146.40,2)          # ceiling junction plate
    for zz in (145.80,146.05,146.28):                                    # velcro ties to the hanger
        wbox(bmB,P(ub,tb+0.045,0),d,n,0.045,0.05,zz,zz+0.018,0)
newobj('CCOM newsroom grid spot power cables + ceiling drops (nb)',bmC,[M_CAB])
newobj('CCOM newsroom grid connector strips + ceiling plates + ties (nb)',bmB,[M_BOX,M_PLT,M_PLT])
# ---------- 2. lavalier mics + IFB on the 2 anchor placeholders ----------
pp=O['CCOM newsroom seated people placeholders (my, GN instances)']
bmL=bmesh.new()
def torso_pt(z,ang,off=0.012):
    f=(z-0.53)/(1.05-0.53); ax=-0.06+(-0.03)*f; r=0.17+0.02*f+off
    return Vector((ax+r*math.cos(ang),r*math.sin(ang),z))
for i in (5,6):
    v=pp.data.vertices[i].co; rz=pp.data.attributes['rot'].data[i].vector[2]
    M=Matrix.Translation(pp.matrix_world@v)@Matrix.Rotation(rz,4,'Z')
    W=lambda p: M@Vector(p)
    c=torso_pt(0.97,0.30,0.022)                           # lapel clip, wearer's left
    ax=W(c)-W(c-Vector((1,0,0))); ax.z=0; ax.normalize(); ay=Z.cross(ax)
    wbox(bmL,W(c),ax,ay,0.006,0.010,W(c).z-0.014,W(c).z+0.012,0)
    tube(bmL,[W(c+Vector((0.004,0,0.012))),W(c+Vector((0.004,0,0.030)))],0.0045,8,0)   # capsule
    path=[c+Vector((-0.004,0,-0.014))]+[torso_pt(z,a,0.008) for z,a in ((0.90,0.32),(0.80,0.45),(0.70,1.0),(0.64,1.7),(0.60,2.4),(0.58,2.85))]
    tube(bmL,[W(p) for p in path],0.0018,5,0)
    bp=torso_pt(0.60,math.pi,0.018)                      # belt pack at the back waist
    wbox(bmL,W(bp),ax,ay,0.016,0.035,W(bp).z-0.05,W(bp).z+0.05,1)
    tube(bmL,[W(bp+Vector((0,0,0.05))),W(bp+Vector((0,0,0.075)))],0.002,5,1)   # pack antenna
    # IFB earpiece: coiled tube from wearer's right ear down behind the collar into the back
    hc=Vector((-0.07,0,1.24)); e=hc+Vector((0.0,-0.108,-0.01))
    ifb=[e,hc+Vector((-0.04,-0.10,-0.08)),Vector((-0.17,-0.08,1.09)),torso_pt(1.0,math.pi*0.85,0.006),torso_pt(0.82,math.pi*0.95,0.006),torso_pt(0.62,math.pi*0.98,0.02)]
    tube(bmL,[W(p) for p in ifb],0.0022,5,2)
    tube(bmL,[W(e+Vector((0.012,0.0,0.0))),W(e+Vector((-0.012,-0.008,0)))],0.006,6,2)  # ear bud
newobj('CCOM newsroom anchor lav mics + IFB earpieces (nb)',bmL,[M_LAV,M_PACK,M_IFB])
# ---------- 3. S eave-return clean-up: (a) the 8 cut-end barrel-tile islands of the main eave course sitting on top of the
# S return (mv dry-run list) and (b) the 1.1 m light coping-strip piece lying along the S return front are split into
# their own objects and HIDDEN (not deleted); REVERT joins them back.
nn=Vector((-0.972,0.232,0)).normalized(); tt=Vector((0.232,0.972,0)).normalized()
hidden=[]
def split_hide(src,newname,u0,u1,w0,w1,z0,z1,note):
    to=O[src]; mw=to.matrix_world
    bm=bmesh.new(); bm.from_mesh(to.data); seen=set(); kill=[]
    for f in bm.faces:
        if f.index in seen: continue
        isl=[]; st=[f]; seen.add(f.index)
        while st:
            g=st.pop(); isl.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen: seen.add(h.index); st.append(h)
        vs={v for g in isl for v in g.verts}; c=sum((mw@v.co for v in vs),Vector())/len(vs)
        if u0<c.dot(tt)<u1 and w0<c.dot(nn)<w1 and z0<c.z<z1: kill.extend(isl)
    ki={g.index for g in kill}
    bm2=bm.copy(); bmesh.ops.delete(bm2,geom=[f for f in bm2.faces if f.index not in ki],context='FACES')
    bmesh.ops.delete(bm2,geom=[v for v in bm2.verts if not v.link_faces],context='VERTS')
    bmesh.ops.delete(bm,geom=list(kill),context='FACES')
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
    bm.to_mesh(to.data); bm.free(); to.data.update()
    me2=bpy.data.meshes.new(newname); bm2.to_mesh(me2); bm2.free()
    for m in to.data.materials: me2.materials.append(m)
    so=bpy.data.objects.new(newname,me2); so.matrix_world=mw.copy(); col.objects.link(so)
    so.hide_render=True; so.hide_viewport=True; so['msu_tag_session']=SES; so['note']=note+'; hidden not deleted'; so['nb_split_from']=src
    to['nb_note']='nb: %d faces split to the hidden object %s'%(len(ki),newname); hidden.append(so.name)
    print('SPLIT',src[:40],len(ki))
split_hide('School of Communication and Media barrel tile eave course','CCOM S eave-return tile stub (nb, HIDDEN, split from the eave course)',
           1.9,3.4,20.5,23.4,146.6,147.6,'8 barrel-tile islands of the main eave course sitting on the S eave return (mu/mv stub)')
cop=[o.name for o in O if o.name.startswith('el coping strips School of Communication and Media')][0]
split_hide(cop,'CCOM S eave-return coping strip end (nb, HIDDEN, split from the el coping strips)',
           1.9,2.6,21.0,23.0,146.6,147.2,'1.1 m light coping-strip piece lying along the S eave return front')
sc['nb_hidden']=hidden
# ---------- 4. per-object material copies ----------
swaps={}
def swap(objname,oldname,newname,fn):
    o=O[objname]; m=mats.get(newname)
    if m is None:
        m=mats[oldname].copy(); m.name=newname; m['msu_tag_session']=SES; fn(m)
    for i,s in enumerate(o.material_slots):
        if s.material and s.material.name==oldname:
            s.link='DATA' if o.data.users==1 else 'OBJECT'; s.material=m; swaps.setdefault(objname,[]).append((i,oldname))
def clearer(m):
    for nd in m.node_tree.nodes:
        if nd.type=='BSDF_PRINCIPLED':
            b=nd.inputs; print('GLASS before',[(k,b[k].default_value if not hasattr(b[k].default_value,'__len__') else tuple(b[k].default_value)) for k in ('Base Color','Roughness','Alpha','Transmission Weight','IOR')])
            b['Roughness'].default_value=min(b['Roughness'].default_value,0.02)
            c=b['Base Color'].default_value; b['Base Color'].default_value=(c[0]*0.55,c[1]*0.55,c[2]*0.55,1)
            if b['Alpha'].default_value<1: b['Alpha'].default_value=max(0.12,b['Alpha'].default_value*0.6)
def blacken(m):
    for nd in m.node_tree.nodes:
        if nd.type=='BSDF_PRINCIPLED':
            print('SHELL before',tuple(nd.inputs['Base Color'].default_value)); nd.inputs['Base Color'].default_value=(0.012,0.012,0.013,1); nd.inputs['Roughness'].default_value=0.7
swap('CCOM newsroom back offices glass fronts (mw)','CCOM_atrium_glass_interior','NB_back_office_glass_fronts_clearer_UNVERIFIED',clearer)
# (softbox shells already near-black 0.008 -> no swap; grey backs = see review)
sc['nb_swaps']=json.dumps(swaps)
sc['nb_note']="nb: collection %s; tile stub clipped (nb_clip_orig on the tile object); material slot swaps in scene['nb_swaps']"%COLN
print('NEWOBJ',len(col.objects),'TOTAL',len(O),'SWAPS',swaps)
if MODE=='SAVE': bpy.ops.wm.save_mainfile(); print('SAVED')
else: bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(bpy.data.filepath),'data/nb/test.blend'),copy=True); print('TESTSAVED')

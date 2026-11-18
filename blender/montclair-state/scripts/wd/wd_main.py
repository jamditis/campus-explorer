# wd: Bohn approach walks from OSM: footway 1132693523 -> W door landing; footway 600258640 + steps 313029912
# -> N door landing as a real stair down a cut (TK N landing was half-buried in the 3DEP slope).
import bpy, bmesh, json, os, math
from mathutils import Vector
SAVE=os.environ.get('SAVE')=='1'
sc=bpy.context.scene
# clean previous wd
for o in [o for o in bpy.data.objects if 'wd_obj' in o]:
    me=o.data; bpy.data.objects.remove(o)
    if me and getattr(me,'users',1)==0 and hasattr(me,'vertices'): bpy.data.meshes.remove(me)
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
for m in [m for m in sk.modifiers if m.name.startswith('WD_')]: sk.modifiers.remove(m)
dg=bpy.context.evaluated_depsgraph_get()
ske=sk.evaluated_get(dg)
TER=[bpy.data.objects[n] for n in ['Terrain_LiDAR_DTM_1m'] if n in bpy.data.objects]
def hit(x,y):
    best=None
    dgl=bpy.context.evaluated_depsgraph_get()
    for o in [sk]+TER:
        e=o.evaluated_get(dgl); mw=o.matrix_world; iw=mw.inverted()
        r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    return best
col=bpy.data.collections.get('WD_Bohn_approach_walks_steps_UNVERIFIED') or bpy.data.collections.new('WD_Bohn_approach_walks_steps_UNVERIFIED')
if col.name not in sc.collection.children: sc.collection.children.link(col)
walkmat=bpy.data.materials['QT_walk_concrete_joints_UNVERIFIED']
L=bpy.data.objects['TK_Bohn_landing_N_steps_UNVERIFIED']
landmat=L.data.materials[0] if L.data.materials else walkmat
wallmat=bpy.data.materials.get('WD_retaining_wall_concrete_UNVERIFIED')
if wallmat is None:
    wallmat=walkmat.copy(); wallmat.name='WD_retaining_wall_concrete_UNVERIFIED'
railmat=bpy.data.materials.get('WD_rail_steel_dark_UNVERIFIED')
if railmat is None:
    railmat=bpy.data.materials.new('WD_rail_steel_dark_UNVERIFIED'); railmat.use_nodes=True
    b=railmat.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.05,0.055,0.06,1)
    b.inputs['Metallic'].default_value=0.85; b.inputs['Roughness'].default_value=0.45
def mkobj(name,bm,mat):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o=bpy.data.objects.new(name,me); col.objects.link(o); o['wd_obj']=1; o['UNVERIFIED']='wd: OSM-sourced line; dims/design invented'; return o
log={}
# ---------- draped walk helper ----------
def walk(name,pts,hw=0.9,end_lift=None):
    P=[Vector((p[0],p[1],0)) for p in pts]
    S=[]
    for i in range(len(P)-1):
        a,b=P[i],P[i+1]; n=max(1,int((b-a).length/0.4))
        for j in range(n): S.append((a+(b-a)*(j/n), (b-a).normalized()))
    S.append((P[-1],(P[-1]-P[-2]).normalized()))
    bm=bmesh.new(); rows=[]
    for k,(c,d) in enumerate(S):
        if 0<k<len(S)-1: d=(S[k+1][0]-S[k-1][0]).normalized()
        side=Vector((-d.y,d.x,0)); tops=[]
        for s in (-hw,hw):
            q=c+side*s; z=(hit(q.x,q.y) or 134)+0.05
            if end_lift and k>=len(S)-3: z=max(z,end_lift)
            tops.append(bm.verts.new((q.x,q.y,z)))
        rows.append([bm.verts.new((tops[0].co.x,tops[0].co.y,tops[0].co.z-0.25))]+tops+[bm.verts.new((tops[1].co.x,tops[1].co.y,tops[1].co.z-0.25))])
    for a,b in zip(rows,rows[1:]):
        for j in range(3): bm.faces.new((a[j],a[j+1],b[j+1],b[j]))
    bm.faces.new(rows[0]); bm.faces.new(list(reversed(rows[-1])))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    return mkobj(name,bm,walkmat)
# ---------- N stair frame ----------
c=[L.matrix_world@v.co for v in L.data.vertices]; top=[p for p in c if p.z>max(q.z for q in c)-0.05]
zL=max(p.z for p in top)
e=Vector((0.9444,-0.3291,0)).normalized(); nrm=Vector((-e.y,e.x,0))   # nrm ~ +y outward
M=Vector((226.825,413.425,0)); SL=4.20
def W(s,l,z=0): return Vector((M.x+e.x*s+nrm.x*l, M.y+e.y*s+nrm.y*l, z))
T=0.32; best=None
for n in range(8,18):
    s0=-(n-1)*T; g=hit(*W(s0-0.15,0).xy)
    rise=(g+0.03-zL)/n
    if 0.14<=rise<=0.18:
        sc_=abs(rise-0.16)
        if best is None or sc_<best[0]: best=(sc_,n,s0,rise,g)
_,n,s0,rise,g0=best
print('STAIR n',n,'s0',round(s0,2),'rise',round(rise,3),'g0',round(g0,2),'zL',zL)
log['stair']=dict(n=n,s0=s0,rise=rise,tread=T,zL=zL,width=1.75)
LAT=(-0.80,0.95); ZB=130.6
def surf(s):
    if s>=0: return zL
    if s<s0: return zL+n*rise
    k=int((s-s0)//T); return zL+(n-1-k)*rise
# stair solid: profile in (s,z) extruded across LAT (+0.03 into walls)
prof=[(s0-0.30,ZB),(s0-0.30,zL+n*rise)]
for k in range(n):
    sk_=s0+k*T; prof.append((sk_,zL+(n-k)*rise)); prof.append((sk_,zL+(n-1-k)*rise-(0.01 if k==n-1 else 0)))
prof.append((0.02,zL-0.01)); prof.append((0.02,ZB))
bm=bmesh.new()
A=[bm.verts.new(W(s,LAT[0]-0.03,z)) for s,z in prof]; B=[bm.verts.new(W(s,LAT[1]+0.03,z)) for s,z in prof]
bm.faces.new(A); bm.faces.new(list(reversed(B)))
for i in range(len(prof)):
    j=(i+1)%len(prof); bm.faces.new((A[i],A[j],B[j],B[i]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
stair=mkobj('WD_Bohn_N_steps_313029912_UNVERIFIED',bm,walkmat)
# ground samples (before cut) along wall lines
def gline(seg,lat_out):
    pass
# walls: list of (s_a,s_b,lat_in,lat_out) along s, and (s,lat_a,lat_b) across
walls=[]
def wall_along(name,sa,sb,li,lo):
    bm=bmesh.new(); rows=[]; N=max(2,int(abs(sb-sa)/0.25))
    sgn=1 if lo>li else -1
    for i in range(N+1):
        s=sa+(sb-sa)*i/N
        go=hit(*W(s,lo+sgn*0.15).xy) or zL
        sf=surf(s)
        zt=max(go,sf)+0.12; zb=min(go,sf)-0.45
        rows.append([bm.verts.new(W(s,li,zb)),bm.verts.new(W(s,li,zt)),bm.verts.new(W(s,lo,zt)),bm.verts.new(W(s,lo,zb))])
    for a,b in zip(rows,rows[1:]):
        for j in range(4): bm.faces.new((a[j],a[(j+1)%4],b[(j+1)%4],b[j]))
    bm.faces.new(rows[0]); bm.faces.new(list(reversed(rows[-1])))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    o=mkobj(name,bm,wallmat); walls.append(o); return o
def wall_across(name,s_in,s_out,la,lb):
    bm=bmesh.new(); rows=[]; N=max(2,int(abs(lb-la)/0.25))
    for i in range(N+1):
        l=la+(lb-la)*i/N
        go=hit(*W(s_out+0.15,l).xy) or zL; sf=zL
        zt=max(go,sf)+0.12; zb=min(go,sf)-0.45
        rows.append([bm.verts.new(W(s_in,l,zb)),bm.verts.new(W(s_in,l,zt)),bm.verts.new(W(s_out,l,zt)),bm.verts.new(W(s_out,l,zb))])
    for a,b in zip(rows,rows[1:]):
        for j in range(4): bm.faces.new((a[j],a[(j+1)%4],b[(j+1)%4],b[j]))
    bm.faces.new(rows[0]); bm.faces.new(list(reversed(rows[-1])))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    o=mkobj(name,bm,wallmat); walls.append(o); return o
wall_along('WD_Bohn_N_steps_wall_outer_UNVERIFIED',s0-0.30,SL+0.20,LAT[1],LAT[1]+0.20)
wall_along('WD_Bohn_N_steps_wall_inner_UNVERIFIED',s0-0.30,0.0,LAT[0],LAT[0]-0.20)
wall_across('WD_Bohn_N_landing_wall_east_UNVERIFIED',SL,SL+0.20,-0.95,LAT[1]+0.20)
# landing plinth face: extend existing landing slab visually by a skirt under its outer/east edges handled by walls.
# ---------- cutter (boolean on skirt) ----------
poly=[(s0-0.30,LAT[0]-0.20),(0.0,LAT[0]-0.20),(0.0,-0.95),(SL+0.20,-0.95),(SL+0.20,LAT[1]+0.20),(s0-0.30,LAT[1]+0.20)]
bm=bmesh.new()
lo_=[bm.verts.new(W(s,l,120)) for s,l in poly]; hi_=[bm.verts.new(W(s,l,150)) for s,l in poly]
bm.faces.new(list(reversed(lo_))); bm.faces.new(hi_)
for i in range(len(poly)):
    j=(i+1)%len(poly); bm.faces.new((lo_[i],lo_[j],hi_[j],hi_[i]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
cut=mkobj('WD_skirt_cutter_Bohn_N_steps',bm,wallmat)
cut.hide_render=True; cut.hide_viewport=True; cut.display_type='WIRE'
# ---------- rails ----------
def tube(bm,a,b,r=0.022,seg=8):
    d=(b-a); L_=d.length
    if L_<1e-4: return
    q=d.to_track_quat('Z','Y')
    res=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=L_)
    for v in res['verts']: v.co=q@v.co+(a+b)/2
bm=bmesh.new()
for lat in (LAT[0]+0.07,LAT[1]-0.07):
    pts=[W(s,lat,surf(s+0.001)+0.90) for s in [s0-0.15+k*T for k in range(n)]]+[W(0.35,lat,zL+0.90)]
    for a,b in zip(pts,pts[1:]): tube(bm,a,b)
    for p in pts[::3]+[pts[-1]]:
        side=(-0.07 if lat<0 else 0.07); tube(bm,p,Vector((p.x+nrm.x*side,p.y+nrm.y*side,p.z)),0.012)
# guard rail on outer wall top + landing east wall top where drop > 0.6
for s_a,s_b,fn in [(s0-0.3,SL+0.2,lambda s:W(s,LAT[1]+0.10)),]:
    N=int((s_b-s_a)/1.4)+1; posts=[]
    for i in range(N+1):
        s=s_a+(s_b-s_a)*i/N; p=fn(s); go=hit(*W(s,LAT[1]+0.35).xy) or zL; zt=max(go,surf(s))+0.12
        posts.append((s,Vector((p.x,p.y,zt)),abs(go-surf(s))))
    for (s1,p1,d1),(s2,p2,d2) in zip(posts,posts[1:]):
        if max(d1,d2)<0.6: continue
        tube(bm,p1+Vector((0,0,1.0)),p2+Vector((0,0,1.0)),0.024); tube(bm,p1+Vector((0,0,0.5)),p2+Vector((0,0,0.5)),0.014)
    for s,p,d in posts:
        if d>=0.6: tube(bm,p,p+Vector((0,0,1.0)),0.022)
rail=mkobj('WD_Bohn_N_steps_rails_UNVERIFIED',bm,railmat)
# ---------- walks ----------
P0=W(s0-0.30,(LAT[0]+LAT[1])/2)
w1=walk('WD_walk_600258640_UNVERIFIED',[(201.03,423.73),(203.56,422.84),(222.41,416.16),(P0.x-e.x*0.1,P0.y-e.y*0.1)],hw=0.9)
LW=bpy.data.objects['TK_Bohn_landing_W_walk_UNVERIFIED']
lw=[LW.matrix_world@v.co for v in LW.data.vertices]
# outer edge = two top verts with smallest x (away from building)
lwt=sorted([p for p in lw if p.z>max(q.z for q in lw)-0.05],key=lambda p:p.x)[:2]
om=(lwt[0]+lwt[1])/2
w2=walk('WD_walk_1132693523_UNVERIFIED',[(208.92,405.95),(om.x+0.15,om.y)],hw=0.9,end_lift=max(q.z for q in lw)-0.005)
log['walks']=dict(w600258640=[201.03,423.73,'->',round(P0.x,2),round(P0.y,2)],w1132693523=[208.92,405.95,'->',round(om.x,2),round(om.y,2)])
# ---------- bury grass points inside footprints ----------
def inside(x,y,polyxy):
    c=False; j=len(polyxy)-1
    for i in range(len(polyxy)):
        xi,yi=polyxy[i]; xj,yj=polyxy[j]
        if ((yi>y)!=(yj>y)) and (x<(xj-xi)*(y-yi)/(yj-yi+1e-12)+xi): c=not c
        j=i
    return c
fps=[[tuple(W(s,l).xy) for s,l in poly]]
for o in (w1,w2):
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    x0=min(v.x for v in vs);x1=max(v.x for v in vs);y0=min(v.y for v in vs);y1=max(v.y for v in vs)
fps_walk=[w1,w2]
from mathutils.bvhtree import BVHTree
bv=[]
for o in fps_walk:
    bmw=bmesh.new(); bmw.from_mesh(o.data); bmw.transform(o.matrix_world); bv.append(BVHTree.FromBMesh(bmw)); bmw.free()
hidden={}
for gname in ['TP_Bohn_surround_grass_points_UNVERIFIED','TJ_Webster_lawn_grass_points_UNVERIFIED']:
    g=bpy.data.objects.get(gname)
    if not g: continue
    mw=g.matrix_world; hl=[]
    for i,v in enumerate(g.data.vertices):
        p=mw@v.co
        if p.z<-100: continue
        hid=inside(p.x,p.y,fps[0])
        if not hid:
            for t in bv:
                r=t.ray_cast(Vector((p.x,p.y,p.z+3)),Vector((0,0,-1)),6)
                if r[0] is not None: hid=True;break
        if hid: hl.append((i,v.co.z)); v.co.z=-500.0
    g.data.update(); hidden[gname]=hl
json.dump({k:[{'i':i,'z':z} for i,z in v] for k,v in hidden.items()},open('data/wd/grass_hidden.json','w'))
log['grass_hidden']={k:len(v) for k,v in hidden.items()}
# ---------- cameras ----------
def cam(name,loc,tgt,lens):
    cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=30000; cd.clip_start=0.1
    o=bpy.data.objects.new(name,cd); col.objects.link(o); o['wd_obj']=1
    o.location=loc; o.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); return o
mid=W(s0/2,0.0,surf(s0/2))
cl=W(s0-2.5,2.8); cl.z=(hit(cl.x,cl.y) or 135)+1.65
cam('WD_CAM_closeup_Bohn_N_steps',cl,W(0.8,0,zL+0.6),28)
ey=W(-9,7.5); ey.z=(hit(ey.x,ey.y) or 135)+1.7
cam('WD_CAM_eye_Bohn_N_door_approach_from_NW',ey,W(0.5,0,zL+1.5),32)
ew=Vector((203.5,404.5,0)); ew.z=(hit(ew.x,ew.y) or 135)+1.7
cam('WD_CAM_eye_Bohn_W_door_walk',ew,Vector((215.0,405.4,(hit(215,405.4) or 134)+1.2)),35)
bpy.context.view_layer.update()
md=sk.modifiers.new('WD_cut_Bohn_N_steps','BOOLEAN'); md.operation='DIFFERENCE'; md.object=cut; md.solver='EXACT'
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
# verify cut
ver=[]
for s,l in [(s0/2,0),(-0.5,0.5),(1.5,0),(3.5,0.5)]:
    p=W(s,l); r=sk.evaluated_get(dg).ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)))
    ver.append((s,l,round(r[1].z,2) if r[0] else None, round(surf(s),2)))
log['verify_skirt_after_cut']=ver; print('VERIFY',ver)
r=sk.evaluated_get(dg).ray_cast(Vector((240,420,400)),Vector((0,0,-1))); print('skirt_far_ok',r[0])
log['objs']=len(bpy.data.objects); print('LOG',json.dumps(log)[:1500])
json.dump(log,open('data/wd/apply.json','w'),indent=1)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

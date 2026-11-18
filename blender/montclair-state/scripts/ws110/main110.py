# ws110: College Ave S end -> Normal Ave (road layer + ground seat), layered build
import bpy, bmesh, numpy as np, json, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state/'
D=np.load(R+'prep/ws79_normal_ave_dtm/normal_ave_dtm_1m.npz'); DT=D['dtm']; DX0=float(D['x0']); DY0=float(D['y0'])
def dtm(x,y):
    fx=x-DX0; fy=y-DY0; j=int(np.floor(fx)); i=int(np.floor(fy))
    if not (0<=i<DT.shape[0]-1 and 0<=j<DT.shape[1]-1): return None
    a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
# --- inventory of what's in the gap
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if min(ys)<-246 and max(ys)>-310 and min(xs)<-180 and max(xs)>-300 and (max(xs)-min(xs))<400:
        print('INV110',o.name,round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),'hide',o.hide_render,[m.type for m in o.modifiers])
for n in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km'):
    o=bpy.data.objects[n]; print('MOD110',n,[(m.type,m.name) for m in o.modifiers],len(o.data.vertices))
# --- WS102 end row
cw=next(o for o in bpy.data.objects if o.name.startswith('WS102_CollegeAve_S_carriageway'))
A=np.array([-244.8,-239.3]);B=np.array([-256.1,-271.6]);d=(B-A)/np.linalg.norm(B-A);n=np.array([d[1],-d[0]])
co=np.array([cw.matrix_world@v.co for v in cw.data.vertices]); s=(co[:,0]-A[0])*d[0]+(co[:,1]-A[1])*d[1]
smax=s.max(); er=co[(s>smax-0.05)]; zt=er[:,2].max(); er=er[er[:,2]>zt-0.1]
o_=(er[:,0]-A[0])*n[0]+(er[:,1]-A[1])*n[1]; order=np.argsort(o_); er=er[order]; o_=o_[order]
print('E110 end s %.2f z %.3f cols %d offs %s'%(smax,zt,len(er),np.round(o_,2).tolist()))
C0=A+d*smax  # start centre
z0=float(np.median(er[:,2]))
# --- Normal ribbon parse
OBJ=R+'prep/ws84_normal_ave_ribbon_11m/normal_ave_carriageway_curbs_W11p3_ortho2020_UNVERIFIED.obj'
V=[];G=[];cur=None
for ln in open(OBJ):
    p=ln.split()
    if not p: continue
    if p[0]=='v': V.append(tuple(map(float,p[1:4])))
    elif p[0]=='o': cur=[p[1],[]]; G.append(cur)
    elif p[0]=='f': cur[1].append([int(q.split('/')[0])-1 for q in p[1:]])
V=np.array(V)
# N edge polyline near the junction: L verts (even of strip) of 583841725_L and 583841727_L carriageway
edge=[]
for nm,fs in G:
    if nm in ('NA84_carriageway_583841725_L','NA84_carriageway_583841727_L'):
        for f in fs: edge+= [V[f[0]],V[f[1]]]
edge=np.unique(np.round(np.array(edge),4),axis=0); edge=edge[np.argsort(edge[:,0])]
# keep only true L verts: those north of centreline -> farthest from profile; L verts have even index in pairs (L,C); pick by y above local line
P81=json.load(open(R+'prep/ws81_normal_ave_profile/normal_ave_centerline_profile.json'))
cl=np.concatenate([np.array(w['profile']) for w in P81 if w['osm_way'] in (583841725,583841727,'583841725','583841727')])
def cdist(p): return np.min(np.hypot(cl[:,0]-p[0],cl[:,1]-p[1]))
edge=np.array([e for e in edge if cdist(e)>4.0 and e[1]>np.interp(e[0],cl[np.argsort(cl[:,0])][:,0],cl[np.argsort(cl[:,0])][:,1])])
edge=edge[(edge[:,0]>-290)&(edge[:,0]<-210)]; edge=edge[np.argsort(edge[:,0])]
print('E110 Nedge pts',len(edge),np.round(edge[[0,-1]],2).tolist())
def hit(p0):  # march along d from p0 until crossing edge polyline (y of edge at x)
    for t in np.arange(0,60,0.02):
        q=p0+d*t; ye=np.interp(q[0],edge[:,0],edge[:,1])
        if q[1]<=ye: return t, float(np.interp(q[0],edge[:,0],edge[:,2]))
    return None,None
Tc,_=hit(C0); print('E110 Tc %.2f'%Tc)
Rf=6.0
def flare(u): u=min(max(u,0),Rf); return Rf-np.sqrt(max(Rf*Rf-(Rf-u)**2,0))
W0,E0=o_.max(),o_.min()
ks=np.linspace(0,1,int(np.ceil(Tc/0.5))+1)
bm=bmesh.new(); grid=[]; rows=[]
for k in ks:
    uc=(1-k)*Tc; f=flare(uc); w=W0+f; e=E0-f
    offs=list(e+(o_-E0)/(W0-E0)*(w-e))
    r=[];rp=[]
    for o in offs:
        p0=C0+n*o; T,ze=hit(p0); q=p0+d*(T*k)
        zd=dtm(*q); zd=(zd if zd is not None else z0)+0.04
        a=min(T*k/3.0,1); a=a*a*(3-2*a); z=z0*(1-a)+zd*a
        b=min(T*(1-k)/3.0,1); b=b*b*(3-2*b); z=(ze+0.0)*(1-b)+z*b
        r.append(bm.verts.new((q[0],q[1],z))); rp.append((q[0],q[1],z))
    grid.append(r); rows.append(rp)
for i in range(len(grid)-1):
    for j in range(len(grid[i])-1): bm.faces.new((grid[i][j],grid[i][j+1],grid[i+1][j+1],grid[i+1][j]))
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS110_CollegeAve_S_end_to_NormalAve'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['WS27_CollegeAve_asphalt_2020ortho'])
ob=bpy.data.objects.new('WS110_CollegeAve_S_end_to_NormalAve_flare6m_ortho2020_DTM2023_UNVERIF',me)
coll=bpy.data.collections.new('WS110_CollegeAve_S_end_NormalAve_road_layer'); bpy.context.scene.collection.children.link(coll); coll.objects.link(ob)
# curbs along both College edges (0.15 w, 0.15 reveal) -- straight runs + 6 m arcs
cm=bpy.data.materials['WS27_curb_concrete_UNVERIFIED']
for side,j in (('W',-1),('E',0)):
    bm=bmesh.new(); prev=None
    for i,rp in enumerate(rows):
        p=np.array(rp[j][:2]); z=rp[j][2]
        # outward normal = perpendicular of the edge tangent
        a=np.array(rows[max(i-1,0)][j][:2]); b=np.array(rows[min(i+1,len(rows)-1)][j][:2]); t=(b-a)/np.linalg.norm(b-a); nn=np.array([-t[1],t[0]])
        if np.dot(nn, p-(C0+d*np.dot(p-C0,d)))<0: nn=-nn
        q=p+nn*0.15
        ring=[bm.verts.new((p[0],p[1],z-0.12)),bm.verts.new((p[0],p[1],z+0.15)),bm.verts.new((q[0],q[1],z+0.15)),bm.verts.new((q[0],q[1],z-0.25))]
        if prev:
            for k in range(3): bm.faces.new((prev[k],prev[k+1],ring[k+1],ring[k]))
        prev=ring
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    m2=bpy.data.meshes.new('WS110_curb_'+side); bm.to_mesh(m2); bm.free(); m2.materials.append(cm)
    c=bpy.data.objects.new('WS110_CollegeAve_S_end_curb_%s_return6m_UNVERIFIED'%side,m2); coll.objects.link(c)
mouthW=np.array(rows[-1][-1][:2]); mouthE=np.array(rows[-1][0][:2]); print('E110 mouth W',np.round(mouthW,2),'E',np.round(mouthE,2))
# --- Normal Ave ribbon import (cut the N curb across the College mouth), with curb faces
am=bpy.data.materials['WS27_CollegeAve_asphalt_2020ortho']
for kind in ('carriageway','curb'):
    bm=bmesh.new(); vm={}
    def gv(i,dz=0.0):
        key=(i,dz)
        if key not in vm: x,y,z=V[i]; vm[key]=bm.verts.new((x,y,z+dz))
        return vm[key]
    cut=0
    for nm,fs in G:
        if (kind=='carriageway')!=('carriageway' in nm): continue
        for f in fs:
            cxy=V[f].mean(0)
            if kind=='curb' and nm.endswith('_L'):
                # inside the mouth (between the two curb-return ends along Normal)?
                tN=mouthE-mouthW; L=np.linalg.norm(tN); u=np.dot(cxy[:2]-mouthW,tN/L)
                if -0.2<u<L+0.2 and abs(np.cross(tN/L,cxy[:2]-mouthW))<2.0: cut+=1; continue
            try: bm.faces.new([gv(i) for i in f])
            except ValueError: pass
            if kind=='curb':
                k0,k2,k3,k1=f  # inner k0,k2 ; outer k1,k3
                for a_,b_ in ((k0,k2),(k3,k1)):
                    try: bm.faces.new((gv(a_),gv(b_),gv(b_,-0.40),gv(a_,-0.40)))
                    except ValueError: pass
    print('E110',kind,'faces',len(bm.faces),'mouth cut',cut)
    for fc in bm.faces:
        if abs(fc.normal.z)>0.5 and fc.normal.z<0: fc.normal_flip()
    m3=bpy.data.meshes.new('WS110_NormalAve_'+kind); bm.to_mesh(m3); bm.free(); m3.materials.append(am if kind=='carriageway' else cm)
    c=bpy.data.objects.new('WS110_NormalAve_%s_W11p3_ws84prep_ortho2020_UNVERIFIED'%kind,m3); coll.objects.link(c)
for hn in ('UA_NormalAve_CR618_583841725_727_729_UNVERIFIED','UA_CollegeAve_spur_1557427669_UNVERIFIED'):
    h=bpy.data.objects.get(hn)
    if h: h.hide_render=True; h.hide_viewport=True; print('E110 hid (superseded)',hn)
sw=bpy.data.objects.get('UA_NormalAve_N_sidewalk_583841727_UNVERIFIED')
if sw:
    sc_=np.array([sw.matrix_world@v.co for v in sw.data.vertices]); dd=np.array([cdist(p) for p in sc_[::max(1,len(sc_)//400)]])
    print('E110 UA N sidewalk dist to Normal CL min %.2f med %.2f max %.2f'%(dd.min(),np.median(dd),dd.max()))
bpy.context.view_layer.update()
# --- ground layer: seat terrain + skirt to the 2023 DTM in the block S of y -246, then cap under new paving
pave=[o for o in coll.objects if 'carriageway' in o.name or 'S_end_to' in o.name]
def obvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
PB=[obvh(o) for o in pave]
def pz(x,y):
    zs=[t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0] for t in PB]; zs=[h.z for h in zs if h is not None]; return min(zs) if zs else None
def pzn(x,y,r=1.5):
    best=None
    for dx in (-r,0,r):
        for dy in (-r,0,r):
            z=pz(x+dx,y+dy)
            if z is not None: best=z if best is None else min(best,z)
    return best
for tn in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km'):
    t=bpy.data.objects[tn]; mw=t.matrix_world; inv=mw.inverted(); seat=cap=0; mx=0
    for v in t.data.vertices:
        w=mw@v.co
        if not (-345<w.x<-140 and -320<w.y<-244): continue
        z=w.z; zd=dtm(w.x,w.y)
        if zd is not None and w.y<-246:
            a=min((-246-w.y)/3.0,1.0); nz=z*(1-a)+zd*a
            if abs(nz-z)>0.02: seat+=1; mx=max(mx,abs(nz-z)); z=nz
        p=pzn(w.x,w.y)
        if p is not None and z>p-0.10: z=p-0.10; cap+=1
        if z!=w.z: v.co=inv@Vector((w.x,w.y,z))
    t.data.update(); print('G110',tn,'seat',seat,'maxdz %.2f'%mx,'cap',cap)
# poke probe: terrain/skirt above new paving (original meshes)
for it in range(3):
    TB={tn:obvh(bpy.data.objects[tn]) for tn in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')}
    pokes=0; worst=0
    for o in pave:
        for v in o.data.vertices:
            w=o.matrix_world@v.co
            for tn,tb in TB.items():
                h,nrm,fi,_=tb.ray_cast(Vector((w.x,w.y,300)),Vector((0,0,-1)))
                if h is not None and h.z>w.z-0.03:
                    pokes+=1; worst=max(worst,h.z-w.z); tob=bpy.data.objects[tn]; inv=tob.matrix_world.inverted()
                    for vi in tob.data.polygons[fi].vertices:
                        vv=tob.data.vertices[vi]; ww=tob.matrix_world@vv.co
                        if ww.z>w.z-0.12: vv.co=inv@Vector((ww.x,ww.y,w.z-0.12))
    for tn in TB: bpy.data.objects[tn].data.update()
    print('P110 iter',it,'pokes',pokes,'worst %.2f'%worst)
    if pokes==0: break
bpy.ops.wm.save_mainfile(); print('M110 SAVED',flush=True)
exec(open(R+'scripts/ws105/cut105.py').read().replace('ws105/render_cut105','ws110/render_cut110'))

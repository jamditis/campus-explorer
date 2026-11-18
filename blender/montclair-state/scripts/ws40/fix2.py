import bpy,bmesh,math,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get(); O=bpy.data.objects
def bvh_multi(names):
    bm=bmesh.new()
    for n in names:
        o=O[n]; e=o.evaluated_get(dg); me=e.to_mesh(); t=bmesh.new(); t.from_mesh(me); t.transform(o.matrix_world)
        me2=bpy.data.meshes.new('tmp'); t.to_mesh(me2); bm.from_mesh(me2); bpy.data.meshes.remove(me2); t.free(); e.to_mesh_clear()
    tr=BVHTree.FromBMesh(bm); bm.free(); return tr
def zz(t,x,y):
    r=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400); return r[0].z if r[0] else None
CL=O['WS27_CollegeAve_curb_left_UNVERIFIED']; clv=[CL.matrix_world@v.co for v in CL.data.vertices]
XC={}
for i in range(-125,-50):
    c=[p for p in clv if abs(p.y-i)<0.6 and -215<p.x<-185]
    if c:
        xm=max(p.x for p in c); XC[i]=(xm,max(p.z for p in c if p.x>xm-0.4))
def xc_at(y):
    i0=math.floor(y); i1=i0+1
    if i0 in XC and i1 in XC:
        t=y-i0; return XC[i0][0]*(1-t)+XC[i1][0]*t, XC[i0][1]*(1-t)+XC[i1][1]*t
    k=min(XC,key=lambda k:abs(k-y)); return XC[k]
XB=-192.25; SB=127.94; XT=-190.0; CY0,CY1=-97.2,-87.1
YA,YB=-106.0,-82.0
def sm(t): t=min(max(t,0),1); return t*t*(3-2*t)
def xback(y):
    return XB+1.3*sm((CY0-0.5-y)/1.5)
for n in ('WS40_CollegeAve_east_sidewalk_to_Kasser_steps_concrete_OSM_JOE','WS40_Cole_deck_cut_fascia_concrete_UNVERIFIED'):
    if O.get(n): bpy.data.objects.remove(O[n],do_unlink=True)
TS=bvh_multi(['COLE_plaza_deck_bs','Terrain_LiDAR_DTM_1m'])
ZB={}
for k in range(int((YB-YA)/0.5)+1):
    y=YA+k*0.5; xc,zc=xc_at(y)
    s=zz(TS,xback(y)+0.4,y) or zc
    zo=min(max(s-0.01,zc-0.02),zc+0.30)
    w=sm((max(CY0-y,y-CY1,0))/2.0)   # 0 near steps, 1 beyond 2 m
    ZB[k]=SB*(1-w)+zo*w
def zb(y):
    f=(y-YA)/0.5; k0=max(0,min(int(f),len(ZB)-2)); t=f-k0; return ZB[k0]*(1-t)+ZB[k0+1]*t
def S(x,y):
    xc,zc=xc_at(y); t=min(max((x-xc)/max(xback(y)-xc,0.5),0),1); return zc+(zb(y)-zc)*t
def in_band(x,y,m=0.0): return YA-m<=y<=YB+m and xc_at(y)[0]-0.05<x<xback(y)+m
def in_raise(x,y): return XB-0.1<x<XT+2.0 and CY0-1.5<y<CY1+1.5
for name in ('COLE_plaza_deck_bs','COLE_plaza_edge_bs','Footpaths_OSM'):
    o=O[name]; m=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data); kill=[]
    for f in bm.faces:
        c=m@f.calc_center_median()
        if not (YA-1<c.y<YB+1 and c.x<-180): continue
        if name.startswith('COLE'):
            if in_band(c.x,c.y,0.0) or (YA<=c.y<=YB and c.x<xback(c.y)): kill.append(f)
        else:
            if in_band(c.x,c.y,0.3) or (YA<=c.y<=YB and xc_at(c.y)[0]<c.x<xback(c.y)+0.3) or in_raise(c.x,c.y): kill.append(f)
    bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update(); print('F40b kill',name,len(kill))
# fascia
o=O['COLE_plaza_deck_bs']; bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
fv=[];ff=[]
for e in bm.edges:
    if not e.is_boundary: continue
    a,b=e.verts[0].co.copy(),e.verts[1].co.copy(); my=(a.y+b.y)/2; mx=(a.x+b.x)/2
    if not (YA-3<my<-60) or mx>XT+0.5: continue
    if YA<=my<=YB:
        if mx>xback(my)+2.0: continue
        za=min(S(min(a.x,xback(a.y)),a.y),a.z)-0.06; zb_=min(S(min(b.x,xback(b.y)),b.y),b.z)-0.06
    else:
        if mx>xc_at(my)[0]+2.0: continue
        za=a.z-0.30; zb_=b.z-0.30
    if a.z-za<0.07 and b.z-zb_<0.07: continue
    i=len(fv); fv+=[tuple(a),tuple(b),(b.x,b.y,zb_),(a.x,a.y,za)]; ff.append((i,i+1,i+2,i+3))
bm.free()
CW=O['WS35_Kasser_steps_cheek_walls_UNVERIFIED']; fm=CW.material_slots[0].material
me=bpy.data.meshes.new('WS40_Cole_deck_cut_fascia'); me.from_pydata(fv,[],ff); me.update(); me.materials.append(fm)
fo=bpy.data.objects.new('WS40_Cole_deck_cut_fascia_concrete_UNVERIFIED',me)
for c in CW.users_collection: c.objects.link(fo)
print('F40b fascia',len(ff))
# sidewalk
mat=bpy.data.materials.get('WS3_Concrete_panels_sawcut')
verts=[];faces=[]; NY=int((YB-YA)/0.5)+1; NX=6
for j in range(NY):
    y=YA+(YB-YA)*j/(NY-1); xc,_=xc_at(y); x0=xc-0.02; x1=xback(y)+0.03
    for i in range(NX):
        x=x0+(x1-x0)*i/(NX-1); verts.append((x,y,S(min(x,xback(y)),y)))
for j in range(NY-1):
    for i in range(NX-1):
        a=j*NX+i; faces.append((a,a+1,a+NX+1,a+NX))
top=len(verts)
ring=[j*NX for j in range(NY)]+[(NY-1)*NX+i for i in range(1,NX)]+[j*NX+NX-1 for j in range(NY-2,-1,-1)]+[i for i in range(NX-2,0,-1)]
for k in ring: x,y,z=verts[k]; verts.append((x,y,z-0.2))
for k in range(len(ring)):
    a=ring[k]; b=ring[(k+1)%len(ring)]; faces.append((b,a,top+k,top+(k+1)%len(ring)))
me=bpy.data.meshes.new('WS40_CollegeAve_sidewalk'); me.from_pydata(verts,[],faces); me.update(); me.materials.append(mat)
so=bpy.data.objects.new('WS40_CollegeAve_east_sidewalk_to_Kasser_steps_concrete_OSM_JOE',me)
for c in CW.users_collection: c.objects.link(so)
print('F40b sidewalk y %.1f..%.1f z %.2f..%.2f'%(YA,YB,min(v[2] for v in verts[:top]),max(v[2] for v in verts[:top])))
T=O['Terrain_LiDAR_DTM_1m']; tm=T.matrix_world; ti=tm.inverted(); mv=0
TT0=bvh_multi(['Terrain_LiDAR_DTM_1m'])
for v in T.data.vertices:
    p=tm@v.co
    if not (-200<p.x<-186 and YA-1<p.y<YB+1): continue
    if in_band(p.x,p.y,0.1):
        nz=min(p.z,S(min(p.x,xback(p.y)),p.y)-0.10)
        if nz<p.z-0.003: v.co=ti@Vector((p.x,p.y,nz)); mv+=1
T.data.update(); dg.update(); TT1=bvh_multi(['Terrain_LiDAR_DTM_1m']); print('F40b terrain',mv)
for o in list(O):
    if o.type!='MESH' or o.library or not any(k in o.name.lower() for k in ('grass','lawn')): continue
    mw=o.matrix_world; ob=[mw@Vector(cc) for cc in o.bound_box]
    if max(q.x for q in ob)<-200 or min(q.x for q in ob)>-186 or max(q.y for q in ob)<YA-1 or min(q.y for q in ob)>YB+1: continue
    if len(o.data.vertices)>300000: continue
    bm=bmesh.new(); bm.from_mesh(o.data); kill=[v for v in bm.verts if in_band(*(mw@v.co).xy,0.15)]
    bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(o.data); bm.free(); o.data.update(); print('F40b grass removed',o.name,len(kill))
for name in ('WS35_CollegeAve_bed_posts_black_PHOTO_JOE_20261110','WS35_CollegeAve_bed_chain_black_PHOTO_JOE_20261110'):
    o=O[name]; mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data); seen=set(); kill=[]
    for v in bm.verts:
        if v in seen: continue
        isl=[];st=[v];seen.add(v)
        while st:
            a=st.pop(); isl.append(a)
            for e in a.link_edges:
                b=e.other_vert(a)
                if b not in seen: seen.add(b); st.append(b)
        c=sum((mw@a.co for a in isl),Vector())/len(isl)
        if in_band(c.x,c.y,0.4): kill+=isl
    bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(o.data); bm.free(); o.data.update(); print('F40b posts/chain verts removed',name,len(kill))
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('F40b SAVED')

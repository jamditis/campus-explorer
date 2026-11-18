# sb (Nov 4 2026 ~11:30 AM ET, MAIN, day 8 Student Center: University Promenade + Annex-west walks/lawn; adapted from qs_main.py). ALL UNVERIFIED, reversible: REVERT=1 removes SB_ collections/meshes/cams.
# (1) OSM footways/service road around Richardson that sit on the 3DEP skirt (outside the LiDAR tile) had NO geometry
#     (Footpaths_OSM/Roads_OSM have no verts there) -> draped concrete walk / asphalt ribbons along the OSM centrelines
#     (footway 2.0 m, service 4.5 m), only where the existing networks have no vertex within 1.5 m, skipping building footprints.
# (2) grass clumps (cx_grass instancer) on the lawn round Richardson (box x 30-145, y 218-325), not on walks/roads/buildings.
# (3) camera QS_CAM_eye_richardson_NE_walk.
import bpy, bmesh, os, sys, json, math, random
from mathutils import Vector, kdtree
REV=os.environ.get('REVERT')=='1'
COLW='SB_AnnexWest_promenade_walks_UNVERIFIED'; COLG='SB_AnnexWest_lawn_grass_20261104sb'
X0,X1,Y0,Y1=-175.,-95.,195.,360.
def revert():
    for cn in (COLW,COLG):
        c=bpy.data.collections.get(cn)
        if c:
            for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
            bpy.data.collections.remove(c)
    for me in [m for m in bpy.data.meshes if m.name.startswith('SB_') and m.users==0]: bpy.data.meshes.remove(me)
    for o in [o for o in bpy.data.objects if o.name.startswith('SB_CAM')]: bpy.data.objects.remove(o,do_unlink=True)
    for c in [c for c in bpy.data.cameras if c.name.startswith('SB_CAM') and c.users==0]: bpy.data.cameras.remove(c)
    print('SB reverted')
revert()
if REV:
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
D=json.load(open('data/scene_data.json'))
def pip(x,y,poly):
    ins=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: ins=not ins
    return ins
blds=[f['pts'] for f in D['features'] if f.get('tags',{}).get('building') and f.get('closed',True)]
blds=[p for p in blds if max(q[0] for q in p)>X0-20 and min(q[0] for q in p)<X1+20 and max(q[1] for q in p)>Y0-20 and min(q[1] for q in p)<Y1+20]

def inbld(x,y,m=0.3): return any(pip(x,y,p) for p in blds)
def kd_of(name):
    o=bpy.data.objects[name]; e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    pts=[mw@v.co for v in me.vertices if X0-10<(mw@v.co).x<X1+10 and Y0-10<(mw@v.co).y<Y1+10]
    e.to_mesh_clear(); k=kdtree.KDTree(max(1,len(pts)))
    for i,p in enumerate(pts): k.insert((p.x,p.y,0),i)
    k.balance(); return k,len(pts)
kfp,nfp=kd_of('Footpaths_OSM'); krd,nrd=kd_of('Roads_OSM'); print('SB existing verts in box fp',nfp,'rd',nrd)
GN=['Terrain_LiDAR_DTM_1m','QJ_NE_seam_fill_UNVERIFIED','Context_skirt_3DEP_ortho_4km','QM_terrain_band_underlay_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED','RZ2_SC_LiDAR_ground_patch','QW_DTM_north_edge_ramp_UNVERIFIED']
gnd=[(bpy.data.objects[n].evaluated_get(dg),bpy.data.objects[n].matrix_world) for n in GN if n in bpy.data.objects]
def gz(x,y):
    best=None
    for e,mw in gnd:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    return best
WALKS=[]  # sb review fix: earlier SB walks act as ground for later ones (no 15-20 cm steps where two drapes cross)
def gzw(x,y,off):
    zg=gz(x,y); best=None
    for o in WALKS:
        e=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); mw=o.matrix_world; iw=mw.inverted()
        r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    if zg is None: return None if best is None else best+0.006
    if best is not None and best+0.006>zg+off: return best+0.006
    return zg+off
def ribbon(pts,w,off,name,mat,foot=True):
    # resample, keep runs where network missing and not inside buildings
    S=[]
    for (ax,ay),(bx,by) in zip(pts[:-1],pts[1:]):
        L=math.hypot(bx-ax,by-ay); n=max(1,int(L/0.75))
        for i in range(n): t=i/n; S.append((ax+(bx-ax)*t,ay+(by-ay)*t))
    S.append(tuple(pts[-1]))
    kd=kfp if foot else krd
    keep=[X0<x<X1 and Y0<y<Y1 and kd.find((x,y,0))[2]>1.5 and not inbld(x,y) for x,y in S]
    runs=[];cur=[]
    for s,k in zip(S,keep):
        if k: cur.append(s)
        elif cur: runs.append(cur); cur=[]
    if cur: runs.append(cur)
    bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap'); nq=0
    for r in runs:
        if len(r)<3: continue
        rows=[]
        for i,(x,y) in enumerate(r):
            a=r[max(i-1,0)]; b=r[min(i+1,len(r)-1)]; tx,ty=b[0]-a[0],b[1]-a[1]; l=math.hypot(tx,ty) or 1; nx,ny=-ty/l,tx/l
            L=(x+nx*w/2,y+ny*w/2); R=(x-nx*w/2,y-ny*w/2)
            zl,zc,zr=gzw(L[0],L[1],off),gzw(x,y,off),gzw(R[0],R[1],off)
            if zc is None: rows.append(None); continue
            zl=zc if zl is None else zl; zr=zc if zr is None else zr
            # sb review fix: per-edge drape (follows cross-slope) instead of max of 3 -> no proud downhill edge
            rows.append([bm.verts.new((L[0],L[1],zl)),bm.verts.new((R[0],R[1],zr)),bm.verts.new((L[0],L[1],zl-0.3)),bm.verts.new((R[0],R[1],zr-0.3))])
        for p,q in zip(rows[:-1],rows[1:]):
            if p is None or q is None: continue
            for quad in ((p[0],q[0],q[1],p[1]),(p[2],q[2],q[0],p[0]),(p[1],q[1],q[3],p[3])):
                f=bm.faces.new(quad); nq+=1
                for lp in f.loops: lp[uv].uv=(lp.vert.co.x/2.0,lp.vert.co.y/2.0+lp.vert.co.z/2.0)
    if nq==0: bm.free(); return None
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.uv_layers.new(name='ortho')
    me.materials.append(mat); ob=bpy.data.objects.new(name,me); cw.objects.link(ob); bpy.context.view_layer.update(); WALKS.append(ob); ob['UNVERIFIED_sb']='OSM centreline drape on 3DEP/LiDAR ground; width default'
    return ob,nq
cw=bpy.data.collections.new(COLW); sc.collection.children.link(cw)
mfp=bpy.data.objects['Footpaths_OSM'].material_slots[0].material; mrd=bpy.data.objects['Roads_OSM'].material_slots[0].material
print('SB mats',mfp.name,mrd.name)
built=[]; k_=0
for f in D['features']:
    t=f.get('tags',{}).get('highway')
    if t not in ('footway','service','residential','secondary','path','pedestrian'): continue
    p=f['pts']
    if max(q[0] for q in p)<X0 or min(q[0] for q in p)>X1 or max(q[1] for q in p)<Y0 or min(q[1] for q in p)>Y1: continue
    pts=list(p)
    if f.get('tags',{}).get('area')=='yes': continue
    foot=t in('footway','path','pedestrian')
    w=2.0 if t in('footway','path') else (5.0 if t=='pedestrian' else (4.5 if t=='service' else 7.0))
    k_+=1; r=ribbon(pts,w,0.022+0.002*k_,'SB_%s_%s_UNVERIFIED'%(t,f['id']),mfp if foot else mrd,foot)
    if r: built.append((r[0].name,r[1])); print('SB built',r[0].name,r[1])
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
# ---- grass
D_=float(os.environ.get('D','35')); rnd=random.Random(1104)
okw=('grass','lawn','ortho')
def sm(t): t=min(max(t,0),1); return t*t*(3-2*t)
roadsegs=[]
for f in D['features']:
    t=f.get('tags',{}).get('highway')
    if not t: continue
    hw=1.4 if t in('footway','path') else 2.9 if t=='pedestrian' else (2.9 if t=='service' else 4.5)
    for a,b in zip(f['pts'][:-1],f['pts'][1:]): roadsegs.append((a,b,hw))
roadsegs=[s for s in roadsegs if max(s[0][0],s[1][0])>X0-10 and min(s[0][0],s[1][0])<X1+10 and max(s[0][1],s[1][1])>Y0-10 and min(s[0][1],s[1][1])<Y1+10]
def nearroad(x,y):
    for (ax,ay),(bx,by),hw in roadsegs:
        dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy or 1; t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/L2))
        if (x-ax-t*dx)**2+(y-ay-t*dy)**2<hw*hw: return True
    return False
blk=[]
for o in sc.objects:
    if o.type!='MESH' or o.name in GN or o.hide_render or not o.visible_get(): continue
    nl=o.name.lower()
    if any(k in nl for k in ('grass','tree','shrub','farfield','helper','probe','pc_','cx_')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    bx0=min(v.x for v in bb); bx1=max(v.x for v in bb); by0=min(v.y for v in bb); by1=max(v.y for v in bb)
    if bx1<X0 or bx0>X1 or by1<Y0 or by0>Y1 or (bx1-bx0)*(by1-by0)>4e5: continue
    blk.append((o.evaluated_get(dg),o.matrix_world.inverted(),bx0,bx1,by0,by1))
print('SB blockers',len(blk))
pts=[]; st={'t':0,'b':0,'m':0,'r':0}; FADE=6.0
for _ in range(int(D_*(X1-X0)*(Y1-Y0))):
    x=X0+rnd.random()*(X1-X0); y=Y0+rnd.random()*(Y1-Y0)
    if rnd.random()>sm(min(x-X0,X1-x,y-Y0,Y1-y)/FADE): continue
    st['t']+=1
    if inbld(x,y) or nearroad(x,y): st['r']+=1; continue
    best=None
    for e,mw in gnd:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best[0]: best=(z,e,r[2],r[3],mw)
    if best is None: st['b']+=1; continue
    z,e,n,fi,mw=best
    if (mw.to_3x3()@n).normalized().z<0.6: st['b']+=1; continue
    ms=e.material_slots
    if ms:
        mn=ms[e.data.polygons[fi].material_index].name.lower() if fi<len(e.data.polygons) else ''
        if not any(k in mn for k in okw): st['m']+=1; continue
    hit=False
    for b,iw,bx0,bx1,by0,by1 in blk:
        if x<bx0 or x>bx1 or y<by0 or y>by1: continue
        o0=iw@Vector((x,y,z+40)); o1=iw@Vector((x,y,z-0.08)); d=o1-o0
        if b.ray_cast(o0,d.normalized(),distance=d.length)[0]: hit=True; break
    if hit: st['b']+=1; continue
    pts.append((x,y,z-0.005))
cg=bpy.data.collections.new(COLG); sc.collection.children.link(cg)
me=bpy.data.meshes.new('SB_AnnexWest_lawn_grass_points_UNVERIFIED'); me.from_pydata(pts,[],[])
ob=bpy.data.objects.new('SB_AnnexWest_lawn_grass_points_UNVERIFIED',me); cg.objects.link(ob)
m=ob.modifiers.new('cx_grass','NODES'); m.node_group=bpy.data.objects['cx_grass_points'].modifiers['cx_grass'].node_group
ob['UNVERIFIED_sb']='grass clumps west of the Annex box x %g-%g y %g-%g D=%g'%(X0,X1,Y0,Y1,D_)
print('SB_GRASS',len(pts),st)
# ---- camera: eye level on the promenade south of the Annex looking north
cd=bpy.data.cameras.new('SB_CAM_eye_promenade_from_S'); cd.lens=28; cam=bpy.data.objects.new('SB_CAM_eye_promenade_from_S',cd); cw.objects.link(cam)
z0=gz(-118.0,240.0) or 140.0; cam.location=(-118.0,240.0,z0+1.65)
d=Vector((-108.0,300.0,z0+2.0))-cam.location; cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
json.dump({'built':built,'grass':len(pts)},open('data/sb/added.json','w'))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

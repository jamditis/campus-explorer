# qx (Nov 3 2026 ~2:35 AM ET, MAIN, day 7 Richardson N/W ground). ALL UNVERIFIED, reversible: REVERT=1.
# Finding: the 1 m-DTM Footpaths_OSM network stops at y~248. North of it the two OSM pedestrian AREAS (313024781 plaza
# round the Student Center, 313027423 Student Center Annex plaza) had no paving, and qs/qv/qx grass treated those closed
# areas like lines (4.5 m bare band along the outline, grass INSIDE the plaza). This (1) paves the area interiors that have no
# existing Footpaths_OSM surface (1 m grid conformal to the OSM outline, draped ground+4 cm, 0.3 m edge curtain, Footpaths_OSM
# material), (2) drapes 2 m footway ribbons along OSM footways in the box where no walk exists, (3) removes grass points
# inside the new paving (coords saved for revert) and (4) refills the bare outline bands with grass at the qv/qx density.
import bpy, bmesh, os, json, math, random
import numpy as np
from mathutils import Vector, kdtree
REV=os.environ.get('REVERT')=='1'; COL='QX_StudentCenter_plaza_paving_UNVERIFIED'; BK='data/qx/grass_removed.npz'
GRS=['QV_Richardson_NW_lawn_grass_points_UNVERIFIED','QX_Richardson_W_ramp_grass_points_UNVERIFIED']
def revert():
    c=bpy.data.collections.get(COL)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
    for me in [m for m in bpy.data.meshes if m.name.startswith('QXP_') and m.users==0]: bpy.data.meshes.remove(me)
    if os.path.exists(BK):
        z=np.load(BK)
        for n in GRS:
            if n in z.files and n in bpy.data.objects and len(z[n]):
                me=bpy.data.objects[n].data; k=len(me.vertices); me.vertices.add(len(z[n])); 
                for i,p in enumerate(z[n]): me.vertices[k+i].co=Vector(p)
                me.update()
        os.rename(BK,BK+'.restored'); print('QXP grass restored')
    print('QXP reverted')
revert()
if REV:
    if os.environ.get('QXSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
D=json.load(open('data/scene_data.json')); F={str(f['id']):f for f in D['features']}
BX0,BX1,BY0,BY1=-60.,60.,238.,345.
def pip(x,y,poly):
    ins=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: ins=not ins
    return ins
AREAS=[F[i]['pts'] for i in ('313024781','313027423')]
def inarea(x,y): return any(pip(x,y,p) for p in AREAS)
blds=[f['pts'] for f in D['features'] if f.get('tags',{}).get('building') and f.get('closed',True)]
blds.append(json.load(open('data/qp/rich_poly.json'))['outer'])
blds=[p for p in blds if max(q[0] for q in p)>BX0-20 and min(q[0] for q in p)<BX1+20 and max(q[1] for q in p)>BY0-20 and min(q[1] for q in p)<BY1+20]
def inbld(x,y): return any(pip(x,y,p) for p in blds)
GN=['QW_DTM_north_edge_ramp_UNVERIFIED','Terrain_LiDAR_DTM_1m','QJ_NE_seam_fill_UNVERIFIED','Context_skirt_3DEP_ortho_4km','QM_terrain_band_underlay_UNVERIFIED']
gnd=[(bpy.data.objects[n].evaluated_get(dg),bpy.data.objects[n].matrix_world) for n in GN if n in bpy.data.objects]
def gz(x,y):
    best=None
    for e,mw in gnd:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    return best
FP=bpy.data.objects['Footpaths_OSM']; fpe=FP.evaluated_get(dg); fpi=FP.matrix_world.inverted()
def has_fp(x,y,z):
    r=fpe.ray_cast(fpi@Vector((x,y,z+30)),(fpi.to_3x3()@Vector((0,0,-1))).normalized())
    return r[0] and (FP.matrix_world@r[1]).z>z-0.6
mfp=FP.material_slots[0].material
cg=bpy.data.collections.new(COL); sc.collection.children.link(cg)
# ---- (1) plaza paving
st={}
for aid in ('313024781','313027423'):
    poly=F[aid]['pts'][:-1] if F[aid]['pts'][0]==F[aid]['pts'][-1] else F[aid]['pts']
    bm=bmesh.new(); vs=[bm.verts.new((x,y,0)) for x,y in poly]; bm.faces.new(vs)
    xs=[p[0] for p in poly]; ys=[p[1] for p in poly]
    for X in range(int(min(xs))+1,int(max(xs))+1):
        g=bm.verts[:]+bm.edges[:]+bm.faces[:]; bmesh.ops.bisect_plane(bm,geom=g,plane_co=(X,0,0),plane_no=(1,0,0))
    for Y in range(int(min(ys))+1,int(max(ys))+1):
        g=bm.verts[:]+bm.edges[:]+bm.faces[:]; bmesh.ops.bisect_plane(bm,geom=g,plane_co=(0,Y,0),plane_no=(0,1,0))
    bmesh.ops.triangulate(bm,faces=bm.faces[:])
    gzv={}
    for v in bm.verts:
        z=gz(v.co.x,v.co.y); gzv[v]=z
    drop=[]
    for f in bm.faces:
        c=f.calc_center_median(); zc=gz(c.x,c.y)
        if zc is None or any(gzv[v] is None for v in f.verts) or inbld(c.x,c.y) or has_fp(c.x,c.y,zc) or c.y<BY0: drop.append(f)
    bmesh.ops.delete(bm,geom=drop,context='FACES')
    for v in bm.verts:
        if gzv.get(v) is not None: v.co.z=gzv[v]+0.04
    # edge curtain
    bnd=[e for e in bm.edges if e.is_boundary]
    for e in bnd:
        a,b=e.verts; a2=bm.verts.new(a.co-Vector((0,0,0.3))); b2=bm.verts.new(b.co-Vector((0,0,0.3)))
        try: bm.faces.new((b,a,a2,b2))
        except ValueError: pass
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    uv=bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        for lp in f.loops: lp[uv].uv=(lp.vert.co.x/2.0,lp.vert.co.y/2.0+lp.vert.co.z/2.0)
    for f in bm.faces: f.smooth=False
    nm='QXP_pedestrian_area_%s_paving_UNVERIFIED'%aid; me=bpy.data.meshes.new(nm); bm.to_mesh(me); st[aid]=len(bm.faces); bm.free()
    me.uv_layers.new(name='ortho'); me.materials.append(mfp)
    ob=bpy.data.objects.new(nm,me); cg.objects.link(ob); ob['UNVERIFIED_qx']='OSM pedestrian area outline, draped ground+4cm, paving material = Footpaths_OSM (no photo)'
print('QXP plaza faces',st)
# ---- (2) footway ribbons where missing
k=kdtree.KDTree(200000); n=0
fme=fpe.to_mesh()
for v in fme.vertices:
    p=FP.matrix_world@v.co
    if BX0-10<p.x<BX1+10 and BY0-10<p.y<BY1+10: k.insert((p.x,p.y,0),n); n+=1
fpe.to_mesh_clear()
wc=bpy.data.collections.get('QW_Richardson_walk_ext_UNVERIFIED')
xw=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith('QS_footway') or o.name.startswith('QS_service') or (wc and o.name in wc.objects and not o.name.startswith('QW_CAM')))]
for o in xw:
    for v in o.data.vertices:
        p=o.matrix_world@v.co
        if BX0-10<p.x<BX1+10 and BY0-10<p.y<BY1+10: k.insert((p.x,p.y,0),n); n+=1
print('QXP existing-walk objects',len(xw),'verts',n)
k.balance()
rib=[]
for f in D['features']:
    t=f.get('tags',{}).get('highway')
    if t not in ('footway','path') or f.get('closed') and f['pts'][0]==f['pts'][-1]: continue
    p=f['pts']
    if max(q[0] for q in p)<BX0 or min(q[0] for q in p)>BX1 or max(q[1] for q in p)<BY0 or min(q[1] for q in p)>BY1: continue
    S=[]
    for (ax,ay),(bx,by) in zip(p[:-1],p[1:]):
        L=math.hypot(bx-ax,by-ay); m=max(1,int(L/0.75))
        for i in range(m): tt=i/m; S.append((ax+(bx-ax)*tt,ay+(by-ay)*tt))
    S.append(tuple(p[-1]))
    keep=[BX0<x<BX1 and BY0<y<BY1 and (k.find((x,y,0))[2] if n else 99)>1.5 and not inbld(x,y) and not inarea(x,y) for x,y in S]
    runs=[];cur=[]
    for s,kk in zip(S,keep):
        if kk: cur.append(s)
        elif cur: runs.append(cur); cur=[]
    if cur: runs.append(cur)
    bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap'); nq=0; w=2.0
    for r in runs:
        if len(r)<3: continue
        rows=[]
        for i,(x,y) in enumerate(r):
            a=r[max(i-1,0)]; b=r[min(i+1,len(r)-1)]; tx,ty=b[0]-a[0],b[1]-a[1]; l=math.hypot(tx,ty) or 1; nx,ny=-ty/l,tx/l
            Lp=(x+nx*w/2,y+ny*w/2); Rp=(x-nx*w/2,y-ny*w/2)
            zs=[z for z in (gz(*Lp),gz(x,y),gz(*Rp)) if z is not None]
            if not zs: rows.append(None); continue
            z=max(zs)+0.05
            rows.append([bm.verts.new((Lp[0],Lp[1],z)),bm.verts.new((Rp[0],Rp[1],z)),bm.verts.new((Lp[0],Lp[1],z-0.3)),bm.verts.new((Rp[0],Rp[1],z-0.3))])
            rib.append((x,y))
        for pp,qq in zip(rows[:-1],rows[1:]):
            if pp is None or qq is None: continue
            for quad in ((pp[0],qq[0],qq[1],pp[1]),(pp[2],qq[2],qq[0],pp[0]),(pp[1],qq[1],qq[3],pp[3])):
                fc=bm.faces.new(quad); nq+=1
                for lp in fc.loops: lp[uv].uv=(lp.vert.co.x/2.0,lp.vert.co.y/2.0+lp.vert.co.z/2.0)
        # end caps (qx fix: open slab ends showed a dark interior); close the first/last row of each continuous piece
        for i,rw in enumerate(rows):
            if rw is None: continue
            first=(i==0 or rows[i-1] is None); last=(i==len(rows)-1 or rows[i+1] is None)
            if first or last:
                fc=bm.faces.new((rw[0],rw[1],rw[3],rw[2])); nq+=1
                for lp in fc.loops: lp[uv].uv=(lp.vert.co.x/2.0,lp.vert.co.y/2.0+lp.vert.co.z/2.0)
    if nq==0: bm.free(); continue
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    nm='QXP_footway_%s_UNVERIFIED'%f['id']; me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free()
    me.uv_layers.new(name='ortho'); me.materials.append(mfp); ob=bpy.data.objects.new(nm,me); cg.objects.link(ob)
    ob['UNVERIFIED_qx']='OSM footway centreline drape, width 2 m default'; print('QXP ribbon',nm,nq)
kr=kdtree.KDTree(max(1,len(rib)))
for i,(x,y) in enumerate(rib): kr.insert((x,y,0),i)
kr.balance()
def onrib(x,y,d=1.3): return bool(rib) and kr.find((x,y,0))[2]<d
# ---- (3) remove grass inside new paving / on ribbons
rem={}
for gname in GRS:
    o=bpy.data.objects.get(gname)
    if not o: continue
    me=o.data; co=np.zeros(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    bad=np.array([inarea(x,y) or onrib(x,y) for x,y,z in co],bool)
    rem[gname]=co[bad]
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.verts[i] for i in np.nonzero(bad)[0]],context='VERTS'); bm.to_mesh(me); bm.free(); me.update()
    print('QXP grass removed',gname,int(bad.sum()))
np.savez(BK,**rem)
# ---- (4) refill bare outline bands
def sm(t): t=min(max(t,0),1); return t*t*(3-2*t)
AIDS=('313024781','313027423'); segs_old=[];segs_new=[]
for f in D['features']:
    t=f.get('tags',{}).get('highway')
    if not t: continue
    hw=1.4 if t in('footway','path') else (2.9 if t=='service' else 4.5)
    for a,b in zip(f['pts'][:-1],f['pts'][1:]):
        segs_old.append((a,b,hw))
        if str(f['id']) not in AIDS: segs_new.append((a,b,hw))
def near(segs,x,y):
    for (ax,ay),(bx,by),hw in segs:
        dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy or 1; t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/L2))
        if (x-ax-t*dx)**2+(y-ay-t*dy)**2<hw*hw: return True
    return False
segs_old=[s for s in segs_old if max(s[0][0],s[1][0])>-55 and min(s[0][0],s[1][0])<160 and max(s[0][1],s[1][1])>230 and min(s[0][1],s[1][1])<355]
segs_new=[s for s in segs_new if max(s[0][0],s[1][0])>-55 and min(s[0][0],s[1][0])<160 and max(s[0][1],s[1][1])>230 and min(s[0][1],s[1][1])<355]
rnd=random.Random(1103002); pts=[]; DEN=35.0
GX0,GX1,GY0,GY1=-45.,150.,240.,345.
blk=[(o.evaluated_get(dg),o.matrix_world.inverted()) for o in cg.objects]
for _ in range(int(DEN*(GX1-GX0)*(GY1-GY0))):
    x=GX0+rnd.random()*(GX1-GX0); y=GY0+rnd.random()*(GY1-GY0)
    wv=sm(min(x+15,150-x,y-240,345-y)/8.0) if (-15<x<150) else 0.0
    wx=(1-wv)*sm(min(x+45,y-240,345-y)/8.0) if x<-7 else 0.0
    if rnd.random()>wv+wx: continue
    if not near(segs_old,x,y) or near(segs_new,x,y) or inarea(x,y) or onrib(x,y,1.4) or inbld(x,y): continue
    z=gz(x,y)
    if z is None: continue
    pts.append((x,y,z-0.005))
me=bpy.data.meshes.new('QXP_band_refill_grass_points_UNVERIFIED'); me.from_pydata(pts,[],[])
ob=bpy.data.objects.new('QXP_band_refill_grass_points_UNVERIFIED',me); cg.objects.link(ob)
m=ob.modifiers.new('cx_grass','NODES'); m.node_group=bpy.data.objects['cx_grass_points'].modifiers['cx_grass'].node_group
print('QXP band refill',len(pts))
if os.environ.get('QXSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

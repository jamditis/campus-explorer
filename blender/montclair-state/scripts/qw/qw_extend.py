# qw (Nov 3 2026 ~1:40 AM ET, MAIN, day 7 Richardson surroundings). ALL UNVERIFIED, reversible: REVERT=1 removes QW_ ext collection/meshes.
# The qs walk/service ribbons were clipped at the qs work box (x 30-145, y 218-325), so they ended in mid-lawn
# (most visibly the footway toward the Student Center at x=30 and the two footways at y=325). This extends the same OSM
# centrelines (313027428, 313027436, 546643369, 546643370) out to x 10-178 / y 218-352, same widths, draped on the same
# ground, snapped edge-to-edge onto the qs end rows; runs stop at the existing Footpaths/Roads network (1.5 m) or at building
# footprints; ends that stop in open lawn at the new box edge get a 3 m taper + rounded tip so nothing ends as a cut slab.
# New footway pieces reuse the qt joint material + 'qt_sl' UVs and get qt-style soil edge strips on their long sides.
import bpy, bmesh, os, json, math
from mathutils import Vector, kdtree
REV=os.environ.get('REVERT')=='1'
COL='QW_Richardson_walk_ext_UNVERIFIED'
def revert():
    c=bpy.data.collections.get(COL)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
    for me in [m for m in bpy.data.meshes if m.name.startswith('QW_') and m.users==0]: bpy.data.meshes.remove(me)
    print('QW ext reverted')
revert()
if REV:
    if os.environ.get('QWSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
X0,X1,Y0,Y1=30.,145.,218.,325.          # qs box
NX0,NX1,NY0,NY1=10.,178.,218.,352.      # extended box
D=json.load(open('data/scene_data.json')); F={str(f['id']):f for f in D['features']}
def pip(x,y,poly):
    ins=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: ins=not ins
    return ins
blds=[f['pts'] for f in D['features'] if f.get('tags',{}).get('building') and f.get('closed',True)]
blds=[p for p in blds if max(q[0] for q in p)>NX0-20 and min(q[0] for q in p)<NX1+20 and max(q[1] for q in p)>NY0-20 and min(q[1] for q in p)<NY1+20]
blds.append(json.load(open('data/qp/rich_poly.json'))['outer'])
def inbld(x,y): return any(pip(x,y,p) for p in blds)
def kd_of(names,box):
    pts=[]
    for name in names:
        o=bpy.data.objects[name]; e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
        pts+=[mw@v.co for v in me.vertices if box[0]-10<(mw@v.co).x<box[1]+10 and box[2]-10<(mw@v.co).y<box[3]+10]
        e.to_mesh_clear()
    k=kdtree.KDTree(max(1,len(pts)))
    for i,p in enumerate(pts): k.insert((p.x,p.y,0),i)
    k.balance(); return k,len(pts)
kfp0,_=kd_of(['Footpaths_OSM'],(X0,X1,Y0,Y1)); krd0,_=kd_of(['Roads_OSM'],(X0,X1,Y0,Y1))
kfp,nf=kd_of(['Footpaths_OSM'],(NX0,NX1,NY0,NY1)); krd,nr=kd_of(['Roads_OSM'],(NX0,NX1,NY0,NY1))
print('QW net verts',nf,nr)
GN=['Terrain_LiDAR_DTM_1m','QJ_NE_seam_fill_UNVERIFIED','Context_skirt_3DEP_ortho_4km','QM_terrain_band_underlay_UNVERIFIED']
gnd=[(bpy.data.objects[n].evaluated_get(dg),bpy.data.objects[n].matrix_world) for n in GN if n in bpy.data.objects]
def gz(x,y):
    best=None
    for e,mw in gnd:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    return best
def proj(poly,x,y):
    best=(1e9,0,0); acc=0
    for (ax,ay),(bx,by) in zip(poly[:-1],poly[1:]):
        dx,dy=bx-ax,by-ay; L=math.hypot(dx,dy) or 1e-9
        t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/(L*L))); px,py=ax+dx*t,ay+dy*t; d=math.hypot(x-px,y-py)
        if d<best[0]: best=(d,((x-ax)*(-dy)+(y-ay)*dx)/L,acc+t*L)
        acc+=L
    return best[1],best[2]
col=bpy.data.collections.new(COL); sc.collection.children.link(col)
soilm=bpy.data.materials.get('QT_walk_soil_edge_UNVERIFIED')
rep={}
ALLS=[]
for _f in ('313027428','313027436','546643369','546643370'):
    _p=F[_f]['pts']
    for (ax,ay),(bx,by) in zip(_p[:-1],_p[1:]):
        _n=max(1,int(math.hypot(bx-ax,by-ay)/0.5))
        for _i in range(_n+1): ALLS.append((_f,ax+(bx-ax)*_i/_n,ay+(by-ay)*_i/_n))
def nearother(fid,x,y,r=2.5): return any(f!=fid and (x-px)**2+(y-py)**2<r*r for f,px,py in ALLS)
for fid,typ in (('313027428','footway'),('313027436','footway'),('546643369','footway'),('546643370','service')):
    src=bpy.data.objects.get('QS_%s_%s_UNVERIFIED'%(typ,fid))
    if not src: print('QW missing',fid); continue
    w=2.0 if typ=='footway' else 4.5
    pts=[tuple(p) for p in F[fid]['pts']]
    S=[]
    for (ax,ay),(bx,by) in zip(pts[:-1],pts[1:]):
        L=math.hypot(bx-ax,by-ay); n=max(1,int(L/0.75))
        for i in range(n): t=i/n; S.append((ax+(bx-ax)*t,ay+(by-ay)*t))
    S.append(pts[-1])
    k0=kfp0 if w<3 else krd0; k1=kfp if w<3 else krd
    keep0=[X0<x<X1 and Y0<y<Y1 and k0.find((x,y,0))[2]>1.5 and not inbld(x,y) for x,y in S]
    keep1=[(not keep0[i]) and NX0<x<NX1 and NY0<y<NY1 and k1.find((x,y,0))[2]>1.5 and not inbld(x,y) for i,(x,y) in enumerate(S)]
    # src top verts (world) for snapping, and its offset above ground at the ends
    mw=src.matrix_world; sv=[mw@v.co for v in src.data.vertices]
    ks=kdtree.KDTree(len(sv))
    for i,p in enumerate(sv): ks.insert(p,i)
    ks.balance()
    runs=[]; cur=[]
    for i,k in enumerate(keep1):
        if k: cur.append(i)
        elif cur: runs.append(cur); cur=[]
    if cur: runs.append(cur)
    bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap'); nq=0; info=[]
    for r in runs:
        joinA=r[0]>0 and keep0[r[0]-1]; joinB=r[-1]<len(S)-1 and keep0[r[-1]+1]
        idx=([r[0]-1] if joinA else [])+r+([r[-1]+1] if joinB else [])
        if len(idx)<3: continue
        def netend(i):
            x,y=S[i]; return k1.find((x,y,0))[2]<3.0 or inbld(x,y) or nearother(fid,x,y)
        # free (taper) ends: not joined to qs, at the new box edge in open lawn
        freeA=not joinA and not netend(max(idx[0]-1,0)) and not netend(idx[0]); freeB=not joinB and not netend(min(idx[-1]+1,len(S)-1)) and not netend(idx[-1])
        # offset above ground from the qs end row we snap to
        off=0.05
        for j in ([idx[0]] if joinA else [])+([idx[-1]] if joinB else []):
            x,y=S[j]; g=gz(x,y); co,_,dd=ks.find((x,y,(g or 0)+0.05))
            if g is not None and dd<2.0: off=max(0.03,min(0.12,co.z-g))
        # cumulative length for taper
        cl=[0.0]
        for a,b in zip(idx[:-1],idx[1:]): cl.append(cl[-1]+math.hypot(S[b][0]-S[a][0],S[b][1]-S[a][1]))
        TL=3.0; rows=[]
        for jj,i in enumerate(idx):
            x,y=S[i]; a=S[max(i-1,0)]; b=S[min(i+1,len(S)-1)]
            tx,ty=b[0]-a[0],b[1]-a[1]; l=math.hypot(tx,ty) or 1; nx,ny=-ty/l,tx/l
            ww=w
            if freeA and cl[jj]<TL: t=cl[jj]/TL; ww=w*(0.35+0.65*math.sqrt(max(0,1-(1-t)**2)))
            if freeB and cl[-1]-cl[jj]<TL: t=(cl[-1]-cl[jj])/TL; ww=min(ww,w*(0.35+0.65*math.sqrt(max(0,1-(1-t)**2))))
            Lp=(x+nx*ww/2,y+ny*ww/2); Rp=(x-nx*ww/2,y-ny*ww/2)
            zs=[z for z in (gz(*Lp),gz(x,y),gz(*Rp)) if z is not None]
            if not zs: rows.append(None); continue
            z=max(zs)+off
            vL=Vector((Lp[0],Lp[1],z)); vR=Vector((Rp[0],Rp[1],z))
            if (jj==0 and joinA) or (jj==len(idx)-1 and joinB):   # snap onto the qs end row
                for vv in (vL,vR):
                    co,_,dd=ks.find(vv)
                    if dd<0.6: vv.x,vv.y,vv.z=co.x,co.y,co.z
            rows.append([bm.verts.new(vL),bm.verts.new(vR),bm.verts.new((vL.x,vL.y,vL.z-0.3)),bm.verts.new((vR.x,vR.y,vR.z-0.3))])
        for p,q in zip(rows[:-1],rows[1:]):
            if p is None or q is None: continue
            for quad in ((p[0],q[0],q[1],p[1]),(p[2],q[2],q[0],p[0]),(p[1],q[1],q[3],p[3])):
                f=bm.faces.new(quad); nq+=1
        # end caps on free ends (front face) so the tip doesn't show an open slab
        for end,fr in ((rows[0],freeA),(rows[-1],freeB)):
            if fr and end: bm.faces.new((end[0],end[1],end[3],end[2])); nq+=1
        info.append(dict(n=len(idx),joinA=joinA,joinB=joinB,freeA=freeA,freeB=freeB,off=round(off,3),a=[round(v,1) for v in S[idx[0]]],b=[round(v,1) for v in S[idx[-1]]]))
    if nq==0: bm.free(); rep[fid]=info; continue
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.001)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new('QW_%s_%s_ext'%(typ,fid)); bm.to_mesh(me); bm.free()
    for f in me.polygons:
        for li in f.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co; me.uv_layers['UVMap'].data[li].uv=(co.x/2.0,co.y/2.0+co.z/2.0)
    me.uv_layers.new(name='ortho')
    if typ=='footway':
        ul=me.uv_layers.new(name='qt_sl')
        for f in me.polygons:
            for li in f.loop_indices:
                co=me.vertices[me.loops[li].vertex_index].co; s,a=proj(pts,co.x,co.y); ul.data[li].uv=(s,a)
    me.materials.append(src.material_slots[0].material)
    ob=bpy.data.objects.new('QW_%s_%s_ext_UNVERIFIED'%(typ,fid),me); col.objects.link(ob)
    ob['UNVERIFIED_qw']='extension of the qs OSM centreline drape past the qs box; widths default; tapered free ends are a visual choice'
    # soil strips on long top boundary edges (skip edges touching the qs join rows: they lie on the qs mesh)
    if typ=='footway' and soilm:
        bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
        out=bmesh.new(); suvl=out.loops.layers.uv.new('qt_soil'); out.loops.layers.uv.new('ortho'); ns=0
        for e in bm.edges:
            tops=[f for f in e.link_faces if f.normal.z>0.7]
            if len(tops)!=1 or len(e.link_faces)<2: continue
            a,b=e.verts[0].co,e.verts[1].co
            if ks.find(a)[2]<0.01 and ks.find(b)[2]<0.01: continue
            d=Vector((b.x-a.x,b.y-a.y,0))
            if d.length<0.05: continue
            d.normalize(); n=Vector((-d.y,d.x,0)); c=tops[0].calc_center_median(); mid=(a+b)/2
            if n.dot(Vector((mid.x-c.x,mid.y-c.y,0)))<0: n=-n
            vs=[]
            for p,qq in ((a,0),(b,0),(b,1),(a,1)):
                x,y=p.x+n.x*0.22*qq,p.y+n.y*0.22*qq; z=gz(x,y)
                vs.append(out.verts.new((x,y,(z if z is not None else p.z-0.06)+0.012)))
            ff=out.faces.new(vs)
            for lp,(qa,qb) in zip(ff.loops,((0,0),(0,0),(1,0),(1,0))): lp[suvl].uv=(qa,qb)
            ns+=1
        bm.free()
        if ns:
            for ff in out.faces:
                ff.normal_update()
                if ff.normal.z<0: ff.normal_flip()
            sme=bpy.data.meshes.new('QW_soil_'+fid); out.to_mesh(sme); sme.materials.append(soilm)
            so=bpy.data.objects.new('QW_soil_edge_%s_ext_UNVERIFIED'%fid,sme); col.objects.link(so); so['UNVERIFIED_qw']='worn soil strip, visual approximation'
        out.free()
    rep[fid]=info; print('QW built',ob.name,nq,info)
json.dump(rep,open('data/qw/extend.json','w'),indent=1)
if os.environ.get('QWSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

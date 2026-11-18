# Session mu (Oct 29 2026): close the raw main-roof eave cut ends left by mt at the two sides of the CCOM west entrance gable.
# 1) bisect + trim every eave item to one clean plane per side (S u=2.355, N u=12.085);
# 2) boxed eave return per side (fascia/soffit box + sloped tile cap) from that plane to the pavilion side face (u 3.197 / 10.397), end board flush under the gable rake;
# 3) convex-hull end caps on the cut gutter + coping ends; 4) valley flashing strip where each gable roof slab meets the main hip roof.
# Detail type is standard practice; no photo of these ends -> all UNVERIFIED.
import bpy, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
def P(u,z,w): v=t*u+n*w; return Vector((v.x,v.y,z))
U0,U1=3.197,10.397
US,UN=2.361,12.085
M=bpy.data.materials
col=bpy.data.collections.new('MS_CCOM_gable_eave_returns_20261029mu'); bpy.context.scene.collection.children.link(col)
ST='standard eave-return/valley detail, no photo of these ends; UNVERIFIED (session mu)'
def mk(name,verts,faces,mat):
    me=bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts],[],faces); me.update()
    me.materials.append(M[mat]); o=bpy.data.objects.new(name,me); col.objects.link(o); o['status']=ST
    for p in me.polygons: p.use_smooth=False
    return o
def prism(name,prof,ua,ub,mat):
    # prof: (w,z) polygon CCW seen from +u; extrude ua->ub along u
    k=len(prof); vs=[P(ua,z,w) for w,z in prof]+[P(ub,z,w) for w,z in prof]
    fs=[list(range(k))[::-1],list(range(k,2*k))]+[[i,(i+1)%k,k+(i+1)%k,k+i] for i in range(k)]
    o=mk(name,vs,fs,mat)
    o.data.validate(); o.data.update()
    # make normals consistent outward
    bm=bmesh.new(); bm.from_mesh(o.data); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(o.data); bm.free()
    return o
skip=('CCOM entrance','CCOM tower','CCOM atrium')
trimmed=[]; caps=[]
for s,(UA,UB) in (('S',(US,U0+0.7)),('N',(U1-0.7,UN))):
    ucut=US if s=='S' else UN
    for o in list(bpy.data.objects):
        if o.type!='MESH' or o.hide_render or o.name.startswith(skip) or 'roof (LiDAR)' in o.name or o.users_collection[0].name.startswith('MS_CCOM'): continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if max(v.z for v in bb)<146.4 or min(v.z for v in bb)>147.9: continue
        if max(v.dot(n) for v in bb)<21.9 or min(v.dot(n) for v in bb)>23.4: continue
        if min(v.dot(t) for v in bb)>UB or max(v.dot(t) for v in bb)<UA: continue
        if o.data.users>1: print('SKIP shared',o.name); continue
        mw=o.matrix_world; mi=mw.inverted()
        bm=bmesh.new(); bm.from_mesh(o.data)
        def inb(c): u=c.dot(t); w=c.dot(n); return UA<u<UB and 21.9<w<23.4 and 146.4<c.z<147.9
        if 'Downspouts' in o.name:
            # orphan gooseneck stub (no gutter left on the N end after mt) -> remove the whole island
            seed=[v for v in bm.verts if inb(mw@v.co)]; isl=set(seed); st=list(seed)
            while st:
                v=st.pop()
                for e in v.link_edges:
                    w2=e.other_vert(v)
                    if w2 not in isl: isl.add(w2); st.append(w2)
            if isl:
                zs=[(mw@v.co).z for v in isl]; print('DOWNSPOUT island',len(isl),'z',round(min(zs),3),round(max(zs),3))
                if min(zs)>146.0: bmesh.ops.delete(bm,geom=list(isl),context='VERTS'); bm.to_mesh(o.data); o.data.update(); trimmed.append((s,o.name,'island')); 
            bm.free(); continue
        if not any(inb(mw@f.calc_center_median()) for f in bm.faces): bm.free(); continue
        nl=(mw.to_3x3().transposed()@t).normalized()
        geom=bm.verts[:]+bm.edges[:]+bm.faces[:]
        bmesh.ops.bisect_plane(bm,geom=geom,dist=0.0005,plane_co=mi@P(ucut,147,22.6),plane_no=nl)
        kill=[f for f in bm.faces if inb(mw@f.calc_center_median())]
        bmesh.ops.delete(bm,geom=kill,context='FACES')
        loose=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=loose,context='VERTS')
        cut=[(mw@v.co) for v in bm.verts if abs((mw@v.co).dot(t)-ucut)<0.002 and 21.9<(mw@v.co).dot(n)<23.4 and 146.4<(mw@v.co).z<147.9]
        bm.to_mesh(o.data); o.data.update(); bm.free()
        trimmed.append((s,o.name,len(kill)))
        print('CUTV',s,o.name[:30],len(cut))
        if ('Gutter' in o.name or 'coping' in o.name) and len(cut)>=3:
            pts=sorted(set((round(p.dot(n),4),round(p.z,4)) for p in cut))
            # 2D convex hull
            def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
            lo=[];
            for p in pts:
                while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0: lo.pop()
                lo.append(p)
            up=[]
            for p in reversed(pts):
                while len(up)>=2 and cross(up[-2],up[-1],p)<=0: up.pop()
                up.append(p)
            hull=lo[:-1]+up[:-1]
            if len(hull)>=3:
                d=0.006 if s=='S' else -0.006
                c=prism('CCOM gable eave end cap %s %s (mu)'%(s,'gutter' if 'Gutter' in o.name else 'coping'),[(w,z) for w,z in hull],ucut+d*0.0,ucut+d,o.data.materials[0].name)
                caps.append(c.name)
g=bpy.data.objects['Gutters half-round (3f, Life/CCOM UNVERIFIED)']; mw=g.matrix_world
ring=[mw@v.co for v in g.data.vertices if abs((mw@v.co).dot(t)-US)<0.002 and 22.9<(mw@v.co).dot(n)<23.3 and 146.6<(mw@v.co).z<147.0]
print('GUTTER ring',len(ring))
if len(ring)>=3 and not any('gutter' in c for c in caps):
    pts=sorted(set((round(p.dot(n),4),round(p.z,4)) for p in ring))
    cx=sum(p[0] for p in pts)/len(pts); cz=sum(p[1] for p in pts)/len(pts)
    pts.sort(key=lambda p: math.atan2(p[1]-cz,p[0]-cx))
    c=prism('CCOM gable eave end cap S gutter (mu)',pts,US,US+0.006,g.data.materials[0].name); caps.append(c.name)
for x in trimmed: print('TRIM',x)
print('CAPS',caps)
# boxed eave returns
fas=[(22.205,146.53),(23.005,146.53),(23.005,146.985),(22.205,146.985)]
til=[(21.40,146.985),(23.06,146.985),(23.06,147.36-(23.06-22.73)*0.59),(21.40,147.36+(22.73-21.40)*0.59)]
for s,(ua,ub) in (('S',(US-0.004,U0-0.006)),('N',(U1+0.006,UN+0.004))):
    prism('CCOM gable eave return %s fascia+soffit box (mu)'%s,fas,ua,ub,'Eave_fascia_dark_wood')
    prism('CCOM gable eave return %s tile cap (mu)'%s,til,ua,ub,'Roof_tile_or_membrane')
bpy.context.view_layer.update()
# valley flashing
def bvh(objs):
    vs=[];fs=[]
    for o in objs:
        mw=o.matrix_world; b=len(vs); vs+= [mw@v.co for v in o.data.vertices]; fs+=[[b+i for i in p.vertices] for p in o.data.polygons]
    return BVHTree.FromPolygons(vs,fs)
roof=[o for o in bpy.data.objects if o.type=='MESH' and o.name=='School of Communication and Media roof (LiDAR)']+[o for o in col.objects if 'tile cap' in o.name]
R=bvh(roof)
def zhit(T,u,w):
    h=T.ray_cast(P(u,160,w),Vector((0,0,-1)),30); return h[0].z if h[0] else None
mat='ek_coping_metal' if 'ek_coping_metal' in M else 'Gutter_downspout_painted_bronze'
for s,sg in (('S',-1),('N',1)):
    slab=bpy.data.objects['CCOM entrance gable roof tiles %s (mt)'%s]; Sl=bvh([slab])
    line=[]
    w=18.9
    while w<=22.65:
        ue=(2.95 if s=='S' else 10.64); uc=6.75 if s=='S' else 6.85
        k=0; prev=None; N=200; found=None
        for i in range(N+1):
            u=ue+(uc-ue)*i/N; zs=zhit(Sl,u,w); zr=zhit(R,u,w)
            if zs is None or zr is None: continue
            d=zs-zr
            if prev is not None and prev[1]<=0<d: found=u; break
            prev=(u,d)
        if found is not None: line.append((w,found))
        w+=0.2
    print('VALLEY',s,len(line),[(round(a,2),round(b,3)) for a,b in line[:3]],'...',[(round(a,2),round(b,3)) for a,b in line[-2:]])
    if len(line)<3: continue
    vs=[];fs=[]
    for w,u in line:
        for du in (-0.14,0.14):
            zz=[z for z in (zhit(Sl,u+du,w),zhit(R,u+du,w)) if z is not None]
            vs.append(P(u+du,max(zz)+0.012,w))
    for i in range(len(line)-1): fs.append([2*i,2*i+1,2*i+3,2*i+2])
    o=mk('CCOM gable valley flashing %s (mu)'%s,vs,fs,mat); o.visible_shadow=False
print('COUNT',len(bpy.data.objects))
bpy.ops.wm.save_mainfile(); print('SAVED')

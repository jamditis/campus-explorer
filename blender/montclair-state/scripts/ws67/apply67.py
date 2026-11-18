# ws67: College Ave west end (x -252..-214, south of Kasser) sat 1-2.7 m above the 2023 1 m DTM and ended 2.7 m above the
# Red Hawk Deck's College Ave carriageway (north file, appended ws66) with a ~5 m gap. Pull terrain onto the DTM (ws64 GN band method),
# move WS27 carriageway/curbs + LH gutter fill + T_ trees by the same per-xy terrain delta, ramp the WS60 apron west of x -250
# from the DTM edge down to the skirt, and bridge the gap to KY_college_ave_carriageway_asphalt with an asphalt strip.
# Idempotent via custom prop. SAVE=1 saves.
import bpy,bmesh,numpy as np,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE='/workspace/nj-scenes/montclair-state/scripts/ws67/'
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
CW=bpy.data.objects['WS27_CollegeAve_carriageway_2020ortho']
done=CW.get('ws67_done',0)==1
def bvh(o):
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); b=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return b
def rz(b,x,y):
    h=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0]; return h.z if h else None
if not done:
    B0=bvh(T)
    sv=os.environ.get('SAVE'); os.environ['SAVE']='0'
    exec(compile(open(HERE+'terrain67_base.py').read(),'t67','exec'))
    if sv is not None: os.environ['SAVE']=sv
    B1=bvh(T)
    def delta(x,y):
        xx=x
        for _ in range(40):
            a=rz(B0,xx,y); b=rz(B1,xx,y)
            if a is not None and b is not None: return b-a
            if xx>-240: return 0.0
            xx+=0.5
        return 0.0
    moved={}
    names=['WS27_CollegeAve_carriageway_2020ortho','WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED']+[o.name for o in bpy.data.objects if o.name.startswith('LH_college_ave_gutter_asphalt_fill')]
    for n in names:
        o=bpy.data.objects.get(n)
        if not o or o.type!='MESH' or o.data.shape_keys: continue
        if o.data.users>1: o.data=o.data.copy()
        mw=o.matrix_world; mi=mw.inverted(); k=0; mx=0
        for v in o.data.vertices:
            p=mw@v.co
            if -262<p.x<-206 and -90<p.y<-42:
                d=delta(p.x,p.y)
                if abs(d)>0.002: v.co=mi@Vector((p.x,p.y,p.z+d)); k+=1; mx=min(mx,d)
        o.data.update(); moved[n]=(k,round(mx,2))
    # trees / small props by origin (T_ trees and anything small sitting on the old ground)
    for o in bpy.data.objects:
        if o.name in names or o.name.startswith(('Terrain','WS67','Context','WS60')) or o.parent: continue
        p=o.matrix_world.translation
        if not (-258<p.x<-206 and -88<p.y<-44): continue
        if any(c.name.startswith('WS66') for c in o.users_collection): continue
        if o.type=='MESH':
            dims=o.dimensions
            if max(dims.x,dims.y)>15: continue
        a=rz(B0,p.x,p.y)
        if a is None or abs(p.z-a)>1.0: continue
        d=delta(p.x,p.y)
        if abs(d)>0.01: o.location.z+=d; moved[o.name]=(1,round(d,2))
    # apron west of the terrain edge: ramp from the DTM edge (x -250) down to the skirt (x -276), lower only
    D=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy').astype(np.float64)
    for _ in range(2):
        P=np.pad(D,1,mode='edge'); D=sum(P[1+a:P.shape[0]-1+a,1+b:P.shape[1]-1+b] for a in (-1,0,1) for b in (-1,0,1))/9.0
    def dtm_edge(y): return float(D[int(round(y))+250,0])
    A=bpy.data.objects.get('WS60_terrain_edge_apron_LiDAR_to_skirt'); SK=bpy.data.objects.get('Context_skirt_3DEP_ortho_4km')
    if A and SK:
        BS=bvh(SK); mw=A.matrix_world; mi=mw.inverted(); k=0; mx=0
        if A.data.users>1: A.data=A.data.copy()
        bm=bmesh.new(); bm.from_mesh(A.data)
        fs=[f for f in bm.faces if (lambda c:-282<c.x<-244 and -100<c.y<-32)(mw@f.calc_center_median())]
        es=list({e for f in fs for e in f.edges}); print('A67 apron faces',len(fs),'verts before',len(bm.verts))
        if es: bmesh.ops.subdivide_edges(bm,edges=es,cuts=int(os.environ.get('ACUTS','8')),use_grid_fill=True)
        bm.to_mesh(A.data); bm.free(); A.data.update(); print('A67 apron verts after',len(A.data.vertices))
        for v in A.data.vertices:
            p=mw@v.co
            if -278<p.x<-246 and -96<p.y<-36:
                s=rz(BS,-276,p.y) or p.z
                t=min(max((-249-p.x)/27.0,0),1); t=t*t*(3-2*t)
                zt=(1-t)*dtm_edge(p.y)+t*(s-0.05)
                wy=1.0
                if p.y>-46: wy=max(0,(-36-p.y)/10)
                if p.y<-88: wy=max(0,(p.y+96)/8)
                wx=1.0 if p.x<-252 else max(0,(-246-p.x)/6)
                nz=p.z+(min(zt,p.z)-p.z)*wy*wx
                if nz<p.z-0.002: v.co=mi@Vector((p.x,p.y,nz)); k+=1; mx=min(mx,nz-p.z)
        A.data.update(); moved['apron']=(k,round(mx,2))
    # bridge strip WS27 west end -> KY carriageway east end
    KY=[o for o in bpy.data.objects if o.name.startswith('KY_college_ave_carriageway_asphalt')]
    if KY:
        ky=KY[0]
        def edge(o,cond):
            pts=[o.matrix_world@v.co for v in o.data.vertices]; pts=[p for p in pts if cond(p)]; return pts
        e1=edge(CW,lambda p:p.x<-249.0); e2=edge(ky,lambda p:p.x>-255.6 and p.y<-50)
        print('B67 edges',len(e1),len(e2))
        if e1 and e2:
            y1a,y1b=min(p.y for p in e1),max(p.y for p in e1); y2a,y2b=min(p.y for p in e2),max(p.y for p in e2)
            x1=max(min(p.x for p in e1)+0.6,-249.6); x2=min(max(p.x for p in e2)-0.6,-255.0)
            def zn(pts,y): return sorted(pts,key=lambda p:abs(p.y-y))[0].z
            NY=9; verts=[]; faces=[]
            for i in range(NY):
                f=i/(NY-1)
                ya=y1a+f*(y1b-y1a); yb=y2a+f*(y2b-y2a)
                za=zn(e1,ya); zb=zn(e2,yb)
                for j,(x,y,z) in enumerate([(x1,ya,za),((x1+x2)/2,(ya+yb)/2,(za+zb)/2),(x2,yb,zb)]): verts.append((x,y,z+0.012))
            for i in range(NY-1):
                for j in range(2): faces.append((i*3+j,i*3+j+1,(i+1)*3+j+1,(i+1)*3+j))
            me=bpy.data.meshes.new('WS67_CollegeAve_gap_asphalt'); me.from_pydata(verts,[],faces); me.update()
            for mat in CW.data.materials: me.materials.append(mat)
            ob=bpy.data.objects.new('WS67_CollegeAve_gap_asphalt (bridges WS27 to north-file KY carriageway)',me)
            CW.users_collection[0].objects.link(ob)
            for pl in me.polygons: pl.use_smooth=False
            print('B67 bridge x',round(x2,1),round(x1,1),'z',round(zn(e2,(y2a+y2b)/2),2),round(zn(e1,(y1a+y1b)/2),2))
    CW['ws67_done']=1
    for k,v in moved.items(): print('M67',k[:60],v)
# verify
A=bpy.data.objects.get('WS60_terrain_edge_apron_LiDAR_to_skirt')
B2=bvh(T); D0=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
CWB=bvh(CW)
for x in (-262,-256,-252,-249,-244,-236,-228,-220,-212,-206):
    for y in (-58,-62,-70):
        t=rz(B2,x,y) if x>-250 else (rz(bvh(A),x,y) if A else None); r=rz(CWB,x,y)
        print('V67 x%d y%d dtm %.2f terr %s road %s'%(x,y,D0[y+250,max(x,-250)+250],None if t is None else round(t,2),None if r is None else round(r,2)))
if os.environ.get('SAVE')=='1' and not done: bpy.ops.wm.save_mainfile(); print('A67 saved')

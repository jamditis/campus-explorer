# ws89: (A) College Ave <-> accessible-lot strip -> curbed dark-mulch median (BVH rewrite of ws88 median88.py; Joe catwalk 9:19 AM)
#       (B) curved concentric steps just OUTSIDE the ws88 arcade arc (Joe 9:20/9:56/9:57 AM refs), seated on COLE_plaza_deck_bs
#       (C) WS35 top step lip slit probe + filler
import bpy,bmesh,math,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get(); OB=bpy.data.objects
LITE=os.environ.get('LITE')=='1'
def bvh_of(o,keep_mats=False):
    bpy.context.view_layer.update()
    if not o.modifiers and o.type=='MESH':
        me=o.data; P=[o.matrix_world@v.co for v in me.vertices]; F=[tuple(p.vertices) for p in me.polygons]
        if not F: return None,None
        mats=None
        if keep_mats:
            ms=[m.name.lower() if m else '' for m in me.materials]; mats=[ms[p.material_index] if p.material_index<len(ms) else '' for p in me.polygons]
        return BVHTree.FromPolygons(P,F),mats
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=e.to_mesh()
    if me is None or not me.polygons: e.to_mesh_clear(); return None,None
    P=[e.matrix_world@v.co for v in me.vertices]; F=[tuple(p.vertices) for p in me.polygons]
    mats=None
    if keep_mats:
        ms=[m.name.lower() if m else '' for m in me.materials]; mats=[ms[p.material_index] if p.material_index<len(ms) else '' for p in me.polygons]
    b=BVHTree.FromPolygons(P,F); e.to_mesh_clear()
    if os.environ.get('DBG'): print('DBG',o.name[:20],len(P),P[0],b.ray_cast(Vector((P[0].x+0.01,P[0].y+0.01,160)),Vector((0,0,-1)))[0])
    return b,mats
def wbox(o):
    c=[o.matrix_world@Vector(v) for v in o.bound_box]; return min(v.x for v in c),max(v.x for v in c),min(v.y for v in c),max(v.y for v in c)
def hit(b,x,y,z0=160):
    r=b.ray_cast(Vector((x,y,z0)),Vector((0,0,-1))); return r
def link(ob,like):
    (OB[like].users_collection[0] if like in OB else bpy.context.scene.collection).objects.link(ob)
def mat(*names):
    for n in names:
        if n in bpy.data.materials: return bpy.data.materials[n]
    return None
DO=os.environ.get('DO','ABC')
# ---------------- A: median ----------------
if 'A' in DO and 'Terrain_LiDAR_DTM_1m' in OB:
    X0,X1,Y0,Y1,S=-262.0,-222.0,-74.0,-58.0,0.5
    T=OB['Terrain_LiDAR_DTM_1m']; TB,TM=bvh_of(T,True)
    others=[]
    for o in OB:
        if o.type!='MESH' or o is T or o.hide_render or o.name.startswith(('WS89_','WS88_CollegeAve_lot_median')) or 'DTM_target' in o.name or 'curtain' in o.name.lower() or 'skirt' in o.name.lower(): continue
        try: x0,x1,y0,y1=wbox(o)
        except Exception: continue
        if x1<X0 or x0>X1 or y1<Y0 or y0>Y1: continue
        if (x1-x0)>400: continue
        b,_=bvh_of(o)
        if b: others.append((o.name,b))
    print('A89 overlap objects',len(others),[n[:30] for n,_ in others][:40])
    nx=int((X1-X0)/S); ny=int((Y1-Y0)/S); grid={}; rows=[]
    for j in range(ny):
        row=''
        for i in range(nx):
            x=X0+(i+0.5)*S; y=Y0+(j+0.5)*S; h=hit(TB,x,y)
            if h[0] is None: row+='.'; continue
            zt=h[0].z; m=TM[h[2]]
            occ=None
            for n,b in others:
                q=hit(b,x,y)
                if q[0] is not None and q[0].z>zt-0.25: occ=n; break
            if occ: row+='a' if ('road' in occ.lower() or 'lot' in occ.lower() or 'college' in occ.lower()) else ('c' if 'curb' in occ.lower() else 'o'); continue
            if any(k in m for k in ('lawn','grass','turf')): row+='L'; grid[(i,j)]=zt
            else: row+='t'
        rows.append(row)
    for r in reversed(rows): print('A89M',r)
    YLO,YHI=float(os.environ.get('YLO','-71')),float(os.environ.get('YHI','-61'))
    # per-column lawn run in the band (largest contiguous run)
    cols={}
    for i in range(nx):
        js=[j for j in range(ny) if (i,j) in grid and YLO<Y0+(j+0.5)*S<YHI]
        if not js: continue
        runs=[];cur=[js[0]]
        for j in js[1:]:
            if j==cur[-1]+1: cur.append(j)
            else: runs.append(cur); cur=[j]
        runs.append(cur); best=max(runs,key=len)
        if len(best)>=2: cols[i]=(Y0+best[0]*S, Y0+(best[-1]+1)*S)
    ks=sorted(cols); print('A89 median columns',len(ks), 'x',ks and (X0+ks[0]*S, X0+(ks[-1]+1)*S))
    # longest contiguous column run
    runs=[];cur=[]
    for i in ks:
        if cur and i!=cur[-1]+1: runs.append(cur); cur=[]
        cur.append(i)
    if cur: runs.append(cur)
    if runs and int(os.environ.get('BUILD','1')):
        run=max(runs,key=len); print('A89 run cols',len(run))
        xs=[X0+i*S for i in run]+[X0+(run[-1]+1)*S]
        lo=[cols[i][0] for i in run]; hi=[cols[i][1] for i in run]
        lo=lo+[lo[-1]]; hi=hi+[hi[-1]]; CW=0.15; CH_=0.10
        def sm(a,n=3):
            out=[]
            for k in range(len(a)):
                w=a[max(0,k-n):k+n+1]; out.append(sum(w)/len(w))
            return out
        lo=sm(sm(lo,6),6); hi=sm(sm(hi,6),6)
        # curb tops: smooth along x so the curb reads as a clean straight line (never below terrain+0.05)
        def tz0(x,y):
            h=hit(TB,x,y); return h[0].z if h[0] is not None else 126
        TOP={}
        for side in (0,1):
            raw=[]; floor=[]
            for k,x in enumerate(xs):
                ya,yb=((lo[k],lo[k]+CW) if side==0 else (hi[k]-CW,hi[k])); m=max(tz0(x,ya),tz0(x,yb)); raw.append(m+CH_); floor.append(m+0.05)
            sm_=sm(sm(raw,5),5); TOP[side]=[max(a,b) for a,b in zip(sm_,floor)]
        def tz(x,y):
            h=hit(TB,x,y); return h[0].z if h[0] is not None else None
        bmM=bmesh.new(); bmC=bmesh.new()
        # mulch: inset CW from each side, subdivided across 4 strips
        NS=4; prev=None; prevc=None
        for k,x in enumerate(xs):
            a=lo[k]+CW; b=hi[k]-CW
            if b-a<0.3: prev=None; prevc=None; continue
            row=[]
            for s in range(NS+1):
                y=a+(b-a)*s/NS; z=tz(x,y) or 126; row.append(bmM.verts.new((x,y,z+0.04)))
            if prev:
                for s in range(NS): bmM.faces.new((prev[s],row[s],row[s+1],prev[s+1]))
            prev=row
            # curbs: two strips (lo side, hi side), top = terrain max across strip + CH, skirt to terrain-0.05
            crow=[]
            for side,(ya,yb) in enumerate(((lo[k],lo[k]+CW),(hi[k]-CW,hi[k]))):
                za=tz(x,ya) or 126; zb=tz(x,yb) or 126; top=TOP[side][k]
                crow+= [bmC.verts.new((x,ya,min(za,zb)-0.05)),bmC.verts.new((x,ya,top)),bmC.verts.new((x,yb,top)),bmC.verts.new((x,yb,min(za,zb)-0.05))]
            if prevc:
                for base in (0,4):
                    for s in range(3): bmC.faces.new((prevc[base+s],crow[base+s],crow[base+s+1],prevc[base+s+1]))
            prevc=crow
        for o in [o for o in OB if o.name.startswith(('WS89_CollegeAve_lot_median','WS88_CollegeAve_lot_median'))]: OB.remove(o)
        for bm_,nm,mt in ((bmM,'WS89_CollegeAve_lot_median_MULCH_JOEcatwalk20261112_BVH_UNVERIFIED_edges',mat('WS87_median_mulch_dark_JOEphoto','WS3_Mulch_bark_dark_brown')),
                          (bmC,'WS89_CollegeAve_lot_median_CURB_concrete_UNVERIFIED',mat('Kasser_apron_concrete_cm','WS35_concrete_steps'))):
            me=bpy.data.meshes.new(nm); bm_.to_mesh(me); bm_.free()
            if mt: me.materials.append(mt)
            for p in me.polygons: p.use_smooth=False
            ob=bpy.data.objects.new(nm,me); link(ob,'WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020')
            print('A89 built',nm,'faces',len(me.polygons))
if 'M' in DO:
    m=bpy.data.materials.get('WS87_median_mulch_dark_JOEphoto')
    if m and m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type=='BSDF_PRINCIPLED' and not n.inputs['Base Color'].is_linked:
                c=n.inputs['Base Color'].default_value; print('A89 mulch col before',tuple(round(v,3) for v in c)); n.inputs['Base Color'].default_value=(c[0]*0.6,c[1]*0.6,c[2]*0.6,1)
            elif n.type in ('RGB',): c=n.outputs[0].default_value; print('A89 mulch rgb before',tuple(round(v,3) for v in c)); n.outputs[0].default_value=(c[0]*0.6,c[1]*0.6,c[2]*0.6,1)
            elif n.type=='VALTORGB':
                for e in n.color_ramp.elements: c=e.color; print('A89 mulch ramp before',tuple(round(v,3) for v in c)); e.color=(c[0]*0.6,c[1]*0.6,c[2]*0.6,c[3])
# ---------------- B: curved steps ----------------
if 'B' in DO and 'COLE_plaza_deck_bs' in OB:
    D=OB['COLE_plaza_deck_bs']; DB,_=bvh_of(D)
    C=Vector((-166.66,-79.9)); N=int(os.environ.get('NST','3')); TR=float(os.environ.get('TR','0.70')); R0=17.45
    A0,A1=float(os.environ.get('AA','161')),float(os.environ.get('AB','246'))
    rs=[R0+TR*k for k in range(N+1)]
    def dz(r,a):
        q=C+Vector((math.cos(a),math.sin(a)))*r; h=hit(DB,q.x,q.y); return h[0].z if h[0] is not None else None
    bm=bmesh.new(); profs=[]; na=int((A1-A0)/0.75)+1; maxrise=0; minr=9
    lastz=None; ZK=[]
    for ia in range(na):
        a=math.radians(A0+(A1-A0)*ia/(na-1))
        zk=[]
        for k in range(N):
            samp=[dz(rs[k]+TR*t/4,a) for t in range(5)]; samp=[s for s in samp if s is not None]
            zk.append((max(samp)+0.015) if samp else (zk[-1]-0.1 if zk else 129.5))
        # target: top tread = inner terrace level (deck just inside the wall), equal risers down to the outer deck; never below the deck
        zin=dz(R0-0.35,a); zo=dz(rs[N]+0.1,a)
        if zin is not None and zo is not None:
            h=(zin+0.02-zo)/N
            zk=[max(zk[k],zin+0.02-h*k) for k in range(N)]
        for k in range(N-1,0,-1): zk[k-1]=max(zk[k-1],zk[k])
        zb0=(dz(rs[0],a) or zk[0])-0.06; zbN=(dz(rs[N],a) or zk[-1]-0.15)-0.06
        ZK.append((a,zk,zb0,zbN,[max([d for d in [dz(rs[k]+TR*t/4,a) for t in range(5)] if d is not None] or [zk[k]-0.015])+0.015 for k in range(N)]))
    SMW=int(os.environ.get('SMW','6')); ZS=[]
    for ia in range(na):
        w=ZK[max(0,ia-SMW):ia+SMW+1]
        zk=[sum(r[1][k] for r in w)/len(w) for k in range(N)]
        zk=[max(zk[k],ZK[ia][4][k]) for k in range(N)]
        for k in range(N-1,0,-1): zk[k-1]=max(zk[k-1],zk[k]+0.06)
        ZS.append(zk)
    for ia in range(na):
        a,_,zb0,zbN,_=ZK[ia]; zk=ZS[ia]
        pts=[(rs[0],zb0),(rs[0],zk[0])]
        for k in range(N):
            pts.append((rs[k+1],zk[k]))
            if k<N-1: pts.append((rs[k+1],zk[k+1]))
            maxrise=max(maxrise,zk[k]-(zk[k+1] if k<N-1 else zbN+0.06))
        pts.append((rs[N],zbN))
        dirv=Vector((math.cos(a),math.sin(a)))
        profs.append([bm.verts.new((C.x+dirv.x*r,C.y+dirv.y*r,z)) for r,z in pts])
    for p0,p1 in zip(profs,profs[1:]):
        for s in range(len(p0)-1): bm.faces.new((p0[s],p1[s],p1[s+1],p0[s+1]))
        bm.faces.new((p0[-1],p1[-1],p1[0],p0[0]))
    bm.faces.new(list(reversed(profs[0]))); bm.faces.new(profs[-1])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    for o in [o for o in OB if o.name.startswith('WS89_Cole_curved_steps')]: OB.remove(o)
    nm='WS89_Cole_curved_steps_concentric_ws88arc_JOE20261112_UNVERIFIED_count'
    me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free()
    mt=mat('WS35_concrete_steps','Kasser_apron_concrete_cm');  mt and me.materials.append(mt)
    ob=bpy.data.objects.new(nm,me); link(ob,'COLE_plaza_deck_bs')
    print('A89 steps built faces',len(me.polygons),'N',N,'r',R0,rs[-1],'ang',A0,A1,'max rise',round(maxrise,3))
    # objects crossing the step band
    for o in OB:
        if o.type!='MESH' or o.hide_render or o is ob or o is D: continue
        try: x0,x1,y0,y1=wbox(o)
        except Exception: continue
        if x1<-190 or x0>-166 or y1<-100 or y0>-60 or (x1-x0)>60: continue
        b,_=bvh_of(o); cnt=0
        if not b: continue
        for ia in range(0,na,4):
            a=math.radians(A0+(A1-A0)*ia/(na-1))
            for r in (rs[0]+0.2,rs[N//2]+0.2,rs[N]-0.2):
                q=C+Vector((math.cos(a),math.sin(a)))*r; h=hit(b,q.x,q.y)
                if h[0] is not None and h[0].z>128.0: cnt+=1
        if cnt: print('A89 step band overlaps',o.name[:60],cnt)
# ---------------- C: WS35 top lip slit ----------------
if 'C' in DO and 'WS35_Kasser_terrace_steps_concrete_5risers_UNVERIFIED' in OB:
    names=['WS35_Kasser_terrace_steps_concrete_5risers_UNVERIFIED','WS40_Cole_deck_cut_fascia_concrete_UNVERIFIED','COLE_plaza_deck_bs','COLE_plaza_edge_bs','Terrain_LiDAR_DTM_1m','WS35_Kasser_steps_cheek_walls_UNVERIFIED']
    B={n:bvh_of(OB[n])[0] for n in names if n in OB}
    print('C89 bvhs',{k:(v.ray_cast(Vector((-199.5,-92,160)),Vector((0,0,-1)))[0] if v else None) for k,v in B.items()}, hit)
    gaps=[]
    for y in (-95.0,-92.0,-89.0):
        prof=[]
        for ix in range(0,110):
            x=-190.5+ix*0.02; best=None
            for n,b in B.items():
                if not b: continue
                h=hit(b,x,y)
                if h[0] is not None and (best is None or h[0].z>best[1]): best=(n[:6],h[0].z)
            prof.append((round(x,2),best))
        s=' '.join(f"{p[0]}:{p[1][0]}{p[1][1]:.2f}" for p in prof[::2] if p[1])
        print('C89',y,s)

# ---------------- D: WS35 top-lip riser filler (closes the dark slit between top tread x=-190.0 and the deck edge) ----------------
if 'D' in DO:
    St=OB['WS35_Kasser_terrace_steps_concrete_5risers_UNVERIFIED']; SB,_=bvh_of(St); DB2,_=bvh_of(OB['COLE_plaza_deck_bs'])
    P=[St.matrix_world@v.co for v in St.data.vertices]; y0=min(p.y for p in P)+0.02; y1=max(p.y for p in P)-0.02; xe=max(p.x for p in P)
    bm=bmesh.new(); prev=None; n=0; gmax=0
    ny=int((y1-y0)/0.25)+1
    for j in range(ny):
        y=y0+(y1-y0)*j/(ny-1)
        hs=hit(SB,xe-0.05,y); hd=hit(DB2,xe+0.10,y)
        if hs[0] is None or hd[0] is None: prev=None; continue
        zt=hs[0].z; zd=hd[0].z+0.002; gmax=max(gmax,zd-zt)
        row=[bm.verts.new((xe-0.06,y,zt-0.02)),bm.verts.new((xe-0.06,y,zd)),bm.verts.new((xe+0.12,y,zd)),bm.verts.new((xe+0.12,y,zt-0.02))]
        if prev:
            for s_ in range(3): bm.faces.new((prev[s_],row[s_],row[s_+1],prev[s_+1])); n+=1
        prev=row
    for o in [o for o in OB if o.name.startswith('WS89_Kasser_steps_top_lip')]: OB.remove(o)
    nm='WS89_Kasser_steps_top_lip_riser_filler_concrete'
    me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free(); me.materials.append(St.data.materials[0])
    ob=bpy.data.objects.new(nm,me); link(ob,St.name); print('A89 lip filler faces',n,'xe',round(xe,2),'max gap',round(gmax,3))
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('A89 saved')

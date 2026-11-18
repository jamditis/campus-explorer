# pz (Nov 2 2026): Dickson west-wing parapet touch-ups on top of py. New objects only -> REVERT=1 deletes them (exact py state).
#  A) PZ_Dickson_wing_infill_seam_bridges_UNVERIFIED: brick quads closing the 3-5 cm gaps between neighbouring PX infill pieces
#     (open vertical edge pairs <0.12 m apart; the two hairline seams near the NW step corner + 3 on the south face), facade UV.
#  B) PZ_Dickson_wing_coping_joints_corners_UNVERIFIED: corner cover pieces at every coping chain corner (>25 deg turn; hides the
#     tiny dark notch at the NW step corner) + 6 cm joint cover straps about every 3 m (metal coping is laid in ~3 m lengths).
#  C) PZ_Dickson_wing_coping_drip_stain_UNVERIFIED: faint streaky run-off band (0.28 m) on the brick just below the coping drip.
# ALL UNVERIFIED (no roofline photo).
import bpy, bmesh, os, collections, math, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
REV=os.environ.get('REVERT')=='1'
ZB=152.92; CT=0.10; OV=0.04; TH=0.30; MW=1.9; ZM=152.50
NAMES=['PZ_Dickson_wing_infill_seam_bridges_UNVERIFIED','PZ_Dickson_wing_coping_joints_corners_UNVERIFIED','PZ_Dickson_wing_coping_drip_stain_UNVERIFIED']
MSN='PZ_coping_drip_stain_UNVERIFIED'
for n in NAMES:
    if n in bpy.data.objects:
        o=bpy.data.objects[n]; m=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m); print('REVERTED',n)
if REV and MSN in bpy.data.materials: bpy.data.materials.remove(bpy.data.materials[MSN]); print('REVERTED',MSN)
def inwing(p): return p.x<-157.5 and 77.0<p.y<160.5
if not REV:
    roof=bpy.data.objects['Dickson Hall roof (LiDAR)']
    bm0=bmesh.new(); bm0.from_mesh(roof.data); bm0.transform(roof.matrix_world); bvh=BVHTree.FromBMesh(bm0)
    def inside(p):
        h=bvh.ray_cast(Vector((p.x,p.y,170.0)),Vector((0,0,-1)),40.0); return h[0] is not None and h[0].z>150.0
    def affine(WV,me,uv,p):
        L=list(p.loop_indices); P=[WV[me.loops[l].vertex_index] for l in L]; U=[uv[l].uv.copy() for l in L]; best=None
        for i in range(len(L)):
            for j in range(i+1,len(L)):
                for k in range(j+1,len(L)):
                    a=U[j]-U[i]; b=U[k]-U[i]; det=a.x*b.y-a.y*b.x
                    if best is None or abs(det)>abs(best[0]): best=(det,i,j,k)
        det,i,j,k=best
        if abs(det)<1e-5: return None
        a=U[j]-U[i]; b=U[k]-U[i]; A=P[j]-P[i]; B=P[k]-P[i]
        return P[i],U[i],(A*b.y-B*a.y)/det,(B*a.x-A*b.x)/det
    def uvof(F,c):
        P0,U0,a,b=F; d=c-P0; aa=a.dot(a); ab=a.dot(b); bb=b.dot(b); da=d.dot(a); db_=d.dot(b); det=aa*bb-ab*ab
        return (U0.x+(da*bb-db_*ab)/det, U0.y+(db_*aa-da*ab)/det)
    SEG=[]
    for on,zmin in (('PX_Dickson_wing_parapet_infill_UNVERIFIED',151.25),('Dickson Hall walls',151.25)):
        o=bpy.data.objects[on]; me=o.data; mw=o.matrix_world; uv=me.uv_layers['facade'].data
        WV=[mw@v.co for v in me.vertices]
        kd=KDTree(len(WV))
        for i,c in enumerate(WV): kd.insert(Vector((c.x,c.y,0)),i)
        kd.balance()
        ec=collections.defaultdict(list)
        for p in me.polygons:
            for k in p.edge_keys: ec[k].append(p.index)
        for k,fl in ec.items():
            if len(fl)!=1: continue
            a=WV[k[0]]; b=WV[k[1]]; m=(a+b)/2
            if (a.xy-b.xy).length<0.05 or min(a.z,b.z)<zmin or max(a.z,b.z)>=ZB or not inwing(m): continue
            p=me.polygons[fl[0]]
            if (mw@p.center).z>=m.z: continue
            if any(WV[i].z>max(a.z,b.z)+0.25 for (co,i,d) in kd.find_range(Vector((m.x,m.y,0)),0.9)): continue
            F=affine(WV,me,uv,p)
            if F is None: continue
            t=(b-a).xy.normalized(); nrm=Vector((-t.y,t.x))
            inn=None
            for dd in (1.0,2.0,0.6,3.5,5.0):
                i1=inside(m.xy+nrm*dd); i2=inside(m.xy-nrm*dd)
                if i1!=i2: inn=nrm if i1 else -nrm; break
            if inn is None:
                cdir=(Vector((-170.0,118.0))-m.xy); inn=nrm if cdir.dot(nrm)>0 else -nrm; print('FALLBACKSIDE %.1f %.1f'%(m.x,m.y))
            if inn is None: print('NOSIDE %.1f %.1f'%(m.x,m.y)); continue
            SEG.append((a,b,F,Vector((inn.x,inn.y,0))))
    print('PY_SEG',len(SEG))
    def key(v): return (round(v.x,2),round(v.y,2))
    inc=collections.defaultdict(list); P2={}
    for a,b,F,inn in SEG:
        for v in (a,b): inc[key(v)].append(inn); P2[key(v)]=Vector((v.x,v.y,0))
    # merge near-coincident endpoints (<0.12 m) into one key
    keys=list(P2); kd2=KDTree(len(keys))
    for i,k in enumerate(keys): kd2.insert(P2[k],i)
    kd2.balance(); rep={}
    for i,k in enumerate(keys):
        if k in rep: continue
        for (co,j,d) in kd2.find_range(P2[k],0.12):
            if keys[j] not in rep: rep[keys[j]]=k
    INN={}; INC=collections.defaultdict(list)
    for k,l in inc.items(): INC[rep[k]]+=l
    for k,l in INC.items():
        s_=Vector((0,0,0))
        for n in l: s_+=n
        if s_.length<1e-6: s_=l[0].copy()
        s_.normalize(); c=max(0.5,min(n.dot(s_) for n in l)); INN[k]=s_/c
    def off(v,d): k=rep[key(v)]; return P2[k]+INN[k]*d
    mats=bpy.data.materials; coll=bpy.data.objects['Dickson Hall walls'].users_collection[0]
    def mk(name,bm,mat,note,shadow=True):
        m2=bpy.data.meshes.new(name); bm.to_mesh(m2); bm.free()
        for mm in mat: m2.materials.append(mats[mm])
        o=bpy.data.objects.new(name,m2); o['source_note']=note; o.visible_shadow=shadow; coll.objects.link(o); return o
    # ---- A) seam bridges between PX infill pieces
    o=bpy.data.objects['PX_Dickson_wing_parapet_infill_UNVERIFIED']; me=o.data; mw=o.matrix_world; uv=me.uv_layers['facade'].data
    WV=[mw@v.co for v in me.vertices]; ec=collections.defaultdict(list)
    for p in me.polygons:
        for k in p.edge_keys: ec[k].append(p.index)
    VE=[]
    for k,fl in ec.items():
        if len(fl)!=1: continue
        a=WV[k[0]]; b=WV[k[1]]
        if (a.xy-b.xy).length<0.02 and abs(a.z-b.z)>0.2 and inwing((a+b)/2):
            lo,hi=sorted((a,b),key=lambda v:v.z); VE.append((lo,hi,fl[0]))
    bm=bmesh.new(); ul=bm.loops.layers.uv.new('facade'); used=set(); nbr=0
    for i,(lo,hi,f) in enumerate(VE):
        if i in used: continue
        best=None
        for j,(lo2,hi2,f2) in enumerate(VE):
            if j==i or j in used or f2==f: continue
            d=(lo2.xy-lo.xy).length; z0=max(lo.z,lo2.z); z1=min(hi.z,hi2.z)
            if 0.005<d<0.12 and z1-z0>0.2 and (best is None or d<best[0]): best=(d,j,z0,z1)
        if best is None: continue
        d,j,z0,z1=best; lo2,hi2,f2=VE[j]; used.add(i); used.add(j)
        p=me.polygons[f]; nw=(mw.to_3x3()@p.normal).normalized()
        q=[Vector((lo.x,lo.y,z0)),Vector((lo2.x,lo2.y,z0)),Vector((lo2.x,lo2.y,z1)),Vector((lo.x,lo.y,z1))]
        if (q[1]-q[0]).cross(q[3]-q[0]).dot(nw)<0: q=[q[1],q[0],q[3],q[2]]
        F=affine(WV,me,uv,p); vs=[bm.verts.new(x) for x in q]; nf=bm.faces.new(vs)
        if F:
            for lp in nf.loops: lp[ul].uv=uvof(F,lp.vert.co)
        nbr+=1; print('PZ_BRIDGE %.2f %.2f -> %.2f %.2f z%.2f-%.2f gap %.3f'%(lo.x,lo.y,lo2.x,lo2.y,z0,z1,d))
    mk(NAMES[0],bm,['PE_Dickson_brick_buff_no_red_spandrel_UNVERIFIED'],'UNVERIFIED (pz, Nov 2 2026): closes 3-5 cm gaps between LiDAR-derived PX infill pieces (hairline seams)')
    # ---- B) coping corner covers + joint straps
    adj=collections.defaultdict(list); SG=[]
    for a,b,F,inn in SEG:
        ka=rep[key(a)]; kb=rep[key(b)]
        if ka==kb: continue
        adj[ka].append((kb,inn)); adj[kb].append((ka,inn)); SG.append((ka,kb,inn))
    bm=bmesh.new()
    def box(c,t,n,u0,u1,w0,w1,z0,z1):
        P=[c+t*u+n*w for u in (u0,u1) for w in (w0,w1)]
        vs=[bm.verts.new((p.x,p.y,z)) for z in (z0,z1) for p in P]
        for fi in ((0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)):
            try: bm.faces.new([vs[i] for i in fi])
            except ValueError: pass
    CORN=set(); nco=0
    ENDS=[k for k,l in adj.items() if len(l)==1]
    for k in ENDS: print('PZ_END %.3f %.3f'%(P2[k].x,P2[k].y), 'inn %.2f %.2f'%(adj[k][0][1].x,adj[k][0][1].y))
    for k,l in adj.items():
        if len(l)<2: continue
        ang=max(math.degrees(l[i][1].angle(l[j][1])) for i in range(len(l)) for j in range(i+1,len(l)))
        if ang<25: continue
        CORN.add(k); c=P2[k]
        for jj,(nk,inn) in enumerate(l):
            t=(P2[nk]-c); t.z=0
            if t.length<1e-4: continue
            t.normalize(); others=[x[1] for x in l if x[1] is not inn]
            conv=all((-t).dot(o2)<0.2 for o2 in others)
            ext=(OV+0.012) if conv else (TH+0.05)
            box(c,t,inn,-ext-0.003*jj,0.50,-(OV+0.010)+0.003*jj,TH+0.075-0.003*jj,ZB-0.045+0.003*jj,ZB+CT+0.009+0.004*jj); nco+=1  # staggered: no coplanar overlap (black in Cycles)
    nj=0; SP=3.0
    for ka,kb,inn in SG:
        a0=P2[ka]; b0=P2[kb]; t=b0-a0; L=t.length
        if L<0.2: continue
        t/=L; ax=0 if abs(t.x)>abs(t.y) else 1
        sa=a0[ax]; sb=b0[ax]; lo_,hi_=sorted((sa,sb))
        m=math.ceil(lo_/SP)*SP
        while m<hi_:
            s=(m-sa)/(sb-sa)*L; c=a0+t*s
            if all((c-P2[k2]).length>0.45 for k2 in CORN):
                box(c,t,inn,-0.03,0.03,-(OV+0.007),TH+0.048,ZB-0.042,ZB+CT+0.006); nj+=1
            m+=SP
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    mk(NAMES[1],bm,['ek_coping_metal'],'UNVERIFIED (pz): coping corner cover pieces + 6 cm joint straps every ~3 m (world grid); generic, no photo')
    print('PZ_COPING corners',len(CORN),'corner pieces',nco,'joints',nj)
    # ---- C) drip-stain band under the coping drip (shadows off)
    src=mats['PW_sill_drip_stain_UNVERIFIED']; ms=mats.get(MSN)
    if ms is None:
        ms=src.copy(); ms.name=MSN
        for nd in ms.node_tree.nodes:
            if nd.type=='MAP_RANGE': nd.inputs['From Min'].default_value=-1.0; nd.inputs['From Max'].default_value=-0.5
            if nd.type=='MATH' and nd.operation=='MULTIPLY' and abs(nd.inputs[1].default_value-0.6)<1e-6 and not nd.inputs[1].is_linked: nd.inputs[1].default_value=0.90
            if nd.type=='MATH' and nd.operation=='MULTIPLY' and abs(nd.inputs[1].default_value-22.0)<1e-6: nd.inputs[1].default_value=9.0
            if nd.type=='MATH' and nd.operation=='POWER': nd.inputs[1].default_value=2.2
    bm=bmesh.new(); ul=bm.loops.layers.uv.new('UVMap'); ns=0
    for a,b,F,inn in SEG:
        a0=Vector((a.x,a.y,0))-inn*0.012; b0=Vector((b.x,b.y,0))-inn*0.012; t=(b0-a0)
        if t.length<0.05: continue
        ax=0 if abs(t.x)>abs(t.y) else 1
        q=[(a0,ZB-0.32,0),(b0,ZB-0.32,0),(b0,ZB-0.038,1),(a0,ZB-0.038,1)]
        vs=[bm.verts.new((p.x,p.y,z)) for p,z,v in q]
        if (vs[1].co-vs[0].co).cross(vs[3].co-vs[0].co).dot(inn)>0: vs=[vs[1],vs[0],vs[3],vs[2]]
        f=bm.faces.new(vs)
        for lp in f.loops:
            lp[ul].uv=(lp.vert.co[ax], 1.0 if lp.vert.co.z>ZB-0.1 else 0.0)
        ns+=1
    mk(NAMES[2],bm,[MSN],'UNVERIFIED (pz): faint run-off staining 0.28 m under the coping drip; invented',shadow=False)
    print('PZ_STAIN',ns)
    bm0.free()

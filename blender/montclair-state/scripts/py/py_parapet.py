# py (Nov 2 2026): Dickson west-wing parapet finished. Finding: the wing's LiDAR roof membrane sits FLAT at 152.51 m with
# the el coping strips at 152.47-152.56 set 0.4-1.3 m inside the wall line, so px's 151.30 brick top left a band of the
# roof's stucco skirt + a dark coping line above it (the 'steps' at the corners). py raises the brick from every
# remaining wing top (px infill tops at 151.30 + the wall tops at 151.3/151.6) to a LEVEL parapet top ZB above the roof,
# adds a parapet back face, a roof-membrane strip that closes the gap to the LiDAR roof edge, and a metal coping cap
# (0.04 m drip overhang outside). New objects only -> REVERT=1 deletes them (exact px state). ALL UNVERIFIED.
import bpy, bmesh, os, collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
REV=os.environ.get('REVERT')=='1'
ZB=float(os.environ.get('ZB','152.92')); CT=0.10; OV=0.04; TH=0.30; MW=1.9; ZM=152.50
NAMES=['PY_Dickson_wing_parapet_raise_UNVERIFIED','PY_Dickson_wing_parapet_back_roofstrip_UNVERIFIED','PY_Dickson_wing_parapet_coping_UNVERIFIED']
for n in NAMES:
    if n in bpy.data.objects:
        o=bpy.data.objects[n]; m=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m); print('REVERTED',n)
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
    mats=bpy.data.materials
    def mk(name,bm,mat,note):
        bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002)
        m2=bpy.data.meshes.new(name); bm.to_mesh(m2); bm.free()
        for mm in mat: m2.materials.append(mats[mm])
        o=bpy.data.objects.new(name,m2); o['source_note']=note
        bpy.data.objects['Dickson Hall walls'].users_collection[0].objects.link(o); return o
    # 1 brick raise (outer face), facing outward
    bm=bmesh.new(); ul=bm.loops.layers.uv.new('facade')
    for a,b,F,inn in SEG:
        a2=Vector((a.x,a.y,ZB)); b2=Vector((b.x,b.y,ZB)); vs=[bm.verts.new(x) for x in (a,b,b2,a2)]
        if (b-a).cross(a2-a).dot(inn)>0: vs=[vs[1],vs[0],vs[3],vs[2]]
        f=bm.faces.new(vs)
        for lp in f.loops: lp[ul].uv=uvof(F,lp.vert.co)
    # bridge small gaps between neighbouring raise quads (LiDAR wall tops whose ends don't meet -> dark vertical seams)
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.01); bm.faces.ensure_lookup_table()
    FM={f.index:SEG[f.index] for f in bm.faces}
    VE=[]
    for e in bm.edges:
        if len(e.link_faces)!=1: continue
        v1,v2=e.verts
        if (v1.co.xy-v2.co.xy).length<0.01 and abs(v1.co.z-v2.co.z)>0.3: VE.append((e,e.link_faces[0]))
    used=set(); nb=0
    for i,(e,f) in enumerate(VE):
        if i in used: continue
        c=e.verts[0].co.xy; best=None
        for j,(e2,f2) in enumerate(VE):
            if j==i or j in used or f2==f: continue
            d=(e2.verts[0].co.xy-c).length
            if d<0.6 and (best is None or d<best[0]): best=(d,j)
        if best is None: continue
        j=best[1]; e2,f2=VE[j]; used.add(i); used.add(j)
        A=sorted(e.verts,key=lambda v:v.co.z); B=sorted(e2.verts,key=lambda v:v.co.z)
        a,b,F,inn=FM[f.index]
        vs=[A[0],B[0],B[1],A[1]]
        if (vs[1].co-vs[0].co).cross(vs[3].co-vs[0].co).dot(inn)>0: vs=[vs[1],vs[0],vs[3],vs[2]]
        try: nf=bm.faces.new(vs)
        except ValueError: continue
        for lp in nf.loops: lp[ul].uv=uvof(F,lp.vert.co)
        nb+=1
    print('PY_BRIDGES',nb,'open vertical edges',len(VE))
    o1=mk(NAMES[0],bm,['PE_Dickson_brick_buff_no_red_spandrel_UNVERIFIED'],'UNVERIFIED (py, Nov 2 2026): brick parapet raised from the px 151.30 top to a level %.2f m, above the LiDAR roof membrane (152.51); no roofline photo'%ZB)
    # chains: per-vertex mitred inward vector (continuous back face / membrane / coping, no sawtooth or corner notches)
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
    bm=bmesh.new(); ul=bm.loops.layers.uv.new('facade'); VC={}
    def V(xy,z):
        kk=(round(xy.x,3),round(xy.y,3),round(z,3))
        if kk not in VC: VC[kk]=bm.verts.new((xy.x,xy.y,z))
        return VC[kk]
    for a,b,F,inn in SEG:
        if rep[key(a)]==rep[key(b)]: continue
        ai=off(a,TH); bi=off(b,TH)
        q=[V(ai,ZM-0.01),V(bi,ZM-0.01),V(bi,ZB),V(ai,ZB)]
        if (q[1].co-q[0].co).cross(q[3].co-q[0].co).dot(inn)<0: q=[q[1],q[0],q[3],q[2]]
        try: f=bm.faces.new(q)
        except ValueError: continue
        f.material_index=1
        for lp in f.loops: lp[ul].uv=uvof(F,Vector((lp.vert.co.x,lp.vert.co.y,lp.vert.co.z))-inn*TH)
        ao=off(a,MW); bo=off(b,MW)
        q=[V(ai,ZM),V(bi,ZM),V(bo,ZM),V(ao,ZM)]
        if (q[1].co-q[0].co).cross(q[3].co-q[0].co).z<0: q=[q[1],q[0],q[3],q[2]]
        try: f=bm.faces.new(q)
        except ValueError: continue
        f.material_index=0
        for lp in f.loops: lp[ul].uv=(lp.vert.co.x*0.25,lp.vert.co.y*0.25)
    mk(NAMES[1],bm,['Roof_tile_or_membrane','PE_Dickson_brick_buff_no_red_spandrel_UNVERIFIED'],'UNVERIFIED (py): parapet back face %.2f m thick + membrane strip at %.2f m closing the gap to the LiDAR roof edge'%(TH,ZM))
    # 3 continuous coping cap (metal) on the mitred chain: outer drip overhang OV, inner edge TH+0.04
    bm=bmesh.new(); VC={}
    def V2(xy,z):
        kk=(round(xy.x,3),round(xy.y,3),round(z,3))
        if kk not in VC: VC[kk]=bm.verts.new((xy.x,xy.y,z))
        return VC[kk]
    nc=0
    for a,b,F,inn in SEG:
        if rep[key(a)]==rep[key(b)]: continue
        P=[off(a,-OV),off(b,-OV),off(b,TH+0.04),off(a,TH+0.04)]
        hi=[V2(p,ZB+CT) for p in P]; lo=[V2(p,ZB-0.005) for p in P]; dr=[V2(p,ZB-0.035) for p in P[:2]]
        for fv in (hi,(dr[0],dr[1],hi[1],hi[0]),(lo[3],lo[2],hi[2],hi[3]),(lo[2],lo[3],dr[0],dr[1]) ):
            try: bm.faces.new(fv)
            except ValueError: pass
        nc+=1
    # cap the open chain ends / gaps: end faces where an edge belongs to one face only on the box ends
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    co_=mk(NAMES[2],bm,['ek_coping_metal'],'UNVERIFIED (py): continuous metal coping cap %.2f-%.2f m on a mitred chain, %.2f m drip overhang; profile generic'%(ZB,ZB+CT,OV))
    print('PY_COPING segs',nc,'faces',len(co_.data.polygons),'chain verts',len(INN))
    bm0.free()
    print('PY_PARAPET done ZB',ZB,'segs',len(SEG),'raise faces',len(o1.data.polygons))

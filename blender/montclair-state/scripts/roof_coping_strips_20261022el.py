# Session el (Oct 22 2026 ~1:35 AM ET): replace ek's per-edge coping boxes (read dashed edge-on: each LiDAR edge got
# its own box at its own z) with continuous mitred strips. Same top-edge selection as ek; edges are chained by shared
# vertices, z smoothed along the chain (moving median+mean, 5 pts), plan simplified (RDP 0.06 m), then one strip
# 0.30 m wide (0.03 m outward overhang), z-0.04..+0.05, mitred at joints. Generic profile (UNVERIFIED), same material.
# Hides (not deletes) the ek objects. Idempotent; SAVE=1 saves; REVERT=1 removes strips and unhides ek.
import bpy, bmesh, os, statistics
from mathutils import Vector
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='Roof_coping_strips_el'
col=bpy.data.collections.get(CN)
if col:
    for o in list(col.objects): bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(col)
ek=bpy.data.collections.get('Roof_coping_caps_ek')
for o in (ek.objects if ek else []):
    o.hide_render=o.hide_viewport=not REVERT
if REVERT:
    print('REVERTED')
else:
    m=bpy.data.materials['ek_coping_metal']
    col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
    names=[o.name for o in bpy.data.objects if o.type=='MESH' and o.name.endswith('roof (LiDAR)') and 'ej_orig_mi' in o.data.attributes]
    K=lambda v:(round(v.x,3),round(v.y,3))
    def rdp(pts,eps):
        if len(pts)<3: return pts
        a,b=pts[0],pts[-1]; ab=(b-a).to_2d(); L=ab.length
        def dist(p):
            ap=(p-a).to_2d()
            return ap.length if L<1e-6 else abs(ab.x*ap.y-ab.y*ap.x)/L
        i,dm=max(((i,dist(p)) for i,p in enumerate(pts[1:-1],1)),key=lambda t:t[1])
        if dm>eps: return rdp(pts[:i+1],eps)[:-1]+rdp(pts[i:],eps)
        return [a,b]
    tot=0
    for n in names:
        o=bpy.data.objects[n]; mw=o.matrix_world; n3=mw.to_3x3()
        bm=bmesh.new(); bm.from_mesh(o.data)
        segs=[]
        for f in bm.faces:
            fn=(n3@f.normal).normalized()
            if abs(fn.z)>=0.35: continue
            zmax=max((mw@v.co).z for v in f.verts)
            for e in f.edges:
                a=mw@e.verts[0].co; c=mw@e.verts[1].co
                if min(a.z,c.z)<zmax-0.15: continue
                if not [g for g in e.link_faces if g is not f and (n3@g.normal).normalized().z>0.8]: continue
                d=Vector((c.x-a.x,c.y-a.y,0))
                if d.length<0.05: continue
                d.normalize(); p=Vector((-d.y,d.x,0))
                if p.dot(Vector((fn.x,fn.y,0)))<0: p=-p
                segs.append((a,c,p))
        bm.free()
        # graph
        adj={}
        for i,(a,c,p) in enumerate(segs):
            adj.setdefault(K(a),[]).append(i); adj.setdefault(K(c),[]).append(i)
        used=set(); chains=[]
        def walk(i,start_key):
            ch=[]; key=start_key; cur=i
            while cur is not None and cur not in used:
                used.add(cur); a,c,p=segs[cur]
                if K(a)==key: pa,pb=a,c
                else: pa,pb=c,a
                ch.append((pa,pb,p)); key=K(pb)
                nxt=[j for j in adj.get(key,[]) if j not in used]
                cur=nxt[0] if len(adj.get(key,[]))==2 and nxt else None
            return ch
        ends=[k for k,v in adj.items() if len(v)!=2]
        for k in ends:
            for i in adj[k]:
                if i not in used: chains.append(walk(i,k))
        for i in range(len(segs)):
            if i not in used: chains.append(walk(i,K(segs[i][0])))
        out=bmesh.new(); L=0; nstrip=0
        for ch in chains:
            pts=[ch[0][0]]+[s[1] for s in ch]; ps=[s[2] for s in ch]
            closed=(K(pts[0])==K(pts[-1])) and len(pts)>3
            # smooth z
            zs=[q.z for q in pts]; N=len(zs); zz=[]
            for i in range(N):
                w=[zs[(i+j)%N] if closed else zs[min(max(i+j,0),N-1)] for j in range(-2,3)]
                zz.append(0.5*statistics.median(w)+0.5*sum(w)/5)
            pts=[Vector((q.x,q.y,z)) for q,z in zip(pts,zz)]
            # outward side per point (avg adjacent seg p)
            pv=[]
            for i in range(len(pts)):
                acc=Vector((0,0,0))
                if i>0: acc+=ps[i-1]
                if i<len(ps): acc+=ps[i]
                if closed and i==0: acc+=ps[-1]
                pv.append(acc.normalized() if acc.length>1e-6 else ps[min(i,len(ps)-1)])
            # simplify plan, keep indices
            idx=list(range(len(pts)))
            if not closed:
                keep=rdp([pts[i].copy() for i in idx],0.06); kk=set(K(q) for q in keep)
                idx=[i for i in idx if K(pts[i]) in kk or i in (0,len(pts)-1)]
            P=[pts[i] for i in idx]; PV=[pv[i] for i in idx]
            if closed and K(P[0])==K(P[-1]): P=P[:-1]; PV=PV[:-1]
            if len(P)<2: continue
            M=len(P)
            # mitred offset direction per vertex
            def segdir(i): return (P[(i+1)%M]-P[i]).to_2d().normalized().to_3d()
            rows=[]
            for i in range(M):
                dirs=[]
                if closed or i>0: dirs.append(segdir((i-1)%M))
                if closed or i<M-1: dirs.append(segdir(i))
                nrm=[Vector((-dd.y,dd.x,0)) for dd in dirs]
                nrm=[nn if nn.dot(PV[i])>=0 else -nn for nn in nrm]
                avg=sum(nrm,Vector()).normalized() if sum(nrm,Vector()).length>1e-6 else nrm[0]
                sc=1.0/max(0.5,avg.dot(nrm[0]))
                base=P[i].copy()
                if not closed and i==0: base-=segdir(0)*0.03
                if not closed and i==M-1: base+=segdir(M-2)*0.03
                r=[out.verts.new(base+avg*off*sc+Vector((0,0,dz))) for off in (0.03,-0.27) for dz in (-0.04,0.05)]
                rows.append(r)  # o_lo,o_hi,i_lo,i_hi
            segsN=M if closed else M-1
            for i in range(segsN):
                A=rows[i]; B=rows[(i+1)%M]
                for q in ((A[1],B[1],B[3],A[3]),(A[0],A[2],B[2],B[0]),(A[0],B[0],B[1],A[1]),(A[2],A[3],B[3],B[2])):
                    try: out.faces.new(q)
                    except ValueError: pass
                L+=(P[(i+1)%M]-P[i]).to_2d().length
            if not closed:
                for A in (rows[0],rows[-1]):
                    try: out.faces.new((A[0],A[1],A[3],A[2]))
                    except ValueError: pass
            nstrip+=1
        bmesh.ops.recalc_face_normals(out, faces=out.faces)
        me=bpy.data.meshes.new('el_coping_'+n); out.to_mesh(out_me:=me) if False else out.to_mesh(me); out.free(); me.materials.append(m)
        for poly in me.polygons: poly.use_smooth=False
        ob=bpy.data.objects.new('el coping strips '+n.replace(' roof (LiDAR)','')+' (generic, UNVERIFIED profile)', me)
        col.objects.link(ob); tot+=nstrip
        print('STRIPS',n,len(segs),'edges ->',nstrip,'strips',round(L,1),'m')
    print('TOTAL strips',tot)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

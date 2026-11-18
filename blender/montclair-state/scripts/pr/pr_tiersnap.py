# pr: Feliciano upper tier walls that stand 3-50 cm inside the tier wall directly below (near-parallel) leave a thin
# membrane sliver / interleaved planes (thin diagonal dark line in the PO close-up, patchy grey NW tower west face).
# Each such upper-tier wall vertex is snapped onto the next-lower tier's wall plane, 1.5 cm inside, processing tiers
# bottom-up; skipped where either tier carries an eave at that edge. Tier windows carried with their host face.
# Original coords in point attr pr_co0; REVERT=1 restores. ALL UNVERIFIED.
import bpy, os, bmesh, json, re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; DRY=os.environ.get('DRY')=='1'
MAXD=float(os.environ.get('PR_MAXD','0.6')); MIND=0.0; OFF=0.015
tiers=sorted([o for o in bpy.data.objects if re.match(r'PN_Feliciano_tier_[\d.]+_UNVERIFIED$',o.name)],key=lambda o:float(o.name.split('_')[3]))
wo=bpy.data.objects.get('PN_Feliciano_tier_windows_UNVERIFIED')
if REV:
    for o in tiers+([wo] if wo else []):
        a=o.data.attributes.get('pr_co0')
        if a:
            for v in o.data.vertices: v.co=Vector(a.data[v.index].vector)
            o.data.attributes.remove(a); o.data.update()
    print('PR_TIERSNAP reverted')
else:
    eo=bpy.data.objects['PN_Feliciano_eaves_UNVERIFIED']; ew=eo.matrix_world
    EB=BVHTree.FromPolygons([ew@v.co for v in eo.data.vertices],[list(p.vertices) for p in eo.data.polygons])
    def eave_near(pt,n,ztop):
        # eave band hugging this wall top? probe 5..35 cm outside, from 0.4 m above down 0.8 m
        for s in (0.08,0.2,0.35):
            q=Vector((pt.x,pt.y,ztop+0.4))+n*s
            h=EB.ray_cast(q,Vector((0,0,-1)),0.8)
            if h[0] is not None: return True
        return False
    def wallfaces(o):
        tw=o.matrix_world; out=[]
        for p in o.data.polygons:
            n=tw.to_3x3()@p.normal
            if abs(n.z)>0.1 or p.area<0.05: continue
            n.z=0; n.normalize(); vs=[tw@o.data.vertices[i].co for i in p.vertices]
            out.append((n,tw@p.center,vs,max(v.z for v in vs)))
        return out
    stats={}
    for k in range(1,len(tiers)):
        lo=tiers[k-1]; up=tiers[k]; LF=wallfaces(lo); ztl=float(lo.name.split('_')[3])
        me=up.data; tw=up.matrix_world; ti=tw.inverted()
        a=me.attributes.get('pr_co0')
        if a is None:
            a=me.attributes.new('pr_co0','FLOAT_VECTOR','POINT')
            for v in me.vertices: a.data[v.index].vector=v.co
        vf={}
        for p in me.polygons:
            n=tw.to_3x3()@p.normal
            if abs(n.z)>0.1: continue
            n.z=0; n.normalize()
            for i in p.vertices: vf.setdefault(i,[]).append(n)
        ztu=float(up.name.split('_')[3])
        moved=0; mx=0; skip_e=0
        for i,ns in vf.items():
            v=tw@me.vertices[i].co
            cons=[]
            for tn in ns:
                best=None
                for (pn,pc,vs,zt) in LF:
                    if pn.dot(tn)<0.97: continue
                    d=(v-pc).dot(pn)            # negative = inside the lower wall
                    if d>-MIND or d<-MAXD: continue
                    t=Vector((-pn.y,pn.x,0)); ss=[(q-pc).dot(t) for q in vs]; s=(v-pc).dot(t)
                    if s<min(ss)-0.3 or s>max(ss)+0.3: continue
                    if best is None or d>best[0]: best=(d,pn,pc)
                if best: cons.append(best)
            if not cons: continue
            d0,n0,_=cons[0]
            if eave_near(v-n0*d0,n0,ztl): skip_e+=1; continue   # lower-tier eave on this edge -> real ledge, keep
            if len(cons)==1 or abs(cons[0][1].dot(cons[1][1]))>0.9:
                d,nn,pc=cons[0]; nv=v-nn*(d+OFF)
            else:
                (d1,n1,p1),(d2,n2,p2)=cons[:2]
                c1=n1.dot(p1)-OFF; c2=n2.dot(p2)-OFF; det=n1.x*n2.y-n1.y*n2.x
                if abs(det)<1e-6: continue
                nv=Vector(((c1*n2.y-c2*n1.y)/det,(n1.x*c2-n2.x*c1)/det,v.z))
            sh=(nv-v).length
            if sh>MAXD+0.1: continue
            mx=max(mx,sh); moved+=1
            if not DRY: me.vertices[i].co=ti@nv
        me.update(); stats[up.name.split('_')[3]]=(moved,round(mx,2),skip_e)
    print('PR_TIERSNAP',json.dumps(stats),'DRY',DRY)
    if wo:
        me=wo.data; a=me.attributes.get('pr_co0')
        if a is None:
            a=me.attributes.new('pr_co0','FLOAT_VECTOR','POINT')
            for v in me.vertices: a.data[v.index].vector=v.co
        faces=[]
        for o in tiers:
            tw=o.matrix_world; at=o.data.attributes.get('pr_co0')
            if at is None: continue
            for p in o.data.polygons:
                n0=tw.to_3x3()@p.normal
                if abs(n0.z)>0.1: continue
                n0.z=0; n0.normalize()
                vs=[tw@Vector(at.data[i].vector) for i in p.vertices]; c0=sum(vs,Vector())/len(vs)
                sh=sum(((tw@o.data.vertices[i].co)-(tw@Vector(at.data[i].vector)) for i in p.vertices),Vector())/len(p.vertices)
                faces.append((n0,c0,sh.dot(n0),vs))
        bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
        seen=set(); nis=0; mxs=0; ww=wo.matrix_world; wi=ww.inverted()
        for v in bm.verts:
            if v.index in seen: continue
            isl=[]; st=[v]; seen.add(v.index)
            while st:
                x=st.pop(); isl.append(x.index)
                for e in x.link_edges:
                    y=e.other_vert(x)
                    if y.index not in seen: seen.add(y.index); st.append(y)
            c=sum((ww@Vector(a.data[i].vector) for i in isl),Vector())/len(isl)
            best=None
            for (n0,c0,s,vs) in faces:
                d=abs((c-c0).dot(n0))
                if d>0.6: continue
                t=Vector((-n0.y,n0.x,0)); ss=[(q-c0).dot(t) for q in vs]; sv=(c-c0).dot(t); zs=[q.z for q in vs]
                if sv<min(ss)-0.2 or sv>max(ss)+0.2 or c.z<min(zs)-0.5 or c.z>max(zs)+0.5: continue
                if best is None or d<best[0]: best=(d,n0,s)
            if best and abs(best[2])>0.005:
                dv=best[1]*best[2]; nis+=1; mxs=max(mxs,abs(best[2]))
                if not DRY:
                    for i in isl: me.vertices[i].co=wi@(ww@Vector(a.data[i].vector)+dv)
        bm.free(); me.update(); print('PR_WIN islands_moved',nis,'max',round(mxs,3))

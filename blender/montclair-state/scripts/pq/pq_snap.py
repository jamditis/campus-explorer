# pq: Feliciano tier walls that run nearly coplanar with the old LiDAR wall planes (crossing diagonal seams)
# are snapped 3 cm INSIDE the old wall plane, so one surface wins consistently. UNVERIFIED. REVERT=1 restores pq_co0.
import bpy, os, bmesh, math, json
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; DRY=os.environ.get('DRY')=='1'
MAXD=float(os.environ.get('MAXD','0.45')); OFF=0.03
old=bpy.data.objects['Feliciano School of Business walls']; mw=old.matrix_world
planes=[]
for p in old.data.polygons:
    n=(mw.to_3x3()@p.normal); 
    if abs(n.z)>0.1 or p.area<1.0: continue
    n.z=0; n.normalize(); vs=[mw@old.data.vertices[i].co for i in p.vertices]
    planes.append((n,mw@p.center,min(v.z for v in vs),max(v.z for v in vs),vs))
tiers=[o for o in bpy.data.objects if o.name.startswith('PN_Feliciano_tier_') and 'windows' not in o.name]
stats={}
for o in tiers:
    me=o.data; tw=o.matrix_world; ti=tw.inverted()
    a=me.attributes.get('pq_co0')
    if REV:
        if a:
            for v in me.vertices: v.co=Vector(a.data[v.index].vector)
            me.attributes.remove(a); me.update()
        continue
    if a is None:
        a=me.attributes.new('pq_co0','FLOAT_VECTOR','POINT')
        for v in me.vertices: a.data[v.index].vector=v.co
    vf={}
    for p in me.polygons:
        n=tw.to_3x3()@p.normal
        if abs(n.z)>0.1: continue
        n.z=0; n.normalize()
        for i in p.vertices: vf.setdefault(i,[]).append(n)
    moved=0; mx=0
    for i,ns in vf.items():
        v=tw@Vector(a.data[i].vector)
        cons=[]
        for tn in ns:
            best=None
            for (pn,pc,z0,z1,vs) in planes:
                dt=pn.dot(tn)
                if abs(dt)<0.985: continue
                nn=pn if dt>0 else -pn
                d=(v-pc).dot(nn)
                if abs(d)>MAXD: continue
                # horizontal extent check along the wall
                t=Vector((-nn.y,nn.x,0)); ss=[(q-pc).dot(t) for q in vs]; s=(v-pc).dot(t)
                if s<min(ss)-1.0 or s>max(ss)+1.0: continue
                if best is None or d>best[0]: best=(d,nn,pc)   # most outward old-wall face (old walls are slabs with inverted normals)
            if best: cons.append(best)
        if not cons: continue
        nv=v.copy()
        if len(cons)==1 or abs(cons[0][1].dot(cons[1][1]))>0.9:
            d,nn,pc=cons[0]; nv=v-nn*(d+OFF)
        else:
            (d1,n1,p1),(d2,n2,p2)=cons[:2]
            # solve n1.x=n1.p1-OFF, n2.x=n2.p2-OFF in xy
            c1=n1.dot(p1)-OFF; c2=n2.dot(p2)-OFF; det=n1.x*n2.y-n1.y*n2.x
            if abs(det)<1e-6: continue
            x=(c1*n2.y-c2*n1.y)/det; y=(n1.x*c2-n2.x*c1)/det; nv=Vector((x,y,v.z))
        sh=(nv-v).length
        if sh>MAXD+0.1: continue
        mx=max(mx,sh); moved+=1
        if not DRY: me.vertices[i].co=ti@nv
    me.update(); stats[o.name]=(moved,round(mx,3))
print('PQ_SNAP',json.dumps(stats),'planes',len(planes),'REV',REV,'DRY',DRY)
# carry the PN tier window units with their host wall (normal component of the host face's shift)
wo=bpy.data.objects.get('PN_Feliciano_tier_windows_UNVERIFIED')
if wo:
    me=wo.data; a=me.attributes.get('pq_co0')
    if REV:
        if a:
            for v in me.vertices: v.co=Vector(a.data[v.index].vector)
            me.attributes.remove(a); me.update()
    else:
        if a is None:
            a=me.attributes.new('pq_co0','FLOAT_VECTOR','POINT')
            for v in me.vertices: a.data[v.index].vector=v.co
        faces=[]
        for o in tiers:
            tw=o.matrix_world; at=o.data.attributes['pq_co0']
            for p in o.data.polygons:
                n0=tw.to_3x3()@p.normal
                if abs(n0.z)>0.1: continue
                n0.z=0; n0.normalize()
                c0=sum((tw@Vector(at.data[i].vector) for i in p.vertices),Vector())/len(p.vertices)
                sh=sum(((tw@o.data.vertices[i].co)-(tw@Vector(at.data[i].vector)) for i in p.vertices),Vector())/len(p.vertices)
                vs=[tw@Vector(at.data[i].vector) for i in p.vertices]
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
                t=Vector((-n0.y,n0.x,0)); ss=[(q-c0).dot(t) for q in vs]; sv=(c-c0).dot(t)
                zs=[q.z for q in vs]
                if sv<min(ss)-0.2 or sv>max(ss)+0.2 or c.z<min(zs)-0.5 or c.z>max(zs)+0.5: continue
                if best is None or d<best[0]: best=(d,n0,s)
            if best and abs(best[2])>0.005:
                dv=best[1]*best[2]; nis+=1; mxs=max(mxs,abs(best[2]))
                if not DRY:
                    for i in isl: me.vertices[i].co=wi@(ww@Vector(a.data[i].vector)+dv)
        bm.free(); me.update(); print('PQ_WIN islands_moved',nis,'max',round(mxs,3))

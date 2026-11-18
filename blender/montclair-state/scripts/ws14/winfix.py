"""ws14: TZ_Cole_north_addition windows were generated facing south on every wall (rotated 90°),
so on the east face they stuck 0.8 m out as dark slabs. Rotate each window onto its wall, recess it
RECESS m, cut real openings in the wall face with stucco reveals, add a sill under each. SAVE=1 saves."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix
RECESS=float(os.environ.get('RECESS','0.10'))
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; me=o.data
slots=[s.material.name for s in o.material_slots]
def slot(name):
    if name not in slots:
        me.materials.append(bpy.data.materials[name]); slots.append(name)
    return slots.index(name)
MUL=slots.index('TZ_Cole_add_mullion_UNVERIFIED'); GLA=slots.index('TZ_Cole_add_glass_UNVERIFIED')
PANEL=slots.index('TZ_Cole_add_panel_UNVERIFIED'); STU=slots.index('COLE_stucco_plain_bq')
SILL=slot('TZ_Cole_sill_drip_UNVERIFIED')
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
# components
seen=set(); comps=[]
for f in bm.faces:
    if f.index in seen or f.material_index not in (MUL,GLA): continue
    st=[f]; comp=[]; seen.add(f.index)
    while st:
        g=st.pop(); comp.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in seen and h.material_index in (MUL,GLA): seen.add(h.index); st.append(h)
    comps.append(comp)
# glass boxes are separate components from mullion boxes; pair them by center
def cen(c):
    vs={v for f in c for v in f.verts}; return sum((v.co for v in vs),Vector())/len(vs), vs
groups=[]
mulc=[c for c in comps if c[0].material_index==MUL]; glac=[c for c in comps if c[0].material_index==GLA]
gc=[(cen(c)[0],cen(c)[1]) for c in glac]
used=set()
for m in mulc:
    cm,vm=cen(m)
    vs=set(vm)
    for i,(cg,vg) in enumerate(gc):
        if i not in used and (cg-cm).length<0.3: vs|=vg; used.add(i)
    big=max([f for f in m if abs(f.normal.z)<0.1],key=lambda f:f.calc_area())
    groups.append(dict(c=cm,verts=vs,n=Vector((big.normal.x,big.normal.y,0)).normalized(),mverts=vm))
print('glass unattached',len(gc)-len(used), 'mullion comps',len(mulc))
print('windows',len(groups))
walls=[f for f in bm.faces if f.material_index in (PANEL,STU) and abs(f.normal.z)<0.1 and f.calc_area()>4]
report=[]
for F in walls:
    Fn=Vector((F.normal.x,F.normal.y,0)).normalized(); P=F.verts[0].co.copy()
    W=Vector((-Fn.y,Fn.x,0))
    us=[(v.co-P).dot(W) for v in F.verts]; zs=[v.co.z for v in F.verts]
    u0,u1,z0,z1=min(us),max(us),min(zs),max(zs)
    mine=[g for g in groups if abs((g['c']-P).dot(Fn))<0.5 and u0+0.2<(g['c']-P).dot(W)<u1-0.2 and z0<g['c'].z<z1]
    if not mine: continue
    if len(F.verts)!=4: print('skip non-quad wall',F.index,len(mine)); continue
    ops=[]
    for g in mine:
        ang=math.atan2(g['n'].x*Fn.y-g['n'].y*Fn.x, g['n'].dot(Fn))  # angle from n to Fn
        ang=-ang
        # choose minimal rotation modulo pi
        while ang>math.pi/2: ang-=math.pi
        while ang<-math.pi/2: ang+=math.pi
        R=Matrix.Rotation(ang,3,'Z'); c=g['c']
        for v in g['verts']: v.co=c+R@(v.co-c)
        front=max((v.co-P).dot(Fn) for v in g['mverts'])
        sh=-(front+RECESS)
        for v in g['verts']: v.co+=Fn*sh
        mu=[(v.co-P).dot(W) for v in g['mverts']]; mz=[v.co.z for v in g['mverts']]
        ops.append((min(mu)-0.005,max(mu)+0.005,min(mz)-0.005,max(mz)+0.005))
        g['done']=True
    # rebuild wall face as grid with holes
    mat=F.material_index
    ub=sorted(set([u0,u1]+[x for op in ops for x in op[:2]])); zb=sorted(set([z0,z1]+[x for op in ops for x in op[2:]]))
    def dd(xs):
        out=[]
        for x in sorted(xs):
            if not out or x-out[-1]>0.002: out.append(x)
        return out
    ub=dd(ub); zb=dd(zb)
    def V(u,z): 
        p=P+W*u; return Vector((p.x,p.y,z))
    vc={}
    def gv(u,z):
        k=(round(u,4),round(z,4))
        if k not in vc: vc[k]=bm.verts.new(V(u,z))
        return vc[k]
    bm.faces.remove(F)
    nf=0
    for i in range(len(ub)-1):
        for j in range(len(zb)-1):
            um=(ub[i]+ub[i+1])/2; zm=(zb[j]+zb[j+1])/2
            if any(a<um<b and c<zm<d for a,b,c,d in ops): continue
            q=[gv(ub[i],zb[j]),gv(ub[i+1],zb[j]),gv(ub[i+1],zb[j+1]),gv(ub[i],zb[j+1])]
            f=bm.faces.new(q); f.material_index=mat; f.normal_update()
            if f.normal.dot(Fn)<0: f.normal_flip()
            nf+=1
    D=RECESS+0.03
    for a,b,c,d in ops:
        # reveals (normals pointing into the opening)
        for (ua,za,ub_,zb_,nn) in [(a,c,a,d,W),(b,c,b,d,-W)]:
            q=[bm.verts.new(V(ua,za)),bm.verts.new(V(ub_,zb_)),bm.verts.new(V(ub_,zb_)-Fn*D),bm.verts.new(V(ua,za)-Fn*D)]
            f=bm.faces.new(q); f.material_index=mat; f.normal_update()
            if f.normal.dot(nn)<0: f.normal_flip()
        for (zz,nn) in [(c,Vector((0,0,1))),(d,Vector((0,0,-1)))]:
            q=[bm.verts.new(V(a,zz)),bm.verts.new(V(b,zz)),bm.verts.new(V(b,zz)-Fn*D),bm.verts.new(V(a,zz)-Fn*D)]
            f=bm.faces.new(q); f.material_index=mat; f.normal_update()
            if f.normal.dot(nn)<0: f.normal_flip()
        # sill: box u a-0.05..b+0.05, z c-0.06..c+0.005, from -RECESS to +0.05
        sa,sb,sz0,sz1,s0,s1=a-0.05,b+0.05,c-0.06,c+0.006,-RECESS,0.05
        cs=[]
        for uu in (sa,sb):
            for zz in (sz0,sz1):
                for dd in (s0,s1):
                    cs.append(bm.verts.new(V(uu,zz)+Fn*dd))
        idx=lambda i,j,k:cs[i*4+j*2+k]
        bc=sum((v.co for v in cs),Vector())/8
        for quad in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
            f=bm.faces.new([cs[i] for i in quad]); f.material_index=SILL; f.normal_update()
            if f.normal.dot(f.calc_center_median()-bc)<0: f.normal_flip()
    report.append((F.index if False else 'wall',[round(x,2) for x in Fn],len(mine),nf))
print('REPORT',report, 'unplaced',sum(1 for g in groups if not g.get('done')))
bm.to_mesh(me); me.update(); bm.free()
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED')

# pt (Nov 1 2026): Calcia slot glazing detail. ALL UNVERIFIED (no photo of the glazing; refs calcia_web_05/07 only show narrow slots).
# 1) the pr transom bar (box 4 of each 6-box slot group in PR_Calcia_slot_surrounds, 1.5 cm proud of the wall) is removed;
# 2) PT_Calcia_slot_glazing_UNVERIFIED adds, per slot (same slot maths as pr/ps, computed on the uncut PS_backup_Calcia_walls):
#    a slim glazing frame + transom at the glass plane (0.12 m in), a dark 2 cm shadow-line reglet at head and jambs just inside
#    the wall face, and an interior blind behind the glass dropped to a seeded, varied height (some fully up).
# PR mesh kept as fake-user 'PT_backup_PR_surrounds'; REVERT=1 restores it exactly and removes the new object.
import bpy, bmesh, os, math, random
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; ON='PT_Calcia_slot_glazing_UNVERIFIED'; BK='PT_backup_PR_surrounds'
pr=bpy.data.objects['PR_Calcia_slot_surrounds_UNVERIFIED']; pme=pr.data
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m2=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m2); print('REVERTED_PT_GLAZING')
if BK in bpy.data.meshes:
    bk=bpy.data.meshes[BK]; bm=bmesh.new(); bm.from_mesh(bk); bm.to_mesh(pme); bm.free(); pme.update(); bpy.data.meshes.remove(bk); print('REVERTED_PT_PR V',len(pme.vertices))
if not REV:
    bk=pme.copy(); bk.name=BK; bk.use_fake_user=True
    assert len(pme.vertices)%48==0
    bm=bmesh.new(); bm.from_mesh(pme); bm.verts.ensure_lookup_table()
    dv=[bm.verts[i] for i in range(len(bm.verts)) if (i%48)//8==4]
    bmesh.ops.delete(bm,geom=dv,context='VERTS'); bm.to_mesh(pme); bm.free(); pme.update(); print('PT_transoms_removed',len(dv)//8,'PR V',len(pme.vertices))
    w=bpy.data.objects['Calcia Hall walls']; me=bpy.data.meshes['PS_backup_Calcia_walls']
    mw=w.matrix_world; uv=me.uv_layers['facade'].data
    cen=sum((mw@v.co for v in me.vertices),Vector())/len(me.vertices)
    FS=[]
    for p in me.polygons:
        n=(mw.to_3x3()@p.normal)
        if abs(n.z)>0.1 or p.area<1: continue
        n.z=0; n.normalize(); c=mw@p.center
        if (c-cen).dot(n)<0: n=-n
        L=list(p.loop_indices)
        P=[mw@me.vertices[me.loops[l].vertex_index].co for l in L]; U=[uv[l].uv.copy() for l in L]
        best=None
        for i in range(len(L)):
            for j in range(i+1,len(L)):
                for k in range(j+1,len(L)):
                    a=(U[j]-U[i]); b=(U[k]-U[i]); det=a.x*b.y-a.y*b.x
                    if best is None or abs(det)>abs(best[0]): best=(det,i,j,k)
        det,i,j,k=best
        if abs(det)<0.3: continue
        a=U[j]-U[i]; b=U[k]-U[i]; A=P[j]-P[i]; B=P[k]-P[i]
        Wu=(A*b.y-B*a.y)/det; Wv=(B*a.x-A*b.x)/det
        if abs(Wu.length-1)>0.15 or abs(Wv.length-1)>0.15: continue
        FS.append(dict(idx=p.index,umin=min(q.x for q in U),umax=max(q.x for q in U),vmin=min(q.y for q in U),vmax=max(q.y for q in U),P0=P[i],U0=U[i].copy(),Wu=Wu,Wv=Wv,n=n))
    WT=float(w.get('win_top',99.0))
    UMIN=min(F['umin'] for F in FS); UMAX=max(F['umax'] for F in FS)
    SL=[]
    for kb in range(math.floor(UMIN/2.4)-1,math.ceil(UMAX/2.4)+1):
        u0=2.4*kb+0.75; u1=u0+0.9; uc=(u0+u1)/2
        ov=[F for F in FS if F['umax']>u0-0.06 and F['umin']<u1+0.06]
        if not ov: continue
        if min(F['umin'] for F in ov)>u0-0.06 or max(F['umax'] for F in ov)<u1+0.06: continue
        if any(F['n'].dot(ov[0]['n'])<0.985 for F in ov): continue
        host=[F for F in ov if F['umin']<=uc<=F['umax']]
        if not host: continue
        F=host[0]; vmx=min(G['vmax'] for G in ov)-0.12; vmn=max(G['vmin'] for G in ov)
        for js in range(0,8):
            v0=max(0.1+4.4*js+0.6,0.8); v1=min(0.1+4.4*js+3.8,WT,vmx)
            if v1-v0<1.0 or v0<vmn+0.1: continue
            SL.append(dict(u0=u0,u1=u1,v0=v0,v1=v1,F=F))
    print('PT_slots',len(SL))
    rnd=random.Random(20261101)
    bm=bmesh.new()
    def box(c,ex,ey,ez,mi):
        vs=[bm.verts.new(c+ex*sx+ey*sy+ez*sz) for sx in (-1,1) for sy in (-1,1) for sz in (-1,1)]
        for q in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]: bm.faces.new([vs[i] for i in q]).material_index=mi
    def quad(a,b,c,d,mi): bm.faces.new([bm.verts.new(a),bm.verts.new(b),bm.verts.new(c),bm.verts.new(d)]).material_index=mi
    nb=0
    for s in SL:
        F=s['F']; n=F['n']; eu=F['Wu'].normalized(); ev=F['Wv'].normalized()
        f=lambda u,v: F['P0']+F['Wu']*(u-F['U0'].x)+F['Wv']*(v-F['U0'].y)
        u0,u1,v0,v1=s['u0'],s['u1'],s['v0'],s['v1']
        def fr(ua,ub,va,vb,dc,hd,mi):
            box(f((ua+ub)/2,(va+vb)/2)+n*dc,eu*(abs(ub-ua)/2),ev*(abs(vb-va)/2),n*hd,mi)
        g=0.03; dc=-0.105; hd=0.012                      # glazing frame just in front of the glass (glass at -0.12)
        fr(u0,u0+g,v0,v1,dc,hd,0); fr(u1-g,u1,v0,v1,dc,hd,0); fr(u0,u1,v1-g,v1,dc,hd,0); fr(u0,u1,v0,v0+g,dc,hd,0)
        tv=v0+(v1-v0)/3; fr(u0,u1,tv-0.022,tv+0.022,dc,hd,0)   # transom now at the glass plane
        # shadow-line reglet: dark 2 cm strip on head soffit + jambs, 0.5-2.5 cm inside the wall face, 2 mm off the reveal
        e=0.002; a0=-0.005; a1=-0.025
        for (pa,pb,off) in ((f(u0,v1),f(u1,v1),-ev*e),(f(u0,v0),f(u0,v1),eu*e),(f(u1,v0),f(u1,v1),-eu*e)):
            quad(pa+off+n*a0,pb+off+n*a0,pb+off+n*a1,pa+off+n*a1,2)
        # interior blind 6 cm behind the glass, varied drop
        r=rnd.random()
        frac=0.04 if r<0.22 else (rnd.uniform(0.15,0.45) if r<0.7 else rnd.uniform(0.5,0.85))
        vb=v1-0.03-frac*(v1-v0-0.06); db=-0.18
        quad(f(u0+0.025,vb)+n*db,f(u1-0.025,vb)+n*db,f(u1-0.025,v1-0.03)+n*db,f(u0+0.025,v1-0.03)+n*db,1)
        fr(u0+0.025,u1-0.025,vb-0.012,vb,db+0.004,0.004,3)    # bottom rail
        fr(u0+0.02,u1-0.02,v1-0.07,v1-0.03,db+0.01,0.012,3)  # head box
        nb+=1
    m2=bpy.data.meshes.new(ON); bm.to_mesh(m2); bm.free()
    def mat(name,col,rough,slats=False):
        m=bpy.data.materials.get(name)
        if m is None:
            m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']
            b.inputs['Base Color'].default_value=col; b.inputs['Roughness'].default_value=rough
            if slats:
                tc=nt.nodes.new('ShaderNodeTexCoord'); wv=nt.nodes.new('ShaderNodeTexWave'); wv.bands_direction='Z'
                wv.inputs['Scale'].default_value=12.57; cr=nt.nodes.new('ShaderNodeValToRGB')
                cr.color_ramp.elements[0].position=0.15; cr.color_ramp.elements[0].color=(col[0]*0.55,col[1]*0.55,col[2]*0.55,1)
                cr.color_ramp.elements[1].position=0.35; cr.color_ramp.elements[1].color=col
                nt.links.new(tc.outputs['Object'],wv.inputs['Vector']); nt.links.new(wv.outputs['Fac'],cr.inputs['Fac']); nt.links.new(cr.outputs['Color'],b.inputs['Base Color'])
        return m
    m2.materials.append(bpy.data.materials['PE_Dickson_coping_dark_bronze_UNVERIFIED'])
    m2.materials.append(mat('PT_blind_slats_offwhite_UNVERIFIED',(0.72,0.69,0.62,1),0.7,True))
    m2.materials.append(bpy.data.materials['PS_slot_interior_dark_UNVERIFIED'])
    m2.materials.append(mat('PT_blind_rail_grey_UNVERIFIED',(0.45,0.45,0.44,1),0.5))
    o=bpy.data.objects.new(ON,m2); w.users_collection[0].objects.link(o); print('PT_GLAZING',len(SL),'blinds',nb)

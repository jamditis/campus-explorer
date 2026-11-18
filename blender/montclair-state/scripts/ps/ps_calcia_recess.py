# ps (Nov 1 2026): Calcia slot windows become REAL recessed openings behind the pr surrounds. ALL UNVERIFIED.
# The 'Calcia Hall walls' faces are cut open exactly at the inner edge of each pr frame (same facade-UV maths as
# pr_calcia_slots / pe shader slots), and PS_Calcia_slot_reveals_glass_UNVERIFIED adds 4 reveal liners (0.22 m deep),
# a glass pane set back 0.12 m, and a dark interior back box 0.6 m in (so the hollow shell never shows through).
# Original wall mesh kept as fake-user mesh 'PS_backup_Calcia_walls'; REVERT=1 restores it exactly and removes the new object.
import bpy, bmesh, os, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; ON='PS_Calcia_slot_reveals_glass_UNVERIFIED'; BK='PS_backup_Calcia_walls'
w=bpy.data.objects['Calcia Hall walls']; me=w.data
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m2=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m2); print('REVERTED_PS_REVEALS')
if BK in bpy.data.meshes:
    bk=bpy.data.meshes[BK]; bm=bmesh.new(); bm.from_mesh(bk); bm.to_mesh(me); bm.free(); me.update()
    bpy.data.meshes.remove(bk); print('REVERTED_PS_WALLS V',len(me.vertices))
if not REV:
    bk=me.copy(); bk.name=BK; bk.use_fake_user=True
    mw=w.matrix_world; uvl=me.uv_layers['facade']; uv=uvl.data
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
            SL.append(dict(u0=u0,u1=u1,v0=v0,v1=v1,F=F,faces=[G['idx'] for G in ov]))
    print('PS_slots',len(SL))
    # --- cut the wall: bisect only the faces that host slots, then delete the cells inside the slots
    bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    src=bm.faces.layers.int.new('ps_src')
    for f in bm.faces: f[src]=f.index
    uvL=bm.loops.layers.uv['facade']
    imw=mw.inverted()
    byface={}
    for s in SL:
        for fi in s['faces']: byface.setdefault(fi,[]).append(s)
    for fi,ss in byface.items():
        F=[G for G in FS if G['idx']==fi][0]
        eu=F['Wu'].normalized(); ev=F['Wv'].normalized()
        f=lambda u,v: F['P0']+F['Wu']*(u-F['U0'].x)+F['Wv']*(v-F['U0'].y)
        planes=set()
        for s in ss:
            for u in (s['u0'],s['u1']):
                if F['umin']+0.005<u<F['umax']-0.005: planes.add(('u',round(u,4)))
            for v in (s['v0'],s['v1']): planes.add(('v',round(v,4)))
        for kind,val in sorted(planes):
            fs=[x for x in bm.faces if x[src]==fi]
            geom=list(fs)+list({e for x in fs for e in x.edges})+list({v for x in fs for v in x.verts})
            if kind=='u': co=imw@f(val,F['U0'].y); no=(imw.to_3x3()@F['Wu']).normalized()
            else: co=imw@f(F['U0'].x,val); no=(imw.to_3x3()@F['Wv']).normalized()
            bmesh.ops.bisect_plane(bm,geom=geom,dist=0.0005,plane_co=co,plane_no=no)
    dele=[]
    for x in bm.faces:
        if x[src] not in byface: continue
        uvs=[l[uvL].uv for l in x.loops]; uc=sum((q.x for q in uvs))/len(uvs); vc=sum((q.y for q in uvs))/len(uvs)
        for s in byface[x[src]]:
            if s['u0']<uc<s['u1'] and s['v0']<vc<s['v1']: dele.append(x); break
    bmesh.ops.delete(bm,geom=dele,context='FACES_ONLY')
    bm.faces.layers.int.remove(src)
    bm.to_mesh(me); bm.free(); me.update(); print('PS_cut cells',len(dele),'V',len(me.vertices))
    # --- reveals, glass, back box
    bm=bmesh.new()
    def quad(a,b,c,d,mi): bm.faces.new([bm.verts.new(a),bm.verts.new(b),bm.verts.new(c),bm.verts.new(d)]).material_index=mi
    for s in SL:
        F=s['F']; n=F['n']; f=lambda u,v: F['P0']+F['Wu']*(u-F['U0'].x)+F['Wv']*(v-F['U0'].y)
        A=f(s['u0'],s['v0']); B=f(s['u1'],s['v0']); C=f(s['u1'],s['v1']); D=f(s['u0'],s['v1'])
        dr=-n*0.22; dg=-n*0.12; db=-n*0.6
        for p,q in ((A,B),(B,C),(C,D),(D,A)): quad(p,q,q+dr,p+dr,0)          # reveal liners
        quad(A+dg,B+dg,C+dg,D+dg,1)                                          # glass
        quad(A+db,B+db,C+db,D+db,2)                                          # back
        for p,q in ((A,B),(B,C),(C,D),(D,A)): quad(p+dr,q+dr,q+db,p+db,2)     # back box sides
    m2=bpy.data.meshes.new(ON); bm.to_mesh(m2); bm.free()
    def mat(name,col,rough,metal=0,alpha=1.0,trans=0):
        m=bpy.data.materials.get(name)
        if m is None:
            m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
            b.inputs['Base Color'].default_value=col; b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
            if trans: b.inputs['Transmission Weight'].default_value=trans; b.inputs['IOR'].default_value=1.45
        return m
    m2.materials.append(mat('PS_precast_reveal_tan_UNVERIFIED',(0.55,0.47,0.36,1),0.8))
    m2.materials.append(mat('PS_slot_glass_tinted_UNVERIFIED',(0.20,0.24,0.26,1),0.05,0,1,0.85))
    m2.materials.append(mat('PS_slot_interior_dark_UNVERIFIED',(0.035,0.033,0.03,1),0.9))
    o=bpy.data.objects.new(ON,m2); w.users_collection[0].objects.link(o); print('PS_REVEALS',len(SL),'col',w.users_collection[0].name)

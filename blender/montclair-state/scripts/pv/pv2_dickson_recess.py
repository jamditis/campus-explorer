# pv2 (Nov 1 2026): Dickson window slots behind the pu frames become REAL recessed openings. ALL UNVERIFIED.
# 'Dickson Hall walls' faces are cut open exactly at the inner edge of each pu frame (same facade-UV slot maths as
# pu_dickson_frames: bay 2.4 m, window u 0.5-1.9, v 4.6*js+1.0..3.6, same corner/clipped skips), and
# PV2_Dickson_window_reveals_glass_UNVERIFIED adds 4 buff reveal liners 0.20 m deep, a glass pane set back 0.10 m and a dark
# interior back box up to 0.6 m in (ray-clamped near corners) (single-sided LiDAR shell never shows through). The pu centre mullion + hopper transom
# (the boxes 3.6 cm thick) are moved back 0.12 m so they sit on the set-back glass instead of floating at the face.
# Original meshes kept as fake-user 'PV2_backup_Dickson_walls' / 'PV2_backup_PU_frames'; REVERT=1 restores both exactly.
import bpy, bmesh, os, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; ON='PV2_Dickson_window_reveals_glass_UNVERIFIED'
BKW='PV2_backup_Dickson_walls'; BKF='PV2_backup_PU_frames'
w=bpy.data.objects['Dickson Hall walls']; me=w.data
fo=bpy.data.objects['PU_Dickson_window_frames_UNVERIFIED']; fme=fo.data
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m2=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m2); print('REVERTED_PV2_REVEALS')
for BK,M in ((BKW,me),(BKF,fme)):
    if BK in bpy.data.meshes:
        bk=bpy.data.meshes[BK]; bm=bmesh.new(); bm.from_mesh(bk); bm.to_mesh(M); bm.free(); M.update()
        bpy.data.meshes.remove(bk); print('REVERTED_PV2',BK,len(M.vertices))
if not REV:
    bk=me.copy(); bk.name=BKW; bk.use_fake_user=True
    bk2=fme.copy(); bk2.name=BKF; bk2.use_fake_user=True
    mw=w.matrix_world; uv=me.uv_layers['facade'].data
    WT=float(w.get('win_top',99.0))
    FS=[]
    for p in me.polygons:
        n=-(mw.to_3x3()@p.normal)
        if abs(n.z)>0.1 or p.area<1: continue
        c=mw@p.center
        if c.x>-134.0: continue
        n.z=0; n.normalize()
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
    UMIN=min(F['umin'] for F in FS); UMAX=max(F['umax'] for F in FS); SL=[]
    for kb in range(math.floor(UMIN/2.4)-1,math.ceil(UMAX/2.4)+1):
        u0=2.4*kb+0.5; u1=u0+1.4; uc=(u0+u1)/2
        ov=[F for F in FS if F['umax']>u0-0.07 and F['umin']<u1+0.07]
        if not ov: continue
        if min(F['umin'] for F in ov)>u0-0.07 or max(F['umax'] for F in ov)<u1+0.07: continue
        if any(F['n'].dot(ov[0]['n'])<0.985 for F in ov): continue
        host=[F for F in ov if F['umin']<=uc<=F['umax']]
        if not host: continue
        F=host[0]; vmx=min(G['vmax'] for G in ov)-0.15; vmn=max(G['vmin'] for G in ov)
        for js in range(0,6):
            v0=max(4.6*js+1.0,0.8); v1=4.6*js+3.6
            if v1>min(WT,vmx): continue
            if v0<vmn+0.1: continue
            SL.append(dict(u0=u0,u1=u1,v0=v0,v1=v1,F=F,faces=[G['idx'] for G in ov]))
    print('PV2_slots',len(SL))
    bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    src=bm.faces.layers.int.new('pv2_src')
    for f in bm.faces: f[src]=f.index
    uvL=bm.loops.layers.uv['facade']; imw=mw.inverted(); byface={}
    for s in SL:
        for fi in s['faces']: byface.setdefault(fi,[]).append(s)
    FD={G['idx']:G for G in FS}
    def uvof(S,c):   # world point -> facade (u,v) with the slot's own host-face affine map (same map as the pu frames)
        F=S['F']; d=c-F['P0']; a=F['Wu']; b=F['Wv']
        aa=a.dot(a); ab=a.dot(b); bb=b.dot(b); da=d.dot(a); db_=d.dot(b); det=aa*bb-ab*ab
        return F['U0'].x+(da*bb-db_*ab)/det, F['U0'].y+(db_*aa-da*ab)/det
    for fi,ss in byface.items():
        for S in ss:
            F=S['F']; f=lambda u,v: F['P0']+F['Wu']*(u-F['U0'].x)+F['Wv']*(v-F['U0'].y)
            for kind,val in (('u',S['u0']),('u',S['u1']),('v',S['v0']),('v',S['v1'])):
                fs=[x for x in bm.faces if x[src]==fi]
                geom=list(fs)+list({e for x in fs for e in x.edges})+list({v for x in fs for v in x.verts})
                if kind=='u': co=imw@f(val,F['U0'].y); no=(imw.to_3x3()@F['Wv'].cross(F['n'])).normalized()
                else: co=imw@f(F['U0'].x,val); no=(imw.to_3x3()@F['Wu'].cross(F['n'])).normalized()
                bmesh.ops.bisect_plane(bm,geom=geom,dist=0.0005,plane_co=co,plane_no=no)
    dele=[]
    for x in bm.faces:
        if x[src] not in byface: continue
        c=mw@x.calc_center_median()
        for S in byface[x[src]]:
            u,v=uvof(S,c)
            if S['u0']<u<S['u1'] and S['v0']<v<S['v1']: dele.append(x); break
    bmesh.ops.delete(bm,geom=dele,context='FACES_ONLY')
    bm.faces.layers.int.remove(src); bm.to_mesh(me); bm.free(); me.update(); print('PV2_cut cells',len(dele),'V',len(me.vertices))
    # move pu mullions/transoms (3.6 cm thick boxes) back onto the glass plane
    fmw=fo.matrix_world; ifm=fmw.inverted(); nm=0
    V=fme.vertices
    for b in range(len(V)//8):
        a=fmw@V[8*b].co; c=fmw@V[8*b+1].co; d=c-a
        if abs(d.length-0.036)<0.002:
            sh=ifm.to_3x3()@(-d.normalized()*0.12)
            for t in range(8): V[8*b+t].co+=sh
            nm+=1
    fme.update(); print('PV2_mullions_moved',nm)
    # clamp depths per slot: ray-cast inward from the opening's corners/centre so the back box never pokes through an
    # adjacent (perpendicular) Dickson wall near a building corner (BVH of the cut wall mesh only)
    from mathutils.bvhtree import BVHTree
    bvh=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); nclamp=0
    for s in SL:
        F=s['F']; n=F['n']; f=lambda u,v: F['P0']+F['Wu']*(u-F['U0'].x)+F['Wv']*(v-F['U0'].y); dmin=0.6
        for u,v in ((s['u0']+0.03,s['v0']+0.03),(s['u1']-0.03,s['v0']+0.03),(s['u1']-0.03,s['v1']-0.03),(s['u0']+0.03,s['v1']-0.03),((s['u0']+s['u1'])/2,(s['v0']+s['v1'])/2)):
            o=f(u,v)-n*0.002
            pp,_,_,dd=bvh.ray_cast(o,-n,0.7)
            if pp is not None: dmin=min(dmin,dd)
        s['D']=max(0.08,dmin-0.03); nclamp+=s['D']<0.57
    print('PV2_depth_clamped',nclamp,'min',round(min(s['D'] for s in SL),3))
    bm=bmesh.new()
    def quad(a,b,c,d,mi): bm.faces.new([bm.verts.new(a),bm.verts.new(b),bm.verts.new(c),bm.verts.new(d)]).material_index=mi
    for s in SL:
        F=s['F']; n=F['n']; f=lambda u,v: F['P0']+F['Wu']*(u-F['U0'].x)+F['Wv']*(v-F['U0'].y)
        A=f(s['u0'],s['v0']); B=f(s['u1'],s['v0']); C=f(s['u1'],s['v1']); D=f(s['u0'],s['v1'])
        DD=s['D']; dr=-n*min(0.20,DD-0.02); dg=-n*min(0.10,DD*0.45); db=-n*DD
        for p,q in ((A,B),(B,C),(C,D),(D,A)): quad(p,q,q+dr,p+dr,0)
        quad(A+dg,B+dg,C+dg,D+dg,1)
        quad(A+db,B+db,C+db,D+db,2)
        for p,q in ((A,B),(B,C),(C,D),(D,A)): quad(p+dr,q+dr,q+db,p+db,2)
    m2=bpy.data.meshes.new(ON); bm.to_mesh(m2); bm.free()
    def mat(name,col,rough,trans=0):
        m=bpy.data.materials.get(name)
        if m is None:
            m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
            b.inputs['Base Color'].default_value=col; b.inputs['Roughness'].default_value=rough
            if trans: b.inputs['Transmission Weight'].default_value=trans; b.inputs['IOR'].default_value=1.45
        return m
    m2.materials.append(mat('PV2_reveal_buff_UNVERIFIED',(0.52,0.42,0.30,1),0.85))
    m2.materials.append(bpy.data.materials.get('PS_slot_glass_tinted_UNVERIFIED') or mat('PV2_glass_UNVERIFIED',(0.2,0.24,0.26,1),0.05,0.85))
    m2.materials.append(bpy.data.materials.get('PS_slot_interior_dark_UNVERIFIED') or mat('PV2_interior_UNVERIFIED',(0.035,0.033,0.03,1),0.9))
    o=bpy.data.objects.new(ON,m2); o['source_note']='UNVERIFIED: openings = pu frame inner edges; depths/colours invented (pv2, Nov 1 2026)'
    w.users_collection[0].objects.link(o); print('PV2_REVEALS',len(SL),'col',w.users_collection[0].name)

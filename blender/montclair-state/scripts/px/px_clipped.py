# px (Nov 2 2026): now that the wing wall tops reach the level parapet (px_parapet), the 26 top-row Dickson slots that the
# old sloped LiDAR wall top clipped (pv_clipped: short frames + brick cards) become FULL-HEIGHT real recessed openings
# consistent with pv2: same slot maths (bay 2.4 m, u 0.5-1.9, v 4.6*js+1.0..3.6, from the pre-pv2 wall faces kept in
# PV2_backup_Dickson_walls), wall + parapet infill cut in world space through the slot's host-face map, buff reveals 0.20 m,
# Dickson clearer glass set back 0.10 m, dark back box (ray-clamped), maroon frame + sill at the face, centre mullion and
# hopper transom on the glass. PV_Dickson_clipped_slot_frames_UNVERIFIED hidden. ALL UNVERIFIED.
# REVERT=1 restores walls + infill from fake-user backups, unhides the pv object, removes the new object.
import bpy, bmesh, os, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; ON='PX_Dickson_fullheight_toprow_windows_UNVERIFIED'
INF='PX_Dickson_wing_parapet_infill_UNVERIFIED'; BKW='PX_backup_Dickson_walls'; BKI='PX_backup_parapet_infill'
w=bpy.data.objects['Dickson Hall walls']; me=w.data; pvo=bpy.data.objects['PV_Dickson_clipped_slot_frames_UNVERIFIED']
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m2=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m2); print('REVERTED_PX_WINDOWS')
for BK,M in ((BKW,me),(BKI,bpy.data.objects[INF].data if INF in bpy.data.objects else None)):
    if BK in bpy.data.meshes:
        bk=bpy.data.meshes[BK]
        if M is not None: bm=bmesh.new(); bm.from_mesh(bk); bm.to_mesh(M); bm.free(); M.update()
        bpy.data.meshes.remove(bk); print('REVERTED_PX',BK)
if 'px_prev_hide' in pvo:
    pvo.hide_render,pvo.hide_viewport=[bool(x) for x in pvo['px_prev_hide']]; del pvo['px_prev_hide']; print('REVERTED_PX_PVHIDE')
if not REV:
    inf=bpy.data.objects[INF]; ime=inf.data
    bk=me.copy(); bk.name=BKW; bk.use_fake_user=True; bk2=ime.copy(); bk2.name=BKI; bk2.use_fake_user=True
    src=bpy.data.meshes['PV2_backup_Dickson_walls']; mw=w.matrix_world; uv=src.uv_layers['facade'].data
    WT=float(w.get('win_top',99.0)); FS=[]
    for p in src.polygons:
        n=-(mw.to_3x3()@p.normal)
        if abs(n.z)>0.1 or p.area<1: continue
        c=mw@p.center
        if c.x>-134.0: continue
        n.z=0; n.normalize(); L=list(p.loop_indices)
        P=[mw@src.vertices[src.loops[l].vertex_index].co for l in L]; U=[uv[l].uv.copy() for l in L]; best=None
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
        FS.append(dict(umin=min(q.x for q in U),umax=max(q.x for q in U),vmin=min(q.y for q in U),vmax=max(q.y for q in U),P0=P[i],U0=U[i].copy(),Wu=Wu,Wv=Wv,n=n))
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
            v0=max(4.6*js+1.0,0.8); v1=4.6*js+3.6; TOP=min(WT,vmx+0.15)
            if v1<=min(WT,vmx): continue
            if v0>=TOP: continue
            if v0<vmn+0.1: continue
            if v1>WT: continue
            SL.append(dict(u0=u0,u1=u1,v0=v0,v1=v1,F=F))
    def fmap(F,u,v): return F['P0']+F['Wu']*(u-F['U0'].x)+F['Wv']*(v-F['U0'].y)
    def uvof(F,c):
        d=c-F['P0']; a=F['Wu']; b=F['Wv']; aa=a.dot(a); ab=a.dot(b); bb=b.dot(b); da=d.dot(a); db_=d.dot(b); det=aa*bb-ab*ab
        return F['U0'].x+(da*bb-db_*ab)/det, F['U0'].y+(db_*aa-da*ab)/det, d.dot(F['n'])
    # keep only slots inside the parapet wing whose full head now lies under the level parapet top
    ZT=max((inf.matrix_world@v.co).z for v in ime.vertices)
    SL=[s for s in SL if fmap(s['F'],(s['u0']+s['u1'])/2,s['v1']).z<ZT-0.4]
    print('PX_slots',len(SL),'ZT',round(ZT,2))
    ncut={}
    for ob in (w,inf):
        M=ob.data; omw=ob.matrix_world; imw=omw.inverted(); bm=bmesh.new(); bm.from_mesh(M); tot=0
        for s in SL:
            F=s['F']
            def near(x):
                u,v,d=uvof(F,omw@x.calc_center_median()); return abs(d)<0.25 and s['u0']-1.2<u<s['u1']+1.2 and s['v0']-1.2<v<s['v1']+1.2
            for kind,val in (('u',s['u0']),('u',s['u1']),('v',s['v0']),('v',s['v1'])):
                bm.faces.ensure_lookup_table(); fs=[x for x in bm.faces if near(x)]
                if not fs: continue
                geom=fs+list({e for x in fs for e in x.edges})+list({v for x in fs for v in x.verts})
                if kind=='u': co=imw@fmap(F,val,F['U0'].y); no=(imw.to_3x3()@F['Wv'].cross(F['n'])).normalized()
                else: co=imw@fmap(F,F['U0'].x,val); no=(imw.to_3x3()@F['Wu'].cross(F['n'])).normalized()
                bmesh.ops.bisect_plane(bm,geom=geom,dist=0.0005,plane_co=co,plane_no=no)
            dele=[]
            for x in bm.faces:
                u,v,d=uvof(F,omw@x.calc_center_median())
                if abs(d)<0.25 and s['u0']<u<s['u1'] and s['v0']<v<s['v1']: dele.append(x)
            bmesh.ops.delete(bm,geom=dele,context='FACES_ONLY'); tot+=len(dele)
        bm.to_mesh(M); bm.free(); M.update(); ncut[ob.name]=tot
    print('PX_cut',ncut)
    from mathutils.bvhtree import BVHTree
    bvh=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
    bm=bmesh.new()
    def quad(a,b,c,d,mi): bm.faces.new([bm.verts.new(a),bm.verts.new(b),bm.verts.new(c),bm.verts.new(d)]).material_index=mi
    def box(c,ex,ey,ez,mi):
        vs=[bm.verts.new(c+ex*sx+ey*sy+ez*sz) for sx in (-1,1) for sy in (-1,1) for sz in (-1,1)]
        for q in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]: bm.faces.new([vs[i] for i in q]).material_index=mi
    for s in SL:
        F=s['F']; n=F['n']; f=lambda u,v: fmap(F,u,v); u0,u1,v0,v1=s['u0'],s['u1'],s['v0'],s['v1']; uc=(u0+u1)/2; dmin=0.6
        for u,v in ((u0+0.03,v0+0.03),(u1-0.03,v0+0.03),(u1-0.03,v1-0.03),(u0+0.03,v1-0.03),(uc,(v0+v1)/2)):
            pp,_,_,dd=bvh.ray_cast(f(u,v)-n*0.002,-n,0.7)
            if pp is not None: dmin=min(dmin,dd)
        DD=max(0.08,dmin-0.03)
        A=f(u0,v0); B=f(u1,v0); C=f(u1,v1); D=f(u0,v1); dr=-n*min(0.20,DD-0.02); dg=-n*min(0.10,DD*0.45); db=-n*DD
        for p,q in ((A,B),(B,C),(C,D),(D,A)): quad(p,q,q+dr,p+dr,0)
        quad(A+dg,B+dg,C+dg,D+dg,1); quad(A+db,B+db,C+db,D+db,2)
        for p,q in ((A,B),(B,C),(C,D),(D,A)): quad(p+dr,q+dr,q+db,p+db,2)
    for s in SL:   # frames after all opening quads (first 40 verts/slot = PV2 layout, read by px_blinds)
        F=s['F']; n=F['n']; f=lambda u,v: fmap(F,u,v); u0,u1,v0,v1=s['u0'],s['u1'],s['v0'],s['v1']; uc=(u0+u1)/2
        eu=F['Wu'].normalized(); ev=F['Wv'].normalized()
        def fr(ua,ub,va,vb,d,mi,back=0.0):
            cc=f((ua+ub)/2,(va+vb)/2)+n*(d-back); box(cc,eu*(abs(ub-ua)/2),ev*(abs(vb-va)/2),n*d,mi)
        fw=0.06; h=0.025
        fr(u0-fw,u0,v0-fw,v1+fw,h,3); fr(u1,u1+fw,v0-fw,v1+fw,h,3); fr(u0,u1,v1,v1+fw,h,3); fr(u0,u1,v0-fw,v0,h,3)
        fr(uc-0.025,uc+0.025,v0,v1,0.018,3,0.12); tv=v0+0.85; fr(u0,u1,tv-0.025,tv+0.025,0.018,3,0.12)
        fr(u0-0.1,u1+0.1,v0-fw-0.08,v0-fw,0.035,4)
    m2=bpy.data.meshes.new(ON); bm.to_mesh(m2); bm.free()
    gl=bpy.data.materials.get('PW_Dickson_glass_clearer_UNVERIFIED') or bpy.data.materials['PS_slot_glass_tinted_UNVERIFIED']
    for mn in ('PV2_reveal_buff_UNVERIFIED',gl.name,'PS_slot_interior_dark_UNVERIFIED','Window_Frame_Maroon_Feliciano','North_Feliciano_sill_tan'):
        m2.materials.append(bpy.data.materials[mn])
    o=bpy.data.objects.new(ON,m2); o['source_note']='UNVERIFIED (px, Nov 2 2026): full-height recessed top-row windows where the old sloped LiDAR wall top clipped the slots (pv_clipped); sizes/colours copied from pu/pv2'
    w.users_collection[0].objects.link(o); o['px_nslots']=len(SL)
    pvo['px_prev_hide']=[int(pvo.hide_render),int(pvo.hide_viewport)]; pvo.hide_render=True; pvo.hide_viewport=True
    print('PX_WINDOWS',len(SL),'polys',len(m2.polygons))

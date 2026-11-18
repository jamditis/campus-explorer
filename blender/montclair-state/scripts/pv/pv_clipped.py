# pv: Dickson shader slots clipped at the top (pu skipped 26 'clipped_top_skips', mostly the north-wing 3rd row) get the
# same maroon frame/mullion/transom/sill as pu, with the head frame at the clip line, so they read as shorter windows.
# Slots shorter than PV_MINH (default 1.0 m) are covered by a thin brick card instead. ALL UNVERIFIED. REVERT=1 removes the object.
import bpy, bmesh, os, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; ON='PV_Dickson_clipped_slot_frames_UNVERIFIED'
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me); print('REVERTED_PV_CLIPPED')
if not REV:
    w=bpy.data.objects['Dickson Hall walls']; me=w.data; mw=w.matrix_world; uv=me.uv_layers['facade'].data
    cen=sum((mw@v.co for v in me.vertices),Vector())/len(me.vertices)
    WT=float(w.get('win_top',99.0))
    bm=bmesh.new(); nslot=0; agree=0
    def box(c,ex,ey,ez,mi):
        vs=[bm.verts.new(c+ex*sx+ey*sy+ez*sz) for sx in (-1,1) for sy in (-1,1) for sz in (-1,1)]
        for q in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]: bm.faces.new([vs[i] for i in q]).material_index=mi
    FS=[]
    for p in me.polygons:
        n=-(mw.to_3x3()@p.normal)            # wall mesh normals point inward -> outward = -normal
        if abs(n.z)>0.1 or p.area<1: continue
        c=mw@p.center
        if c.x>-134.0: continue               # east face: covered by the pe skin with its own 3D windows
        n.z=0; n.normalize(); agree+=(c-cen).dot(n)>0
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
        FS.append(dict(UVP=[(q.x,q.y) for q in U],umin=min(q.x for q in U),umax=max(q.x for q in U),vmin=min(q.y for q in U),vmax=max(q.y for q in U),P0=P[i],U0=U[i].copy(),Wu=Wu,Wv=Wv,n=n))
    print('PU_faces',len(FS),'outward_agree_centroid',agree)
    HS=[]; CS=[]; CARDS=[]; nstub=0; ntri=0; MINH=float(os.environ.get('PV_MINH','1.0'))
    UMIN=min(F['umin'] for F in FS); UMAX=max(F['umax'] for F in FS); skipc=0; skipt=0
    for kb in range(math.floor(UMIN/2.4)-1,math.ceil(UMAX/2.4)+1):
        u0=2.4*kb+0.5; u1=u0+1.4; uc=(u0+u1)/2
        ov=[F for F in FS if F['umax']>u0-0.07 and F['umin']<u1+0.07]
        if not ov: continue
        if min(F['umin'] for F in ov)>u0-0.07 or max(F['umax'] for F in ov)<u1+0.07: continue
        if any(F['n'].dot(ov[0]['n'])<0.985 for F in ov): skipc+=1; continue
        host=[F for F in ov if F['umin']<=uc<=F['umax']]
        if not host: continue
        F=host[0]; vmx=min(G['vmax'] for G in ov)-0.15; vmn=max(G['vmin'] for G in ov)
        f=lambda u,v,F=F: F['P0']+F['Wu']*(u-F['U0'].x)+F['Wv']*(v-F['U0'].y)
        n=F['n']; eu=F['Wu'].normalized(); ev=F['Wv'].normalized()
        for js in range(0,6):
            v0=max(4.6*js+1.0,0.8); v1=4.6*js+3.6
            TOP=min(WT,vmx+0.15)
            if v1<=min(WT,vmx): continue                              # full slot: already framed by pu
            if v0>=TOP: continue
            if v0<vmn+0.1: continue
            hgt=TOP-v0; HS.append(round(hgt,2))
            if hgt<MINH:                                              # stub too short to read as a window: brick it over
                ua,ub,va,vb=u0-0.05,u1+0.05,v0-0.02,TOP+0.02; q=[]
                for (uu,vv) in ((ua,va),(ub,va),(ub,vb),(ua,vb)): q.append(bm.verts.new(f(uu,vv)+n*0.006))
                fc=bm.faces.new(q); fc.material_index=2; CARDS.append((fc,[(ua,4.6*js+3.7),(ub,4.6*js+3.7),(ub,4.6*js+3.7+vb-va),(ua,4.6*js+3.7+vb-va)]))
                nstub+=1; CS.append(('stub',)+tuple(round(x,1) for x in f(uc,v0))); continue
            # glass above the head where the wall top slopes: brick card = (face UV polygon) ∩ (slot rect, v >= TOP-0.01)
            for G in ov:
                poly=G['UVP']
                for (ax,sgn,val) in ((0,1,u0-0.05),(0,-1,u1+0.05),(1,1,TOP-0.01)):
                    out=[]
                    for i_ in range(len(poly)):
                        A_=poly[i_]; B_=poly[(i_+1)%len(poly)]
                        ina=sgn*(A_[ax]-val)>=0; inb=sgn*(B_[ax]-val)>=0
                        if ina: out.append(A_)
                        if ina!=inb:
                            t_=(val-A_[ax])/(B_[ax]-A_[ax]); out.append((A_[0]+t_*(B_[0]-A_[0]),A_[1]+t_*(B_[1]-A_[1])))
                    poly=out
                    if len(poly)<3: break
                if len(poly)<3: continue
                ar=0.5*abs(sum(poly[i_][0]*poly[(i_+1)%len(poly)][1]-poly[(i_+1)%len(poly)][0]*poly[i_][1] for i_ in range(len(poly))))
                if ar<0.005: continue
                g=lambda u,v,G=G: G['P0']+G['Wu']*(u-G['U0'].x)+G['Wv']*(v-G['U0'].y)
                q=[bm.verts.new(g(uu,vv)+G['n']*0.006) for (uu,vv) in poly]
                try: fc=bm.faces.new(q)
                except ValueError: continue
                fc.material_index=2; CARDS.append((fc,[(uu,4.6*js+3.7+(vv-v0)) for (uu,vv) in poly])); ntri+=1
            v1=TOP-0.06; skipt+=1; CS.append(tuple(round(x,1) for x in f(uc,(v0+v1)/2)))
            def fr(ua,ub,va,vb,d,mi):
                cc=f((ua+ub)/2,(va+vb)/2)+n*d
                box(cc,eu*(abs(ub-ua)/2),ev*(abs(vb-va)/2),n*d,mi)
            fw=0.06; h=0.025
            fr(u0-fw,u0,v0-fw,v1+fw,h,0); fr(u1,u1+fw,v0-fw,v1+fw,h,0)
            fr(u0,u1,v1,v1+fw,h,0); fr(u0,u1,v0-fw,v0,h,0)
            fr(uc-0.025,uc+0.025,v0,v1,0.018,0)                       # centre mullion
            tv=v0+0.85
            if v1-v0>1.3: fr(u0,u1,tv-0.025,tv+0.025,0.018,0)          # hopper transom (only if the slot is tall enough)
            fr(u0-0.1,u1+0.1,v0-fw-0.08,v0-fw,0.035,1)                 # sill
            nslot+=1
    print('PV_CLIPPED framed',skipt,'top_cards',ntri,'stubs_bricked',nstub,'heights',sorted(HS)); print('PV_CENTRES',CS)
    uvl=bm.loops.layers.uv.new('facade')
    for fc,uvs in CARDS:
        if fc.normal.dot(n)<0: pass
        for lp,(uu,vv) in zip(fc.loops,uvs): lp[uvl].uv=(uu,vv)
    bm.normal_update()
    for fc,uvs in CARDS:
        pass
    me2=bpy.data.meshes.new(ON); bm.to_mesh(me2); bm.free()
    me2.materials.append(bpy.data.materials['Window_Frame_Maroon_Feliciano'])
    me2.materials.append(bpy.data.materials.get('North_Feliciano_sill_tan') or bpy.data.materials['Window_Frame_Maroon_Feliciano'])
    me2.materials.append(bpy.data.materials['PE_Dickson_brick_buff_no_red_spandrel_UNVERIFIED'])
    o=bpy.data.objects.new(ON,me2); o['source_note']='UNVERIFIED (pv, Nov 1 2026): frames on the shader-clipped top-row Dickson slots (head at the clip line); stubs <MINH bricked over with a brick-facade card'
    col=w.users_collection[0]; col.objects.link(o); print('PV_CLIPPED_OBJ',nslot,len(me2.polygons),'col',col.name)

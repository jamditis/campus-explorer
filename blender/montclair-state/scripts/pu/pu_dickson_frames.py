# pu: Dickson Hall shader windows (west/south/north walls; east face is the pe brick skin) get 3D frames on top of the
# shader slots of PE_Dickson_brick_buff_no_red_spandrel_UNVERIFIED (facade UV in metres: window u 0.5-1.9 of a 2.4 m bay,
# v 1.0-3.6 of each 4.6 m storey band, v>0.8 and v<win_top). Maroon frame 6 cm / 2.5 cm proud (matches the pe east
# windows' Window_Frame_Maroon_Feliciano), centre mullion + hopper transom at 0.85 m, cast-stone sill 6 cm proud.
# Slot positions follow the shader exactly; frame/mullion/transom/sill sizes UNVERIFIED (mref_04 shows the east face only).
# REVERT=1 removes the object.
import bpy, bmesh, os, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; ON='PU_Dickson_window_frames_UNVERIFIED'
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me); print('REVERTED_PU_FRAMES')
_w=bpy.data.objects['Dickson Hall walls']
if 'pu_prev_win_top' in _w:                      # west/south top strip: restore the shader's window ceiling
    _w['win_top']=_w['pu_prev_win_top']; del _w['pu_prev_win_top']; print('REVERTED_PU_WINTOP',_w['win_top'])
if not REV:
    # Top strip (UNVERIFIED): the shader's 4th window row (v 14.8-17.4) was cut by win_top 15.98 / the wall top into
    # 0.3-1.2 m stubs along the west/south top; lower the ceiling to 14.3 so that band reads as plain brick under the coping.
    _w['pu_prev_win_top']=float(_w['win_top']); _w['win_top']=14.3; print('PU_WINTOP',_w['pu_prev_win_top'],'->',14.3)
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
        FS.append(dict(umin=min(q.x for q in U),umax=max(q.x for q in U),vmin=min(q.y for q in U),vmax=max(q.y for q in U),P0=P[i],U0=U[i].copy(),Wu=Wu,Wv=Wv,n=n))
    print('PU_faces',len(FS),'outward_agree_centroid',agree)
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
            if v1>min(WT,vmx): skipt+= v0<min(WT,vmx); continue     # shader-clipped top-row slot: no frame (not a full window)
            if v0<vmn+0.1: continue
            def fr(ua,ub,va,vb,d,mi):
                cc=f((ua+ub)/2,(va+vb)/2)+n*d
                box(cc,eu*(abs(ub-ua)/2),ev*(abs(vb-va)/2),n*d,mi)
            fw=0.06; h=0.025
            fr(u0-fw,u0,v0-fw,v1+fw,h,0); fr(u1,u1+fw,v0-fw,v1+fw,h,0)
            fr(u0,u1,v1,v1+fw,h,0); fr(u0,u1,v0-fw,v0,h,0)
            fr(uc-0.025,uc+0.025,v0,v1,0.018,0)                       # centre mullion
            tv=v0+0.85; fr(u0,u1,tv-0.025,tv+0.025,0.018,0)            # hopper transom
            fr(u0-0.1,u1+0.1,v0-fw-0.08,v0-fw,0.035,1)                 # sill
            nslot+=1
    print('PU_FRAMES corner_skips',skipc,'clipped_top_skips',skipt)
    me2=bpy.data.meshes.new(ON); bm.to_mesh(me2); bm.free()
    me2.materials.append(bpy.data.materials['Window_Frame_Maroon_Feliciano'])
    me2.materials.append(bpy.data.materials.get('North_Feliciano_sill_tan') or bpy.data.materials['Window_Frame_Maroon_Feliciano'])
    o=bpy.data.objects.new(ON,me2); o['source_note']='UNVERIFIED: positions = Dickson facade shader slots; sizes/colours invented (pu, Nov 1 2026)'
    col=w.users_collection[0]; col.objects.link(o); print('PU_FRAMES',nslot,'col',col.name)

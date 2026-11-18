# pr: Calcia slot windows get 3D surrounds on top of pe's shader slots (facade UV in metres: slot x 0.75-1.65 of a 2.4 m bay,
# y 0.7-3.9 of each 4.4 m storey band, above 0.8 m and below the per-vertex 'win_top'): dark bronze frame (5 cm, 2.5 cm proud),
# one horizontal transom bar at 1/3 height, precast sill 6 cm proud. Slot positions follow the shader exactly; sizes/frame
# colours UNVERIFIED (refs calcia_web_05/07 show narrow vertical slots, no frame detail). REVERT=1 removes the object.
import bpy, bmesh, os
from mathutils import Vector, Matrix
REV=os.environ.get('REVERT')=='1'; ON='PR_Calcia_slot_surrounds_UNVERIFIED'
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; me=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me); print('REVERTED_PR_SLOTS')
if not REV:
    w=bpy.data.objects['Calcia Hall walls']; me=w.data; mw=w.matrix_world; uv=me.uv_layers['facade'].data
    wt=me.attributes.get('win_top')
    cen=sum((mw@v.co for v in me.vertices),Vector())/len(me.vertices)
    bm=bmesh.new(); nslot=0
    def box(c,ex,ey,ez,mi):
        vs=[bm.verts.new(c+ex*sx+ey*sy+ez*sz) for sx in (-1,1) for sy in (-1,1) for sz in (-1,1)]
        for q in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]: bm.faces.new([vs[i] for i in q]).material_index=mi
    import math
    FS=[]
    for p in me.polygons:
        n=(mw.to_3x3()@p.normal)
        if abs(n.z)>0.1 or p.area<1: continue
        n.z=0; n.normalize()
        c=mw@p.center
        if (c-cen).dot(n)<0: n=-n          # outward
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
    WT=float(w.get('win_top',99.0))
    UMIN=min(F['umin'] for F in FS); UMAX=max(F['umax'] for F in FS); skipc=0
    for kb in range(math.floor(UMIN/2.4)-1,math.ceil(UMAX/2.4)+1):
        u0=2.4*kb+0.75; u1=u0+0.9; uc=(u0+u1)/2
        ov=[F for F in FS if F['umax']>u0-0.06 and F['umin']<u1+0.06]
        if not ov: continue
        if min(F['umin'] for F in ov)>u0-0.06 or max(F['umax'] for F in ov)<u1+0.06: continue   # slot runs off the wall end
        if any(F['n'].dot(ov[0]['n'])<0.985 for F in ov): skipc+=1; continue                     # straddles a corner
        host=[F for F in ov if F['umin']<=uc<=F['umax']]
        if not host: continue
        F=host[0]; vmx=min(G['vmax'] for G in ov)-0.12; vmn=max(G['vmin'] for G in ov)
        f=lambda u,v,F=F: F['P0']+F['Wu']*(u-F['U0'].x)+F['Wv']*(v-F['U0'].y)
        n=F['n']; eu=F['Wu'].normalized(); ev=F['Wv'].normalized()
        for js in range(0,8):
            v0=max(0.1+4.4*js+0.6,0.8); v1=min(0.1+4.4*js+3.8,WT,vmx)
            if v1-v0<1.0 or v0<vmn+0.1: continue
            def fr(ua,ub,va,vb,d,mi):
                cc=f((ua+ub)/2,(va+vb)/2)+n*d
                box(cc,eu*(abs(ub-ua)/2),ev*(abs(vb-va)/2),n*d,mi)
            fw=0.05; h=0.025
            fr(u0-fw,u0,v0-fw,v1+fw,h,0); fr(u1,u1+fw,v0-fw,v1+fw,h,0)
            fr(u0,u1,v1,v1+fw,h,0); fr(u0,u1,v0-fw,v0,h,0)
            tv=v0+(v1-v0)/3; fr(u0,u1,tv-0.02,tv+0.02,0.015,0)
            fr(u0-0.08,u1+0.08,v0-fw-0.07,v0-fw,0.03,1)
            nslot+=1
    print('PR_SLOTS_corner_skips',skipc,'faces',len(FS))
    me2=bpy.data.meshes.new(ON); bm.to_mesh(me2); bm.free()
    me2.materials.append(bpy.data.materials['PE_Dickson_coping_dark_bronze_UNVERIFIED'])
    sm=bpy.data.materials.get('North_Feliciano_sill_tan') or bpy.data.materials['PE_Dickson_coping_dark_bronze_UNVERIFIED']
    me2.materials.append(sm)
    o=bpy.data.objects.new(ON,me2)
    col=w.users_collection[0]; col.objects.link(o); print('PR_SLOTS',nslot,'col',col.name)

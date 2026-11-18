# px (Nov 2 2026): Dickson west/"north" wing wall tops (LiDAR-derived, sloping 148.5-151.3 m) are brought up to a LEVEL
# parapet line ZT=151.30 m (the highest existing level top at the wing's south end) by a brick infill object
# PX_Dickson_wing_parapet_infill_UNVERIFIED built on every true wall-top edge in the wing (x<-157.5, 77<y<160.5).
# Brick UV continues the host wall face's own facade-UV affine map (courses line up). The coping strips that sat on the
# old sloped tops (Roof_coping / ek caps / el strips for Dickson) are lifted by the same local dz so they cap the new top.
# Replaces the pv_pent stop-gap visually (Roof_pent's box top 151.02 is now below the parapet). ALL UNVERIFIED.
# REVERT=1 removes the infill and restores the coping vertices exactly (orig coords stored as object props).
import bpy, bmesh, os, math, collections
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; ON='PX_Dickson_wing_parapet_infill_UNVERIFIED'; ZT=float(os.environ.get('ZT','151.30'))
COP=[o for o in bpy.data.objects if o.type=='MESH' and (o.name=='Roof_coping' or o.name.startswith('ek coping caps Dickson') or o.name.startswith('el coping strips Dickson'))]
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m2=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m2); print('REVERTED_PX_INFILL')
for o in COP:
    if 'px_idx' in o:
        V=o.data.vertices; I=list(o['px_idx']); C=list(o['px_co'])
        for n,i in enumerate(I): V[i].co=(C[3*n],C[3*n+1],C[3*n+2])
        del o['px_idx']; del o['px_co']; o.data.update(); print('REVERTED_PX_COPING',o.name,len(I))
def inwing(p): return p.x<-157.5 and 77.0<p.y<160.5
if not REV:
    w=bpy.data.objects['Dickson Hall walls']; me=w.data; mw=w.matrix_world; uv=me.uv_layers['facade'].data
    ec=collections.defaultdict(list)
    for p in me.polygons:
        for k in p.edge_keys: ec[k].append(p.index)
    WV=[mw@v.co for v in me.vertices]
    from mathutils.kdtree import KDTree
    kd=KDTree(len(WV))
    for i,c in enumerate(WV): kd.insert(Vector((c.x,c.y,0)),i)
    kd.balance()
    def affine(p):
        L=list(p.loop_indices); P=[WV[me.loops[l].vertex_index] for l in L]; U=[uv[l].uv.copy() for l in L]; best=None
        for i in range(len(L)):
            for j in range(i+1,len(L)):
                for k in range(j+1,len(L)):
                    a=U[j]-U[i]; b=U[k]-U[i]; det=a.x*b.y-a.y*b.x
                    if best is None or abs(det)>abs(best[0]): best=(det,i,j,k)
        det,i,j,k=best
        if abs(det)<1e-4: return None
        a=U[j]-U[i]; b=U[k]-U[i]; A=P[j]-P[i]; B=P[k]-P[i]
        return P[i],U[i],(A*b.y-B*a.y)/det,(B*a.x-A*b.x)/det
    def uvof(F,c):
        P0,U0,a,b=F; d=c-P0; aa=a.dot(a); ab=a.dot(b); bb=b.dot(b); da=d.dot(a); db_=d.dot(b); det=aa*bb-ab*ab
        return (U0.x+(da*bb-db_*ab)/det, U0.y+(db_*aa-da*ab)/det)
    bm=bmesh.new(); ul=bm.loops.layers.uv.new('facade'); nq=0; SEG=[]
    for k,fl in ec.items():
        if len(fl)!=1: continue
        a=WV[k[0]]; b=WV[k[1]]
        if (a.xy-b.xy).length<0.05 or min(a.z,b.z)<146 or max(a.z,b.z)>=ZT-0.01: continue
        m=(a+b)/2
        if not inwing(m): continue
        p=me.polygons[fl[0]]
        if (mw@p.center).z>m.z-0.05 and abs((mw.to_3x3()@p.normal).z)<0.3:
            pass
        if (mw@p.center).z>=m.z: continue
        # true top: no wall vertex above within 0.9 m horizontally
        hit=False
        for (co,i,d) in kd.find_range(Vector((m.x,m.y,0)),0.9):
            if WV[i].z>max(a.z,b.z)+0.25: hit=True; break
        if hit: continue
        F=affine(p)
        if F is None: continue
        a2=Vector((a.x,a.y,ZT)); b2=Vector((b.x,b.y,ZT))
        vs=[bm.verts.new(x) for x in (a,b,b2,a2)]
        n=(mw.to_3x3()@p.normal); fn=(b-a).cross(a2-a)
        if fn.dot(n)>0: vs=[vs[1],vs[0],vs[3],vs[2]]   # wall normals point inward -> infill faces outward
        f=bm.faces.new(vs)
        for lp in f.loops: lp[ul].uv=uvof(F,lp.vert.co)
        nq+=1; SEG.append((a,b))
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002)
    m2=bpy.data.meshes.new(ON); bm.to_mesh(m2); bm.free()
    m2.materials.append(bpy.data.materials['PE_Dickson_brick_buff_no_red_spandrel_UNVERIFIED'])
    for pl in m2.polygons: pl.use_smooth=False
    o=bpy.data.objects.new(ON,m2); o['source_note']='UNVERIFIED (px, Nov 2 2026): level parapet infill on the LiDAR-sloped Dickson wing wall tops up to %.2f m; no photo of the roofline'%ZT
    (w.users_collection[0]).objects.link(o)
    print('PX_INFILL quads',nq,'verts',len(m2.vertices),'dz max',round(max(ZT-min(a.z,b.z) for a,b in SEG),2))
    # lift coping verts sitting on the raised tops by the local dz
    def dz_at(c):
        best=None
        for a,b in SEG:
            ab=(b-a).xy; L2=ab.length_squared
            t=0 if L2<1e-9 else max(0,min(1,(c.xy-a.xy).dot(ab)/L2)); q=a.lerp(b,t); d=(c.xy-q.xy).length
            if d<0.75 and -0.35<c.z-q.z<0.6 and (best is None or d<best[0]): best=(d,ZT-q.z)
        return None if best is None else best[1]
    for co in COP:
        V=co.data.vertices; cw=co.matrix_world; icw=cw.inverted(); I=[]; C=[]
        for v in V:
            c=cw@v.co
            if not inwing(c) or c.z<146 or c.z>ZT+0.6: continue
            d=dz_at(c)
            if d is None or d<0.01: continue
            I.append(v.index); C+= [v.co.x,v.co.y,v.co.z]
            v.co=icw@(c+Vector((0,0,d)))
        if I: co['px_idx']=I; co['px_co']=C; co.data.update()
        print('PX_COPING',co.name,len(I))

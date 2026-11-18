# qa (Nov 2 2026): close the two ~0.8 m gaps in the Dickson west-wing parapet chain at the south end (py/pz left open chain
# ends at x -182 y 84.66/85.45 and y ~78.4 x -177.35/-178.20: there the LiDAR wall top was skipped by py's segment filter,
# so the brick stopped at ~151.2-151.3 and coping / back face / membrane / stain all ended). New object only: bridges each
# open end profile of the py raise, py back face + membrane strip, py coping and pz drip stain across the gap (exact end
# vertices, so no hairlines), + a brick sliver from the true wall top up to the 151.30 raise bottom. ALL UNVERIFIED.
import bpy, bmesh, os, collections
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
NAME='QA_Dickson_wing_parapet_south_gap_fill_UNVERIFIED'
if NAME in bpy.data.objects:
    o=bpy.data.objects[NAME]; m=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m); print('REVERTED',NAME)
GAPS=[(Vector((-181.985,85.451)),Vector((-182.042,84.660))),(Vector((-177.350,78.404)),Vector((-178.202,78.465)))]
SRC=[('PY_Dickson_wing_parapet_raise_UNVERIFIED',0.03),('PY_Dickson_wing_parapet_back_roofstrip_UNVERIFIED',0.03),
     ('PY_Dickson_wing_parapet_coping_UNVERIFIED',0.05),('PZ_Dickson_wing_coping_drip_stain_UNVERIFIED',0.03)]
if not REV:
    mats=bpy.data.materials; MAT=[]; 
    def mi(m):
        if m.name not in MAT: MAT.append(m.name)
        return MAT.index(m.name)
    bm=bmesh.new(); ULF=bm.loops.layers.uv.new('facade'); ULU=bm.loops.layers.uv.new('UVMap')
    VC={}
    def V(c):
        k=(round(c.x,4),round(c.y,4),round(c.z,4))
        if k not in VC: VC[k]=bm.verts.new(c)
        return VC[k]
    nf=0
    for A,B in GAPS:
        t=(B-A).normalized(); n=Vector((-t.y,t.x))
        if n.x*( -170.0-A.x)+n.y*(118.0-A.y)<0: n=-n          # inward (towards the wing interior)
        for on,tol in SRC:
            o=bpy.data.objects[on]; me=o.data; mw=o.matrix_world; W=[mw@v.co for v in me.vertices]
            ec=collections.defaultdict(list)
            for p in me.polygons:
                for k in p.edge_keys: ec[k].append(p)
            def endset(P,sgn):
                S={}
                for k,fl in ec.items():
                    if len(fl)!=1: continue
                    a=W[k[0]]; b=W[k[1]]
                    ok=all(abs((v.xy-P).dot(t))<tol and -0.2<(v.xy-P).dot(n)<2.1 for v in (a,b))
                    if not ok: continue
                    # the face must lie on the far side of the end (away from the gap)
                    if (mw@fl[0].center).xy.__sub__(P).dot(t)*sgn>0: continue
                    ka=(round((a.xy-P).dot(n),2),round(a.z,2)); kb=(round((b.xy-P).dot(n),2),round(b.z,2))
                    if ka==kb: continue
                    S[frozenset((ka,kb))]=(k,fl[0],{ka:k[0],kb:k[1]})
                return S
            SA=endset(A,+1); SB=endset(B,-1)
            for key,(kA,fA,mA) in SA.items():
                if key not in SB: print('QA_NOMATCH',on,sorted(key)); continue
                kB,fB,mB=SB[key]; k1,k2=sorted(key)
                q=[W[mA[k1]],W[mA[k2]],W[mB[k2]],W[mB[k1]]]
                src=[(fA,mA[k1]),(fA,mA[k2]),(fB,mB[k2]),(fB,mB[k1])]
                Nref=(mw.to_3x3()@fA.normal).normalized()
                if (q[1]-q[0]).cross(q[3]-q[0]).dot(Nref)<0: q=[q[1],q[0],q[3],q[2]]; src=[src[1],src[0],src[3],src[2]]
                try: f=bm.faces.new([V(x) for x in q])
                except ValueError: continue
                f.material_index=mi(me.materials[fA.material_index]); nf+=1
                for lp,(fp,vi) in zip(f.loops,src):
                    for lname,ul in (('facade',ULF),('UVMap',ULU)):
                        if lname in me.uv_layers:
                            L=me.uv_layers[lname].data
                            for li in fp.loop_indices:
                                if me.loops[li].vertex_index==vi: lp[ul].uv=L[li].uv.copy()
        # brick sliver from the true LiDAR wall top up to the 151.30 raise bottom
        wo=bpy.data.objects['Dickson Hall walls']; me=wo.data; mw=wo.matrix_world; W=[mw@v.co for v in me.vertices]
        ec=collections.defaultdict(list)
        for p in me.polygons:
            for k in p.edge_keys: ec[k].append(p)
        for k,fl in ec.items():
            a=W[k[0]]; b=W[k[1]]
            if len(fl)!=1 or min(a.z,b.z)<151.0: continue
            if ((a.xy-A).length<0.02 and (b.xy-B).length<0.02) or ((a.xy-B).length<0.02 and (b.xy-A).length<0.02):
                Nref=-Vector((n.x,n.y,0)); vs=[a,b]+[Vector((v.x,v.y,151.30)) for v in (b,a)]
                pts=[vs[0],vs[1]]+([vs[2]] if vs[2].z-vs[1].z>0.004 else [])+([vs[3]] if vs[3].z-vs[0].z>0.004 else [])
                if len(pts)<3: continue
                if (pts[1]-pts[0]).cross(pts[2]-pts[0]).dot(Nref)<0: pts=pts[::-1]
                f=bm.faces.new([V(x) for x in pts]); f.material_index=mi(mats['PE_Dickson_brick_buff_no_red_spandrel_UNVERIFIED'])
                # facade UV from the wall face's own map (affine fit)
                L=me.uv_layers['facade'].data; P=[W[me.loops[li].vertex_index] for li in fl[0].loop_indices]; U=[L[li].uv for li in fl[0].loop_indices]
                a0=P[1]-P[0]; b0=P[2]-P[0]; du=U[1]-U[0]; dv=U[2]-U[0]
                import numpy as np
                M=np.array([[a0.x,a0.y,a0.z],[b0.x,b0.y,b0.z]]); R=np.array([[du.x,du.y],[dv.x,dv.y]])
                X=np.linalg.lstsq(M,R,rcond=None)[0]
                for lp in f.loops:
                    d=lp.vert.co-P[0]; uv=np.array([d.x,d.y,d.z])@X; lp[ULF].uv=(U[0].x+uv[0],U[0].y+uv[1])
                nf+=1; print('QA_SLIVER %.2f %.2f z %.3f/%.3f'%(a.x,a.y,a.z,b.z))
    m2=bpy.data.meshes.new(NAME); bm.to_mesh(m2); bm.free()
    for mm in MAT: m2.materials.append(mats[mm])
    o=bpy.data.objects.new(NAME,m2); o['source_note']='UNVERIFIED (qa, Nov 2 2026): closes the two ~0.8 m south-end gaps in the py/pz parapet chain (brick raise, back face, membrane, coping, drip stain bridged between the exact open end profiles + wall-top sliver); no roofline photo'
    bpy.data.objects['Dickson Hall walls'].users_collection[0].objects.link(o)
    print('QA_GAPS faces',nf,'mats',MAT)

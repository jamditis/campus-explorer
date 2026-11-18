# qi (Nov 2 2026): re-grid the east edge x 150-246(250), y -35..250 from the 1 m LiDAR DTM to kill the 21,272 m2
# east-edge fan quad (qh: evaluated face 115658, centre (162.8,49.7)) + neighbours. Method = qg/qh: hidden 1 m LiDAR
# patch QI_east_edge_LiDAR_terrain_patch joined into Terrain_LiDAR_DTM_1m by removable GN QI_east_edge_LiDAR_patch that
# deletes old evaluated faces whose centre lies over the patch. The patch grows (iteratively) to cover the full
# footprint of every deleted face, so no hole opens to Context_skirt. Heights: north/data/grid_1m.npz dtm_filled
# (2023, x<=219); x>219: data/dtm_1m.npy shape offset to the x=219 column, its relief faded out north of y~95-110
# (data/dtm_1m is beyond-data fill there) -> flat-east extrapolation, APPROXIMATE. 4 m feather into kept surface.
# Re-drape: mesh objects draped on the old (deleted) surface (roads, OZ walks, grass, ...) get per-vertex dz; small
# resting objects are moved whole ('qi_dz'). Original coords in data/qi/drape_bak.npz. REVERT=1 -> exact pre-qi.
import bpy, bmesh, os, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; PN='QI_east_edge_LiDAR_terrain_patch'; MODN='QI_east_edge_LiDAR_patch'
BAK='data/qi/drape_bak.npz'; PRN='QI_east_edge_delete_probe'
def rm():
    m=T.modifiers.get(MODN)
    if m:
        ng=m.node_group; T.modifiers.remove(m)
        if ng and ng.users==0: bpy.data.node_groups.remove(ng)
    for nm in (PN,PRN):
        p=bpy.data.objects.get(nm)
        if p: me=p.data; bpy.data.objects.remove(p,do_unlink=True); bpy.data.meshes.remove(me)
    for o in bpy.data.objects:
        if 'qi_dz' in o: o.location.z-=o['qi_dz']; del o['qi_dz']
    if os.path.exists(BAK):
        z=np.load(BAK)
        for k in z.files:
            o=bpy.data.objects.get(k)
            if o and o.type=='MESH' and o.get('qi_drape'):
                o.data.vertices.foreach_set('co',z[k].ravel()); o.data.update(); del o['qi_drape']
rm()
if REV: print('QI east reverted')
else:
    dg=bpy.context.evaluated_depsgraph_get(); Te=T.evaluated_get(dg); em=Te.to_mesh(); MW=T.matrix_world
    vs=[MW@v.co for v in em.vertices]; ps=[tuple(p.vertices) for p in em.polygons]; mats=[p.material_index for p in em.polygons]
    uvl=em.uv_layers['ortho'].data; A_=[];B_=[]
    for pi_ in range(0,len(em.polygons),997):
        p=em.polygons[pi_]
        for li in p.loop_indices:
            v=vs[em.loops[li].vertex_index]; A_.append((v.x,v.y,1)); B_.append(tuple(uvl[li].uv))
    sol=np.linalg.lstsq(np.array(A_),np.array(B_),rcond=None)[0]
    Te.to_mesh_clear()
    V=np.array([(v.x,v.y,v.z) for v in vs]); NF=len(ps)
    cen=np.array([V[list(p),:2].mean(0) for p in ps])
    print('TERRAIN eval faces',NF,'xmax',V[:,0].max(),'ymin',V[:,1].min())
    GX0,GX1,GY0,GY1=40,250,-60,262; gnx,gny=GX1-GX0,GY1-GY0
    mark=np.zeros((gny,gnx),bool); mark[-35-GY0:250-GY0, 150-GX0:min(246,GX1)-GX0]=True
    if V[:,0].max()>246: mark[-35-GY0:250-GY0, 150-GX0:gnx]=True
    bh=BVHTree.FromPolygons(vs,ps); cov=np.zeros_like(mark)
    for j in range(gny):
        for i in range(gnx):
            if mark[j,i] and bh.ray_cast(Vector((GX0+i+.5,GY0+j+.5,400)),Vector((0,0,-1)))[0] is not None: cov[j,i]=True
    print('RECT cells',int(mark.sum()),'covered by old terrain',int(cov.sum())); mark=cov
    # long fan slivers (max edge > 6 m on a 1 m grid) touching the east edge box: their centres join the mark
    nsl=0
    for f,p in enumerate(ps):
        Q=V[list(p),:2]
        if Q[:,0].max()<140 or Q[:,0].min()>250 or Q[:,1].max()<-40 or Q[:,1].min()>255: continue
        if np.max(np.linalg.norm(Q-np.roll(Q,1,0),axis=1))>6:
            i=int(math.floor(cen[f,0]-GX0)); j=int(math.floor(cen[f,1]-GY0))
            if 0<=i<gnx and 0<=j<gny: mark[j,i]=True; nsl+=1
    print('SLIVERS',nsl)
    # faces in the LiDAR-covered box (x<=219) whose vertices sit > 2 m off the 1 m DTM: centres join the mark
    Dg=np.load('north/data/grid_1m.npz')['dtm_filled']
    vi=np.clip(np.floor(V[:,0]).astype(int)+600,0,819); vj=np.clip(np.floor(V[:,1]).astype(int)+260,0,1659); vdev=np.abs(V[:,2]-Dg[vj,vi]); nof=0
    for f,p in enumerate(ps):
        cx,cy=cen[f]
        if not(150<=cx<219 and -35<=cy<250): continue
        if vdev[list(p)].max()>2.0:
            i=int(math.floor(cx-GX0)); j=int(math.floor(cy-GY0))
            if not mark[j,i]: mark[j,i]=True; nof+=1
    print('OFFDTM faces added',nof)
    def cellsof(xy):
        i=np.floor(xy[:,0]-GX0).astype(int); j=np.floor(xy[:,1]-GY0).astype(int); ok=(i>=0)&(i<gnx)&(j>=0)&(j<gny); return i,j,ok
    ci,cj,cok=cellsof(cen)
    for it in range(4):
        dele=np.zeros(NF,bool); dele[cok]=mark[cj[cok],ci[cok]]
        markdel=mark.copy(); new=mark.copy()
        for f in np.nonzero(dele)[0]:
            P=V[list(ps[f]),:2]; x0,y0=np.floor(P.min(0)).astype(int); x1,y1=np.ceil(P.max(0)).astype(int)
            if (x1-x0)*(y1-y0)<=4:
                for yy in range(y0,y1):
                    for xx in range(x0,x1):
                        if GX0<=xx<GX1 and GY0<=yy<GY1: new[yy-GY0,xx-GX0]=True
                continue
            gx,gy=np.meshgrid(np.arange(x0,x1)+0.5,np.arange(y0,y1)+0.5); q=np.stack([gx.ravel(),gy.ravel()],1)
            inside=np.zeros(len(q),bool)
            for t in range(1,len(P)-1):   # fan triangulation, point-in-triangle (+0.75 m margin via cell corners)
                a,b,c=P[0],P[t],P[t+1]
                for off in ((0,0),(-.5,-.5),(.5,-.5),(-.5,.5),(.5,.5)):
                    qq=q+np.array(off)
                    d1=(qq[:,0]-b[0])*(a[1]-b[1])-(a[0]-b[0])*(qq[:,1]-b[1]); d2=(qq[:,0]-c[0])*(b[1]-c[1])-(b[0]-c[0])*(qq[:,1]-c[1]); d3=(qq[:,0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(qq[:,1]-a[1])
                    inside|=~(((d1<0)|(d2<0)|(d3<0))&((d1>0)|(d2>0)|(d3>0)))
            qi_=np.floor(q[inside]).astype(int)
            for xx,yy in qi_:
                if GX0<=xx<GX1 and GY0<=yy<GY1: new[yy-GY0,xx-GX0]=True
        print('ITER',it,'deleted',int(dele.sum()),'cells',int(mark.sum()),'->',int(new.sum()))
        mark=new
    print('DEL cells',int(markdel.sum()),'PATCH cells',int(mark.sum()))
    keep=[ps[f] for f in range(NF) if not dele[f]]; delp=[ps[f] for f in range(NF) if dele[f]]
    bk=BVHTree.FromPolygons(vs,keep); bd=BVHTree.FromPolygons(vs,delp); delidx=np.nonzero(dele)[0]
    D=np.load('north/data/grid_1m.npz')['dtm_filled']; A=np.load('data/dtm_1m.npy')
    def hcell(x,y):  # x,y integer cell (lower-left)
        y=min(max(y,-259),249)
        if x<=219: return float(D[y+260,max(x,-600)+600])
        w=1.0 if y<95 else (0.0 if y>110 else (110-y)/15.0)
        xa=min(x,249); return float(D[y+260,819]+(A[y+250,xa+250]-A[y+250,219+250])*w)
    src=~mark; dist=np.full((gny,gnx),99.0); cur=src.copy(); dist[src]=0
    SK=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; bsk=BVHTree.FromObject(SK,bpy.context.evaluated_depsgraph_get())
    for k in range(1,9):
        nb=cur.copy(); nb[1:,:]|=cur[:-1,:]; nb[:-1,:]|=cur[1:,:]; nb[:,1:]|=cur[:,:-1]; nb[:,:-1]|=cur[:,1:]
        dist[nb&~cur]=k; cur=nb
    bm=bmesh.new(); vid={}; uvL=bm.loops.layers.uv.new('ortho'); nfe=0
    def vert(i,j):
        if (i,j) in vid: return vid[(i,j)]
        x=GX0+i; y=GY0+j; z=(hcell(x-1,y-1)+hcell(x,y-1)+hcell(x-1,y)+hcell(x,y))/4
        cs=[(min(j,gny-1),min(i,gnx-1)),(max(j-1,0),max(i-1,0)),(min(j,gny-1),max(i-1,0)),(max(j-1,0),min(i,gnx-1))]
        dd=min(dist[a][b] for a,b in cs)
        if dd<6.5:
            loc=bk.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0] if dd<4.5 else None
            if loc is not None:
                w=max(0.0,(dd-0.5)/4.0); w=w*w*(3-2*w); z=loc.z*(1-w)+z*w
            elif bk.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0] is None:
                ls=bsk.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
                if ls is not None:
                    w=max(0.0,(dd-0.5)/6.0); w=w*w*(3-2*w); z=ls.z*(1-w)+z*w
        if not any(markdel[a][b] for a,b in cs if mark[a][b]): z-=0.03
        v=bm.verts.new((x,y,z)); vid[(i,j)]=v; return v
    mi=np.zeros((gny,gnx),int); common=None
    for j in range(gny):
        for i in range(gnx):
            if not mark[j,i]: continue
            h=bd.ray_cast(Vector((GX0+i+.5,GY0+j+.5,400)),Vector((0,0,-1)))
            mi[j,i]=mats[int(delidx[h[2]])] if h[0] is not None else -1
    vals=mi[mark&(mi>=0)]; common=int(np.bincount(vals).argmax()) if len(vals) else 0
    for j in range(gny):
        for i in range(gnx):
            if not mark[j,i]: continue
            f=bm.faces.new([vert(i,j),vert(i+1,j),vert(i+1,j+1),vert(i,j+1)]); f.material_index=int(mi[j,i]) if mi[j,i]>=0 else common; f.smooth=True
            for l in f.loops:
                co=l.vert.co; l[uvL].uv=(sol[0,0]*co.x+sol[1,0]*co.y+sol[2,0], sol[0,1]*co.x+sol[1,1]*co.y+sol[2,1])
    me=bpy.data.meshes.new(PN); bm.to_mesh(me); bm.free()
    for m in T.data.materials: me.materials.append(m)
    P=bpy.data.objects.new(PN,me); P['qi']=1; T.users_collection[0].objects.link(P); P.hide_render=True; P.hide_viewport=True
    bm2=bmesh.new(); v2={}
    def vv(i,j):
        if (i,j) not in v2: v2[(i,j)]=bm2.verts.new((GX0+i,GY0+j,0))
        return v2[(i,j)]
    for j in range(gny):
        for i in range(gnx):
            if markdel[j,i]: bm2.faces.new([vv(i,j),vv(i+1,j),vv(i+1,j+1),vv(i,j+1)])
    me2=bpy.data.meshes.new(PRN); bm2.to_mesh(me2); bm2.free()
    PR=bpy.data.objects.new(PRN,me2); PR['qi']=1; T.users_collection[0].objects.link(PR); PR.hide_render=True; PR.hide_viewport=True
    ng=bpy.data.node_groups.new(MODN+'_GN','GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=P; oi.transform_space='ORIGINAL'
    pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); comb=N.new('ShaderNodeCombineXYZ'); comb.inputs['Z'].default_value=400
    L.new(pos.outputs[0],sep.inputs[0]); L.new(sep.outputs[0],comb.inputs[0]); L.new(sep.outputs[1],comb.inputs[1])
    rc=N.new('GeometryNodeRaycast'); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=1000
    oi2=N.new('GeometryNodeObjectInfo'); oi2.inputs['Object'].default_value=PR; oi2.transform_space='ORIGINAL'
    L.new(oi2.outputs['Geometry'],rc.inputs['Target Geometry']); L.new(comb.outputs[0],rc.inputs['Source Position'])
    dl=N.new('GeometryNodeDeleteGeometry'); dl.domain='FACE'
    L.new(gi.outputs[0],dl.inputs['Geometry']); L.new(rc.outputs['Is Hit'],dl.inputs['Selection'])
    jn=N.new('GeometryNodeJoinGeometry'); L.new(oi.outputs['Geometry'],jn.inputs[0]); L.new(dl.outputs[0],jn.inputs[0]); L.new(jn.outputs[0],go.inputs[0])
    md=T.modifiers.new(MODN,'NODES'); md.node_group=ng
    nb_=BVHTree.FromObject(P,bpy.context.evaluated_depsgraph_get())
    # check: evaluated faces now vs GN deletion agrees with our set
    Te2=T.evaluated_get(bpy.context.evaluated_depsgraph_get()); print('EVAL faces after',len(Te2.data.polygons))
    # outer edge vs Context_skirt
    sk=[]
    pk=[(v.co.z-(bsk.ray_cast(Vector((v.co.x,v.co.y,400)),Vector((0,0,-1)))[0] or Vector((0,0,-999))).z) for v in me.vertices]
    print('PATCH minus skirt min',round(min(pk),2),'n<0.05',sum(1 for d in pk if d<0.05))
    if sk:
        bs=BVHTree.FromObject(sk[0],bpy.context.evaluated_depsgraph_get()); mx=[]
        for v in me.vertices:
            if v.co.x>=245 or v.co.y<=-34:
                h=bs.ray_cast(Vector((v.co.x+1.5 if v.co.x>=245 else v.co.x, v.co.y if v.co.x>=245 else v.co.y-1.5, 400)),Vector((0,0,-1)))[0]
                if h is not None: mx.append(v.co.z-h.z)
        if mx: print('SKIRT edge dz min/max/mean',round(min(mx),2),round(max(mx),2),round(float(np.mean(mx)),2),len(mx))
    # re-drape
    skipn=('Terrain','Context_','QG_','QH_','QI_')
    bak={}; dr=[]; moved=[]; nr=[]
    def inmark(x,y):
        i=np.floor(x-GX0).astype(int); j=np.floor(y-GY0).astype(int); ok=(i>=0)&(i<gnx)&(j>=0)&(j<gny)
        r=np.zeros(len(x),bool); r[ok]=mark[j[ok],i[ok]]; return r
    X0w,X1w,Y0w,Y1w=GX0,GX1,GY0,GY1
    for o in list(bpy.data.objects):
        if o.parent or o.hide_render or any(o.name.startswith(s) for s in skipn) or o.type not in('MESH','EMPTY','CURVE','CAMERA','LIGHT'): continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if max(v.x for v in bb)<X0w or min(v.x for v in bb)>X1w or max(v.y for v in bb)<Y0w or min(v.y for v in bb)>Y1w: continue
        small=o.name.startswith('T_') or (max(v.x for v in bb)-min(v.x for v in bb))<=25 and (max(v.y for v in bb)-min(v.y for v in bb))<=25 and (max(v.z for v in bb)-min(v.z for v in bb))<=40
        if o.type=='MESH' and len(o.data.vertices)>0 and not small:
            if any(m.type=='SHRINKWRAP' for m in o.modifiers): nr.append(o.name+'(shrinkwrap)'); continue
            n=len(o.data.vertices); co=np.zeros(n*3,np.float32); o.data.vertices.foreach_get('co',co); co=co.reshape(n,3)
            M=np.array(o.matrix_world); W=co@M[:3,:3].T+M[:3,3]
            sel=np.nonzero(inmark(W[:,0],W[:,1]))[0]
            if len(sel)==0: continue
            dz=np.zeros(len(sel)); ok=np.zeros(len(sel),bool)
            for k,ix in enumerate(sel):
                x,y,z=W[ix]; lo=bh.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
                if lo is None or abs(z-lo.z)>1.5: continue
                ln=nb_.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
                if ln is None: continue
                dz[k]=ln.z-lo.z; ok[k]=True
            frac=ok.mean()
            if frac<0.8 or not np.any(np.abs(dz[ok])>0.02):
                if ok.sum()>0 and np.abs(dz[ok]).max()>0.3: nr.append('%s(frac %.2f n%d maxdz %.1f)'%(o.name,frac,len(sel),np.abs(dz[ok]).max()))
                continue
            if abs(np.linalg.det(M[:3,:3])-1)>1e-3 or abs(M[2,2]-1)>1e-4: nr.append(o.name+'(xform)'); continue
            bak[o.name]=co.copy(); W2=W.copy(); W2[sel[ok],2]+=dz[ok]
            co2=(W2-M[:3,3])@np.linalg.inv(M[:3,:3]).T; o.data.vertices.foreach_set('co',co2.astype(np.float32).ravel()); o.data.update(); o['qi_drape']=1
            dr.append((o.name,int(ok.sum()),round(float(dz[ok].min()),1),round(float(dz[ok].max()),1)))
        elif small:
            x,y=o.matrix_world.translation.x,o.matrix_world.translation.y
            if not inmark(np.array([x]),np.array([y]))[0]: continue
            zmin=min(v.z for v in bb); lo=bh.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]; ln=nb_.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
            if lo is None or ln is None: continue
            if abs(zmin-lo.z)>0.8 and abs(o.matrix_world.translation.z-lo.z)>0.8: continue
            dz=ln.z-lo.z
            if abs(dz)<0.05: continue
            o.location.z+=dz; o['qi_dz']=dz; moved.append((o.name,round(dz,2)))
    # trees / lamps / benches inside the patch whose base is off the new ground (incl. pre-existing buried London planes)
    btn=BVHTree.FromObject(T,bpy.context.evaluated_depsgraph_get()); bpp=BVHTree.FromObject(P,bpy.context.evaluated_depsgraph_get()); rs=[]
    for o in bpy.data.objects:
        if o.parent or o.hide_render or 'qi_dz' in o or not o.name.startswith(('T_','Lamp_','Bench_')): continue
        x,y,z=o.matrix_world.translation
        if not(140<=x<=252 and -40<=y<=256): continue
        if bpp.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0] is None: continue
        h=btn.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
        if h is None: continue
        if o.name.startswith('T_'): d=h.z-z; th=0.3
        else: d=h.z-min((o.matrix_world@Vector(c)).z for c in o.bound_box); th=0.15
        if abs(d)>th: o.location.z+=d; o['qi_dz']=d; rs.append((o.name,round(d,2)))
    print('RESEAT',len(rs),rs[:60])
    if bak: np.savez(BAK,**bak)
    print('DRAPED',len(dr),dr[:40]); print('MOVED',len(moved),moved[:40]); print('NOT_REDRAPED',len(nr),nr[:40])
    print('PATCH faces',len(me.polygons),'GRID z range',round(min(v.co.z for v in me.vertices),1),round(max(v.co.z for v in me.vertices),1))

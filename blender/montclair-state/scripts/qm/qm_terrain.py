# qm (4): terrain band SE/E of CELS (old stair-stepped LiDAR-disc edge): scene terrain was 2-6 m BELOW the 2023 1 m DTM along a
# diagonal strip (105,140)->(150,185) (the 'pit' at ~(146,172)) and 0.5-3 m ABOVE it on a parallel strip x 130-150, y 125-165.
# Fix: hidden helper grid QM_terrain_band_DTM_helper (cell centres, z = north/data/grid_1m.npz dtm_filled, point attr qm_w =
# 1 where |scene-DTM|>0.25 m, dilated 2 cells, 3-cell feather, 0 under buildings) + last GN modifier QM_terrain_band_to_DTM on
# Terrain_LiDAR_DTM_1m: z += w*(DTM - z) via a downward Raycast onto the helper. Box x 86-162, y 64-194 only.
# Objects standing on the old ground in the box are re-seated by whole-object dz (prop qm_dz). REVERT=1 undoes all. UNVERIFIED feather.
import bpy, os, numpy as np, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; MN='QM_terrain_band_to_DTM'; HN='QM_terrain_band_DTM_helper'
X0,X1,Y0,Y1=86,162,64,194
for o in bpy.data.objects:
    if 'qm_dz' in o: o.location.z-=o['qm_dz']; del o['qm_dz']
for nm in (MN+'_cut',MN):
    m=T.modifiers.get(nm)
    if m: T.modifiers.remove(m)
    g=bpy.data.node_groups.get(nm+'_GN')
    if g: bpy.data.node_groups.remove(g)
h=bpy.data.objects.get(HN)
if h: me=h.data; bpy.data.objects.remove(h,do_unlink=True); bpy.data.meshes.remove(me)
UN='QM_terrain_band_underlay_UNVERIFIED'
u=bpy.data.objects.get(UN)
if u: me=u.data; bpy.data.objects.remove(u,do_unlink=True); bpy.data.meshes.remove(me)
if not REV:
    dg=bpy.context.evaluated_depsgraph_get(); bt=BVHTree.FromObject(T,dg)
    D=np.load('north/data/grid_1m.npz')['dtm_filled']
    xs=np.arange(X0,X1); ys=np.arange(Y0,Y1); nx,ny=len(xs),len(ys)
    Z=np.full((ny,nx),np.nan); DZ=D[ys[:,None]+260, xs[None,:]+600].astype(float)
    for j,y in enumerate(ys):
        for i,x in enumerate(xs):
            r=bt.ray_cast(Vector((x+0.5,y+0.5,400)),Vector((0,0,-1)))[0]
            if r is not None: Z[j,i]=r.z
    # building mask: any visible mesh in Buildings_context (or other building collections) above the cell
    bobs=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and (' walls' in o.name or 'roof (LiDAR)' in o.name or o.name.startswith('CELS L'))]
    btrees=[]
    for o in bobs:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if max(p.x for p in bb)<X0-2 or min(p.x for p in bb)>X1+2 or max(p.y for p in bb)<Y0-2 or min(p.y for p in bb)>Y1+2: continue
        btrees.append(BVHTree.FromObject(o,dg))
    B=np.zeros((ny,nx),bool)
    for j,y in enumerate(ys):
        for i,x in enumerate(xs):
            p=Vector((x+0.5,y+0.5,(Z[j,i] if not np.isnan(Z[j,i]) else DZ[j,i])-3))
            B[j,i]=any(t.ray_cast(p,Vector((0,0,1)),60)[0] is not None for t in btrees)
    bad=(np.abs(Z-DZ)>0.25)&~np.isnan(Z)&~B
    def dil(M):
        R=M.copy(); R[1:,:]|=M[:-1,:]; R[:-1,:]|=M[1:,:]; R[:,1:]|=M[:,:-1]; R[:,:-1]|=M[:,1:]; return R
    core=dil(dil(bad))&~B
    dist=np.where(core,0.0,99.0); cur=core.copy()
    for k in range(1,4):
        nxt=dil(cur); dist[nxt&~cur]=k; cur=nxt
    W=np.clip(1-dist/3.0,0,1); W[B]=0
    # zero at the box border so the edge is seamless
    for k in range(3): W[k,:]*=k/3; W[-1-k,:]*=k/3; W[:,k]*=k/3; W[:,-1-k]*=k/3
    print('QM_TERRAIN cells bad',int(bad.sum()),'w>0',int((W>0).sum()),'bldg',int(B.sum()),'max |diff| before',round(float(np.nanmax(np.abs(Z-DZ)[~B])),2))
    np.savez('data/qm/terrain_band.npz',Z=Z,D=DZ,W=W,B=B)
    me=bpy.data.meshes.new(HN); bm=bmesh.new(); V=[]
    gx=np.arange(X0-1,X1+1); gy=np.arange(Y0-1,Y1+1)   # 1-cell pad, w=0
    vid={}
    for j,y in enumerate(gy):
        for i,x in enumerate(gx):
            xi=min(max(x,X0),X1-1); yi=min(max(y,Y0),Y1-1)
            vid[(i,j)]=bm.verts.new((x+0.5,y+0.5,float(D[yi+260,xi+600])))
    bm.verts.ensure_lookup_table()
    for j in range(len(gy)-1):
        for i in range(len(gx)-1): bm.faces.new((vid[(i,j)],vid[(i+1,j)],vid[(i+1,j+1)],vid[(i,j+1)]))
    bm.to_mesh(me); bm.free()
    wa=np.zeros((len(gy),len(gx))); wa[1:-1,1:-1]=W
    at=me.attributes.new('qm_w','FLOAT','POINT'); at.data.foreach_set('value',wa.ravel().astype(np.float32))
    hobj=bpy.data.objects.new(HN,me); bpy.context.scene.collection.objects.link(hobj); hobj.hide_render=True; hobj.hide_viewport=True
    hobj['UNVERIFIED_qm']='qm: DTM helper for QM_terrain_band_to_DTM'
    ng=bpy.data.node_groups.new(MN+'_GN','GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=hobj; oi.transform_space='RELATIVE'
    na=N.new('GeometryNodeInputNamedAttribute'); na.data_type='FLOAT'; na.inputs['Name'].default_value='qm_w'
    pos=N.new('GeometryNodeInputPosition'); sp=N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0],sp.inputs[0])
    so=N.new('ShaderNodeCombineXYZ'); L(sp.outputs[0],so.inputs[0]); L(sp.outputs[1],so.inputs[1]); so.inputs[2].default_value=400.0
    rc=N.new('GeometryNodeRaycast'); rc.data_type='FLOAT'
    L(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L(na.outputs[0],rc.inputs['Attribute'])
    L(so.outputs[0],rc.inputs['Source Position']); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=1000
    hs=N.new('ShaderNodeSeparateXYZ'); L(rc.outputs['Hit Position'],hs.inputs[0])
    sub=N.new('ShaderNodeMath'); sub.operation='SUBTRACT'; L(hs.outputs[2],sub.inputs[0]); L(sp.outputs[2],sub.inputs[1])
    mul=N.new('ShaderNodeMath'); mul.operation='MULTIPLY'; L(sub.outputs[0],mul.inputs[0]); L(rc.outputs['Attribute'],mul.inputs[1])
    off=N.new('ShaderNodeCombineXYZ'); L(mul.outputs[0],off.inputs[2])
    st=N.new('GeometryNodeSetPosition'); L(gi.outputs[0],st.inputs['Geometry']); L(rc.outputs['Is Hit'],st.inputs['Selection']); L(off.outputs[0],st.inputs['Offset']); L(st.outputs[0],go.inputs[0])
    md=T.modifiers.new(MN,'NODES'); md.node_group=ng
    T['UNVERIFIED_qm']='qm: terrain band SE/E of CELS pulled onto the 2023 DTM (GN QM_terrain_band_to_DTM)'
    dg=bpy.context.evaluated_depsgraph_get(); dg.update(); bt2=BVHTree.FromObject(T,dg)
    Z2=np.full((ny,nx),np.nan)
    for j,y in enumerate(ys):
        for i,x in enumerate(xs):
            r=bt2.ray_cast(Vector((x+0.5,y+0.5,400)),Vector((0,0,-1)))[0]
            if r is not None: Z2[j,i]=r.z
    dd=np.abs(Z2-DZ); print('QM_TERRAIN after: cells >0.25',int(((dd>0.25)&~B).sum()),'max',round(float(np.nanmax(dd[~B])),2))
    # reseat objects standing on the old ground
    def gz(t,x,y):
        r=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]; return r.z if r is not None else None
    nres=0; skipped=[]
    for o in bpy.data.objects:
        if o.type not in ('MESH','EMPTY') or o==T or o.name==HN or o.parent: continue
        x,y=o.location.x,o.location.y
        if not (X0<=x<X1 and Y0<=y<Y1): continue
        if max(o.dimensions)>40: continue
        a=gz(bt,x,y); b=gz(bt2,x,y)
        if a is None or b is None or abs(b-a)<0.03: continue
        if abs(o.location.z-a)<1.0: o['qm_dz']=b-a; o.location.z+=b-a; nres+=1
        else: skipped.append((o.name[:40],round(o.location.z-a,2)))
    print('QM_TERRAIN reseated',nres,'skipped',skipped[:12])

    # cut: terrain faces in the band core (helper weight >0.5) are deleted; the continuous underlay (offset 0 there) becomes the
    # visible surface, removing the fold lips left by the unmerged QG/QI patch seams. NOTE: later terrain raycasts miss inside the cut.
    ng2=bpy.data.node_groups.new(MN+'_cut_GN','GeometryNodeTree')
    ng2.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng2.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng2.nodes; L=ng2.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=hobj; oi.transform_space='RELATIVE'
    na=N.new('GeometryNodeInputNamedAttribute'); na.data_type='FLOAT'; na.inputs['Name'].default_value='qm_w'
    pos=N.new('GeometryNodeInputPosition'); sp=N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0],sp.inputs[0])
    so=N.new('ShaderNodeCombineXYZ'); L(sp.outputs[0],so.inputs[0]); L(sp.outputs[1],so.inputs[1]); so.inputs[2].default_value=400.0
    rc=N.new('GeometryNodeRaycast'); rc.data_type='FLOAT'
    L(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L(na.outputs[0],rc.inputs['Attribute'])
    L(so.outputs[0],rc.inputs['Source Position']); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=1000
    cp=N.new('FunctionNodeCompare'); cp.data_type='FLOAT'; cp.operation='GREATER_THAN'; L(rc.outputs['Attribute'],cp.inputs[0]); cp.inputs[1].default_value=0.5
    dl=N.new('GeometryNodeDeleteGeometry'); dl.domain='FACE'; L(gi.outputs[0],dl.inputs['Geometry']); L(cp.outputs[0],dl.inputs['Selection']); L(dl.outputs[0],go.inputs[0])
    md2=T.modifiers.new(MN+'_cut','NODES'); md2.node_group=ng2
    print('QM_CUT added')
    # underlay: the corrected terrain has unmerged patch seams (QG/QI joins) that open thin vertical slits once moved; a copy of the
    # corrected surface 0.12 m lower (UVs + material sampled from the evaluated terrain) fills what shows through them.
    md2.show_viewport=True; dg=bpy.context.evaluated_depsgraph_get(); dg.update(); btc=BVHTree.FromObject(T,dg)
    md2.show_viewport=False; md2.show_render=False; dg.update()
    em=T.evaluated_get(dg).to_mesh(); emw=T.matrix_world
    vs=[emw@v.co for v in em.vertices]; ps=[tuple(p.vertices) for p in em.polygons]
    bf=BVHTree.FromPolygons(vs,ps); uvl=em.uv_layers.active
    from mathutils.interpolate import poly_3d_calc
    um=bpy.data.meshes.new(UN); bm=bmesh.new(); uvb=bm.loops.layers.uv.new('UVMap')
    for mt in T.data.materials: um.materials.append(mt)
    WD=np.zeros_like(W,bool); WD|=W>0; WD[1:,:]|=W[:-1,:]>0; WD[:-1,:]|=W[1:,:]>0; WD[:,1:]|=W[:,:-1]>0; WD[:,:-1]|=W[:,1:]>0
    vmap={}
    def vert(x,y):
        k=(x,y)
        if k not in vmap:
            r=bf.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
            for ox,oy in ((.03,.03),(-.03,.03),(.03,-.03),(-.03,-.03),(.15,.15),(-.15,-.15),(.15,-.15),(-.15,.15)):
                if r[0] is not None: break
                r=bf.ray_cast(Vector((x+ox,y+oy,400)),Vector((0,0,-1)))
            zfix=None
            if r[0] is None:  # inside a pre-existing patch slit: DTM height, UV/material from the nearest hit within 1 m
                for ox,oy in ((.5,0),(-.5,0),(0,.5),(0,-.5),(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):
                    r=bf.ray_cast(Vector((x+ox,y+oy,400)),Vector((0,0,-1)))
                    if r[0] is not None: break
                xi=min(max(int(x),X0),X1-1); yi=min(max(int(y),Y0),Y1-1); zfix=float(D[yi+260,xi+600])
            if r[0] is None: vmap[k]=None
            else:
                f=r[2]; pv=[vs[i] for i in ps[f]]; w=poly_3d_calc(pv,r[0]); lp=em.polygons[f].loop_indices
                uv=sum((uvl.data[l].uv*w[n] for n,l in enumerate(lp)),Vector((0,0))) if uvl else Vector((0,0))
                ci=x-X0; cj=y-Y0
                if abs(ci-round(ci))<1e-6:  # grid corner: max of the 4 adjoining cells
                    ii=int(round(ci)); jj=int(round(cj)); wc=max([float(W[b,a]) for a in (ii-1,ii) for b in (jj-1,jj) if 0<=a<W.shape[1] and 0<=b<W.shape[0]]+[0.0])
                else: wc=float(W[int(cj),int(ci)])
                if btc.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0] is None: wc=1.0
                vmap[k]=(bm.verts.new((x,y,(zfix if zfix is not None else r[0].z)-(0.0 if wc>0.4 else 0.12))),uv.copy(),em.polygons[f].material_index)
        return vmap[k]
    nf=0
    for j,y in enumerate(ys):
        for i,x in enumerate(xs):
            opened=any(btc.ray_cast(Vector((x+dx,y+dy,400)),Vector((0,0,-1)))[0] is None and bf.ray_cast(Vector((x+dx,y+dy,400)),Vector((0,0,-1)))[0] is not None for dx in (0.1,0.5,0.9) for dy in (0.1,0.5,0.9))
            if not opened and (not WD[j,i] or B[j,i]): continue
            q=[vert(float(x),float(y)),vert(float(x+1),float(y)),vert(float(x+1),float(y+1)),vert(float(x),float(y+1))]
            if any(a is None for a in q): continue
            try: f=bm.faces.new([a[0] for a in q])
            except ValueError: continue
            for l,a in zip(f.loops,q): l[uvb].uv=a[1]
            c=vert(float(x)+0.5,float(y)+0.5)
            f.material_index=c[2] if c else q[0][2]; nf+=1
    bm.to_mesh(um); bm.free(); T.evaluated_get(dg).to_mesh_clear(); md2.show_viewport=True; md2.show_render=True
    uo=bpy.data.objects.new(UN,um); bpy.context.scene.collection.objects.link(uo); uo['UNVERIFIED_qm']='qm: underlay under the QM terrain band fix'
    uo.visible_shadow=False
    print('QM_UNDERLAY faces',nf)


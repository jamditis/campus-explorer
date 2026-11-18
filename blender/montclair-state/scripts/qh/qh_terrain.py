# qh (Nov 2 2026): residual north-strip terrain fan east of the qg patch (x~165-220, y~196-249): old sliver fan was
# +2..+15 m above the 1 m LiDAR (north/data/grid_1m.npz dtm_filled) and had a hole at y~198-206 (ground fell to the
# beyond-data plane). Same method as qg: 1 m LiDAR patch object (hidden) joined into Terrain_LiDAR_DTM_1m by a removable
# GN modifier that deletes old faces whose centre lies over the patch; 4 m feather into good surface; objects resting on
# the old surface re-seated (z shift in 'qh_dz'). All bad fan faces are covered completely (cells hit by any bad face).
# REVERT=1 -> exact pre-qh. UNVERIFIED feather.
import bpy, bmesh, os, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; DRY=os.environ.get('DRY')=='1'
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; PN='QH_east_fan_LiDAR_terrain_patch'; MODN='QH_east_fan_LiDAR_patch'
def rm():
    m=T.modifiers.get(MODN)
    if m:
        ng=m.node_group; T.modifiers.remove(m)
        if ng and ng.users==0: bpy.data.node_groups.remove(ng)
    p=bpy.data.objects.get(PN)
    if p: me=p.data; bpy.data.objects.remove(p,do_unlink=True); bpy.data.meshes.remove(me)
    for o in bpy.data.objects:
        if 'qh_dz' in o: o.location.z-=o['qh_dz']; del o['qh_dz']
rm()
if REV: print('QH terrain reverted')
else:
    dg=bpy.context.evaluated_depsgraph_get(); Te=T.evaluated_get(dg); em=Te.to_mesh(); MW=T.matrix_world
    vs=[MW@v.co for v in em.vertices]; ps=[tuple(p.vertices) for p in em.polygons]; mats=[p.material_index for p in em.polygons]
    uvl=em.uv_layers['ortho'].data; A=[];B=[]
    for pi_ in range(0,len(em.polygons),997):
        p=em.polygons[pi_]
        for li in p.loop_indices:
            v=vs[em.loops[li].vertex_index]; A.append((v.x,v.y,1)); B.append(tuple(uvl[li].uv))
    sol=np.linalg.lstsq(np.array(A),np.array(B),rcond=None)[0]
    bvh=BVHTree.FromPolygons(vs,ps); Te.to_mesh_clear()
    D=np.load('north/data/grid_1m.npz')['dtm_filled']
    def lidc(x,y): return float(D[int(math.floor(y))+260,int(math.floor(x))+600])
    def lid(x,y):
        r=int(round(y))+260; c=int(round(x))+600; c=min(c,819); return float(D[r-1:r+1,c-1:c+1].mean())
    X0,X1,Y0,Y1=150,220,190,250; nx,ny=X1-X0,Y1-Y0
    face=np.full((ny,nx),-1); dev=np.zeros((ny,nx))
    for j in range(ny):
        for i in range(nx):
            x=X0+i+0.5; y=Y0+j+0.5; loc,n,fi,d=bvh.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
            if loc is None: continue
            face[j,i]=fi; dev[j,i]=loc.z-lidc(x,y)
    bad=set(int(face[j,i]) for j in range(ny) for i in range(nx) if face[j,i]>=0 and abs(dev[j,i])>0.6 and X0+i>=165)
    # pass 2: grow the grid to the full extent of the bad faces (long fan slivers reach far outside the probe box)
    bx=[vs[k].x for f in bad for k in ps[f]]; by=[vs[k].y for f in bad for k in ps[f]]
    X0=max(-220,int(math.floor(min(bx)))-1); X1=min(220,int(math.ceil(max(bx)))+1); Y0=max(100,int(math.floor(min(by)))-1); Y1=min(262,int(math.ceil(max(by)))+1)
    nx,ny=X1-X0,Y1-Y0; print('GRID2',X0,X1,Y0,Y1)
    face=np.full((ny,nx),-1); dev=np.zeros((ny,nx))
    for j in range(ny):
        for i in range(nx):
            x=X0+i+0.5; y=Y0+j+0.5; loc,n,fi,d=bvh.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
            if loc is None: continue
            face[j,i]=fi; dev[j,i]=loc.z-lidc(x,y)
    bad|=set(int(face[j,i]) for j in range(ny) for i in range(nx) if face[j,i]>=0 and abs(dev[j,i])>0.6 and X0+i>=165)
    mark=np.isin(face,list(bad))
    # hole cells (no terrain) between y 196 and 210 inside the strip: fill
    hole=(face<0); 
    for j in range(ny):
        for i in range(nx):
            if hole[j,i] and 196<=Y0+j<=212 and X0+i>=165: mark[j,i]=True
    print('BADFACES',len(bad),'CELLS',int(mark.sum()),'holes',int((hole&mark).sum()))
    src=(face>=0)&~mark; dist=np.full((ny,nx),99.0); cur=src.copy(); dist[src]=0
    for k in range(1,7):
        nb=cur.copy(); nb[1:,:]|=cur[:-1,:]; nb[:-1,:]|=cur[1:,:]; nb[:,1:]|=cur[:,:-1]; nb[:,:-1]|=cur[:,1:]
        dist[nb&~cur]=k; cur=nb
    cm=np.where(face>=0,face,0); mi=np.vectorize(lambda f: mats[f] if f>=0 else 0)(face)
    if not DRY:
        bm=bmesh.new(); vid={}; uvL=bm.loops.layers.uv.new('ortho')
        def vert(i,j):
            if (i,j) in vid: return vid[(i,j)]
            x=X0+i; y=Y0+j; z=lid(x,y)
            cs=[(min(j,ny-1),min(i,nx-1)),(max(j-1,0),max(i-1,0)),(min(j,ny-1),max(i-1,0)),(max(j-1,0),min(i,nx-1))]
            dd=min(dist[a][b] for a,b in cs)
            if dd<4.5:
                loc,n,fi,d=bvh.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
                if loc is not None and fi not in bad:
                    w=max(0.0,(dd-0.5)/4.0); w=w*w*(3-2*w); z=loc.z*(1-w)+z*w
            v=bm.verts.new((x,y,z)); vid[(i,j)]=v; return v
        # fill material: most common neighbour material for hole cells
        common=int(np.bincount(mi[mark&(face>=0)]).argmax()) if (mark&(face>=0)).any() else 0
        for j in range(ny):
            for i in range(nx):
                if not mark[j,i]: continue
                f=bm.faces.new([vert(i,j),vert(i+1,j),vert(i+1,j+1),vert(i,j+1)]); f.material_index=int(mi[j,i]) if face[j,i]>=0 else common; f.smooth=True
                for l in f.loops:
                    co=l.vert.co; l[uvL].uv=(sol[0,0]*co.x+sol[1,0]*co.y+sol[2,0], sol[0,1]*co.x+sol[1,1]*co.y+sol[2,1])
        me=bpy.data.meshes.new(PN); bm.to_mesh(me); bm.free()
        for m in T.data.materials: me.materials.append(m)
        P=bpy.data.objects.new(PN,me); P['qh']=1; T.users_collection[0].objects.link(P); P.hide_render=True; P.hide_viewport=True
        ng=bpy.data.node_groups.new(MODN+'_GN','GeometryNodeTree')
        ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
        N=ng.nodes; L=ng.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
        oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=P; oi.transform_space='ORIGINAL'
        pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); comb=N.new('ShaderNodeCombineXYZ'); comb.inputs['Z'].default_value=400
        L.new(pos.outputs[0],sep.inputs[0]); L.new(sep.outputs[0],comb.inputs[0]); L.new(sep.outputs[1],comb.inputs[1])
        rc=N.new('GeometryNodeRaycast'); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=1000
        L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L.new(comb.outputs[0],rc.inputs['Source Position'])
        dl=N.new('GeometryNodeDeleteGeometry'); dl.domain='FACE'
        L.new(gi.outputs[0],dl.inputs['Geometry']); L.new(rc.outputs['Is Hit'],dl.inputs['Selection'])
        jn=N.new('GeometryNodeJoinGeometry'); L.new(oi.outputs['Geometry'],jn.inputs[0]); L.new(dl.outputs[0],jn.inputs[0]); L.new(jn.outputs[0],go.inputs[0])
        md=T.modifiers.new(MODN,'NODES'); md.node_group=ng
        newb=BVHTree.FromObject(P,bpy.context.evaluated_depsgraph_get())
        skip=('Terrain','Context_','Footpaths','Roads','OO_skirt','OR_','QF_','QE_','walls','roof','Wall','Facade','Building','BD_')
        moved=[]
        for o in bpy.data.objects:
            if o.parent or o.type not in('MESH','EMPTY','CURVE','CAMERA','LIGHT') or any(s in o.name for s in skip) or o==P: continue
            if o.type=='MESH' and len(o.data.vertices)==0: continue
            bb=[o.matrix_world@Vector(c) for c in o.bound_box]; zmin=min(v.z for v in bb); h=max(v.z for v in bb)-zmin
            if h>40 or max(v.x for v in bb)-min(v.x for v in bb)>25 or max(v.y for v in bb)-min(v.y for v in bb)>25: continue
            x,y=o.matrix_world.translation.x,o.matrix_world.translation.y; i=int(math.floor(x-X0)); j=int(math.floor(y-Y0))
            if not(0<=i<nx and 0<=j<ny) or not mark[j,i]: continue
            lo=bvh.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]; ln=newb.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
            if ln is None: continue
            if lo is None or (abs(zmin-lo.z)>0.8 and abs(o.matrix_world.translation.z-lo.z)>0.8):
                print('NOTRESTING',o.name,round(zmin,1),None if lo is None else round(lo.z,1),round(ln.z,1)); continue
            dz=ln.z-lo.z
            if abs(dz)<0.05: continue
            o.location.z+=dz; o['qh_dz']=dz; moved.append((o.name,round(dz,2)))
        print('MOVED',len(moved),moved[:30]); print('PATCH faces',len(me.polygons))

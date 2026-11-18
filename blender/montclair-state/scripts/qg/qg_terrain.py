# qg (Nov 2 2026): MAIN terrain north strip fix. Terrain_LiDAR_DTM_1m north of the LiDAR disc (y~140-262) is a fan of
# 1 m x ~270 m slivers to a hub (216.4,248.5): up to 11 m too LOW under CCIS/CELS and up to 14 m too HIGH at the east end
# vs the north LiDAR grid (north/data/grid_1m.npz dtm_filled, which matches the 3DEP skirt and the CCIS ground ring 138.55).
# Fix: patch mesh on the 1 m LiDAR lattice covering exactly the fan cells, joined into the terrain by a removable GN
# modifier (old fan faces deleted where the patch lies), feathered 4 m into the old surface at LiDAR-disc borders.
# Small objects resting on the old surface in the patch are re-seated (z shift stored in 'qg_dz'). REVERT=1 -> exact pre-qg.
import bpy, bmesh, os, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; DRY=os.environ.get('DRY')=='1'
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; PN='QG_north_strip_LiDAR_terrain_patch'; MODN='QG_north_strip_LiDAR_patch'
def rm():
    m=T.modifiers.get(MODN)
    if m:
        ng=m.node_group; T.modifiers.remove(m)
        if ng and ng.users==0: bpy.data.node_groups.remove(ng)
    p=bpy.data.objects.get(PN)
    if p: me=p.data; bpy.data.objects.remove(p,do_unlink=True); bpy.data.meshes.remove(me)
    for o in bpy.data.objects:
        if 'qg_dz' in o: o.location.z-=o['qg_dz']; del o['qg_dz']
rm()
if REV: print('QG reverted')
else:
    dg=bpy.context.evaluated_depsgraph_get(); Te=T.evaluated_get(dg); em=Te.to_mesh()
    MW=T.matrix_world
    vs=[MW@v.co for v in em.vertices]; ps=[tuple(p.vertices) for p in em.polygons]
    HUB=Vector((216.4,248.5)); hubf=[any((vs[k].to_2d()-HUB).length<1.0 for k in p.vertices) for p in em.polygons]; print('HUBFACES',sum(hubf))
    areas=[p.area for p in em.polygons]; mats=[p.material_index for p in em.polygons]
    # ortho UV affine fit (x,y)->uv
    uvl=em.uv_layers['ortho'].data; A=[];B=[]
    for pi_ in range(0,len(em.polygons),997):
        p=em.polygons[pi_]
        for li in p.loop_indices:
            v=vs[em.loops[li].vertex_index]; A.append((v.x,v.y,1)); B.append(tuple(uvl[li].uv))
    sol,res,_,_=np.linalg.lstsq(np.array(A),np.array(B),rcond=None); print('UVFIT resid',res)
    bvh=BVHTree.FromPolygons(vs,ps); Te.to_mesh_clear()
    g=np.load('north/data/grid_1m.npz'); D=g['dtm_filled']
    X0,X1,Y0,Y1=-220,222,100,263
    nx,ny=X1-X0,Y1-Y0
    mark=np.zeros((ny,nx),bool); hit=np.zeros((ny,nx),bool); cmat=np.zeros((ny,nx),int)
    for j in range(ny):
        for i in range(nx):
            x=X0+i+0.5; y=Y0+j+0.5
            loc,n,fi,d=bvh.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
            if loc is None: continue
            hit[j,i]=True; cmat[j,i]=mats[fi]; a=areas[fi]
            if hubf[fi] or (80<=x<=205 and 120<=y<=262 and a<0.3): mark[j,i]=True
    print('CELLS marked',mark.sum(),'hit',hit.sum())
    # distance (cells) to nearest hit-but-unmarked cell (feather source)
    src=hit&~mark; dist=np.full((ny,nx),99.0)
    pts=np.argwhere(src)
    cur=src.copy(); dist[src]=0
    for k in range(1,7):
        nb=cur.copy(); nb[1:,:]|=cur[:-1,:]; nb[:-1,:]|=cur[1:,:]; nb[:,1:]|=cur[:,:-1]; nb[:,:-1]|=cur[:,1:]
        dist[nb&~cur]=k; cur=nb
    def lid(x,y):  # vertex value: mean of 4 cells
        r=int(y+260); c=int(x+600); return float(D[r-1:r+1,c-1:c+1].mean())
    if DRY:
        print('DRY'); 
    else:
        bm=bmesh.new(); vid={}
        uvL=bm.loops.layers.uv.new('ortho')
        def vert(i,j):
            if (i,j) in vid: return vid[(i,j)]
            x=X0+i; y=Y0+j; z=lid(x,y)
            dd=min(dist[min(j,ny-1)][min(i,nx-1)], dist[max(j-1,0)][max(i-1,0)], dist[min(j,ny-1)][max(i-1,0)], dist[max(j-1,0)][min(i,nx-1)])
            if dd<4.5:
                loc,n,fi,d=bvh.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
                if loc is not None:
                    w=max(0.0,(dd-0.5)/4.0); w=w*w*(3-2*w); z=loc.z*(1-w)+z*w
            v=bm.verts.new((x,y,z)); vid[(i,j)]=v; return v
        for j in range(ny):
            for i in range(nx):
                if not mark[j,i]: continue
                f=bm.faces.new([vert(i,j),vert(i+1,j),vert(i+1,j+1),vert(i,j+1)]); f.material_index=int(cmat[j,i]); f.smooth=True
                for l in f.loops:
                    co=l.vert.co; l[uvL].uv=(sol[0,0]*co.x+sol[1,0]*co.y+sol[2,0], sol[0,1]*co.x+sol[1,1]*co.y+sol[2,1])
        me=bpy.data.meshes.new(PN); bm.to_mesh(me); bm.free()
        for m in T.data.materials: me.materials.append(m)
        P=bpy.data.objects.new(PN,me); P['qg']=1
        T.users_collection[0].objects.link(P); P.hide_render=True; P.hide_viewport=True
        # GN: delete terrain faces whose centre lies over the patch, join the patch
        ng=bpy.data.node_groups.new(MODN+'_GN','GeometryNodeTree')
        ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
        N=ng.nodes; L=ng.links
        gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
        oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=P; oi.transform_space='ORIGINAL'
        pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); comb=N.new('ShaderNodeCombineXYZ'); comb.inputs['Z'].default_value=400
        L.new(pos.outputs[0],sep.inputs[0]); L.new(sep.outputs[0],comb.inputs[0]); L.new(sep.outputs[1],comb.inputs[1])
        rc=N.new('GeometryNodeRaycast'); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=1000
        L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L.new(comb.outputs[0],rc.inputs['Source Position'])
        dl=N.new('GeometryNodeDeleteGeometry'); dl.domain='FACE'
        L.new(gi.outputs[0],dl.inputs['Geometry']); L.new(rc.outputs['Is Hit'],dl.inputs['Selection'])
        jn=N.new('GeometryNodeJoinGeometry'); L.new(oi.outputs['Geometry'],jn.inputs[0]); L.new(dl.outputs[0],jn.inputs[0])
        L.new(jn.outputs[0],go.inputs[0])
        md=T.modifiers.new(MODN,'NODES'); md.node_group=ng
        # re-seat small objects resting on the old surface
        newb=BVHTree.FromObject(P,bpy.context.evaluated_depsgraph_get())
        skip=('Terrain','Context_','Footpaths','Roads','OO_skirt','OR_','QF_','QE_','walls','roof','Wall','Facade','Building')
        moved=[]
        for o in bpy.data.objects:
            if o.parent or o.type not in('MESH','EMPTY','CURVE','CAMERA','LIGHT') or any(s in o.name for s in skip) or o==P: continue
            if o.type=='MESH' and len(o.data.vertices)==0: continue
            bb=[o.matrix_world@Vector(c) for c in o.bound_box]; zmin=min(v.z for v in bb); h=max(v.z for v in bb)-zmin
            dx=max(v.x for v in bb)-min(v.x for v in bb); dyy=max(v.y for v in bb)-min(v.y for v in bb)
            if h>30 or dx>25 or dyy>25: continue
            x,y=o.matrix_world.translation.x,o.matrix_world.translation.y
            i=int(math.floor(x-X0)); j=int(math.floor(y-Y0))
            if not(0<=i<nx and 0<=j<ny) or not mark[j,i]: continue
            lo,_,_,_=bvh.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); ln,_,_,_=newb.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
            if lo is None or ln is None: continue
            if o.type in('CAMERA','LIGHT'):
                if not(-0.5<o.matrix_world.translation.z-lo.z<6.0) and not(o.type=='CAMERA' and o.matrix_world.translation.z<ln.z+1.2): continue
            elif abs(zmin-lo.z)>0.8 and abs(o.matrix_world.translation.z-lo.z)>0.8: continue
            dz=ln.z-lo.z
            if o.type=='CAMERA': dz=max(dz,ln.z+1.7-o.matrix_world.translation.z) if o.matrix_world.translation.z<ln.z+1.2 else dz
            if abs(dz)<0.05: continue
            o.location.z+=dz; o['qg_dz']=dz; moved.append((o.name,round(dz,2)))
        print('MOVED',len(moved),moved[:40])
        print('PATCH faces',len(me.polygons))

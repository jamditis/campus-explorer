# qj (Nov 2 2026): NE terrain/skirt seam (x~214-236, y 140-252). qi left the flat-extrapolated terrain edge 0.4-2 m above the
# 3DEP skirt (a step/dark fold) and ~100 one-cell see-through slivers where the skirt is cut but no terrain lies.
# (1) removable GN 'QJ_NE_seam_ramp' (last on Terrain_LiDAR_DTM_1m) raycasts a hidden helper grid 'QJ_NE_seam_ramp_field'
#     whose z = dz and lowers the terrain over a 12 m smoothstep so its NE edge meets the skirt (all terrain parts move
#     together, no cracks). (2) 'QJ_NE_seam_fill_UNVERIFIED' 0.5 m fill cells (terrain material + ortho UV) close the
#     see-through cells, tucked 3 cm under. (3) trees/lamps/benches (qj_dz) and PC_* grass points (per vertex, backup npz)
#     follow. APPROXIMATE (terrain there is a flat extrapolation; skirt is 3DEP). REVERT=1 -> exact pre-qj.
import bpy, bmesh, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; S=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
MODN='QJ_NE_seam_ramp'; HN='QJ_NE_seam_ramp_field'; FN='QJ_NE_seam_fill_UNVERIFIED'; BAK='data/qj/drape_bak.npz'
DN=Vector((0,0,-1))
def rm():
    m=T.modifiers.get(MODN)
    if m:
        ng=m.node_group; T.modifiers.remove(m)
        if ng and ng.users==0: bpy.data.node_groups.remove(ng)
    for nm in (HN,FN):
        p=bpy.data.objects.get(nm)
        if p: me=p.data; bpy.data.objects.remove(p,do_unlink=True); bpy.data.meshes.remove(me)
    for o in bpy.data.objects:
        if 'qj_dz' in o: o.location.z-=o['qj_dz']; del o['qj_dz']
    if os.path.exists(BAK):
        z=np.load(BAK)
        for k in z.files:
            o=bpy.data.objects.get(k)
            if o and o.get('qj_drape'): o.data.vertices.foreach_set('co',z[k].ravel()); o.data.update(); del o['qj_drape']
rm()
def holes(bt,bs):
    n=0;H=[]
    for y in np.arange(140.25,252,0.5):
        for x in np.arange(205.25,240,0.5):
            if bt.ray_cast(Vector((x,y,500)),DN)[0] is None and bs.ray_cast(Vector((x,y,500)),DN)[0] is None: n+=1; H.append((x,y))
    return n,H
if REV: print('QJ reverted')
else:
    dg=bpy.context.evaluated_depsgraph_get(); bt=BVHTree.FromObject(T,dg); bs=BVHTree.FromObject(S,dg)
    n0,_=holes(bt,bs); print('HOLES before',n0)
    Y=np.arange(140.0,252.01,0.5); XE=np.full(len(Y),np.nan); ZT=XE.copy(); ZS=XE.copy(); SB=np.zeros(len(Y))
    for k,y in enumerate(Y):
        xe=None
        for x in np.arange(252,200,-0.25):
            h=bt.ray_cast(Vector((x,y,500)),DN)[0]
            if h is not None: xe=x; ZT[k]=h.z; break
        if xe is None: continue
        XE[k]=xe; pts=[]
        for x in np.arange(xe+0.25,xe+12,0.25):
            h=bs.ray_cast(Vector((x,y,500)),DN)[0]
            if h is not None: pts.append((x,h.z))
            if len(pts)>=8: break
        if len(pts)>=3:
            P=np.array(pts); b,a=np.polyfit(P[:,0],P[:,1],1); ZS[k]=a+b*xe; SB[k]=b
    ok=~np.isnan(XE)&~np.isnan(ZS)
    print('ROWS',len(Y),'with edge',int((~np.isnan(XE)).sum()),'with skirt',int(ok.sum()))
    def fill(a):
        a=a.copy(); i=np.arange(len(a)); g=~np.isnan(a); a[~g]=np.interp(i[~g],i[g],a[g]); return a
    XEf=fill(XE); D=fill(np.where(ok,ZS-0.02-ZT,np.nan)); SBf=fill(np.where(ok,SB,np.nan)); ZSf=fill(np.where(ok,ZS,np.nan))
    def smooth(a,w=11):
        k=np.ones(w)/w; p=np.pad(a,(w//2,w//2),mode='edge'); return np.convolve(p,k,'valid')
    XEs=smooth(XEf); Ds=smooth(D,7); Ds=np.minimum(Ds,0.0)   # only lower the terrain toward the skirt
    tap=np.clip((Y-140)/8.0,0,1); tap=tap*tap*(3-2*tap); Ds*=tap
    print('DELTA min/mean',round(float(Ds.min()),2),round(float(Ds.mean()),2),'XEs range',round(float(XEs.min()),1),round(float(XEs.max()),1))
    R=12.0
    def dz_at(x,y):
        k=int(np.clip(round((y-140.0)/0.5),0,len(Y)-1)); d=XEs[k]+1.0-x
        if d<=0: return float(Ds[k])
        if d>=R: return 0.0
        w=1-d/R; return float(Ds[k]*w*w*(3-2*w))
    # helper field grid
    bm=bmesh.new(); vid={}
    xs=np.arange(190.0,240.01,0.5); ys=np.arange(138.0,253.01,0.5)
    for j,y in enumerate(ys):
        for i,x in enumerate(xs): vid[(i,j)]=bm.verts.new((x,y,dz_at(x,y)))
    for j in range(len(ys)-1):
        for i in range(len(xs)-1): bm.faces.new([vid[(i,j)],vid[(i+1,j)],vid[(i+1,j+1)],vid[(i,j+1)]])
    me=bpy.data.meshes.new(HN); bm.to_mesh(me); bm.free()
    H=bpy.data.objects.new(HN,me); H['qj']=1; T.users_collection[0].objects.link(H); H.hide_render=True; H.hide_viewport=True
    ng=bpy.data.node_groups.new(MODN+'_GN','GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=H; oi.transform_space='ORIGINAL'
    pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); comb=N.new('ShaderNodeCombineXYZ'); comb.inputs['Z'].default_value=400
    L.new(pos.outputs[0],sep.inputs[0]); L.new(sep.outputs[0],comb.inputs[0]); L.new(sep.outputs[1],comb.inputs[1])
    rc=N.new('GeometryNodeRaycast'); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=1000
    L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L.new(comb.outputs[0],rc.inputs['Source Position'])
    s2=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],s2.inputs[0]); c2=N.new('ShaderNodeCombineXYZ'); L.new(s2.outputs[2],c2.inputs[2])
    sp=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],sp.inputs['Geometry']); L.new(rc.outputs['Is Hit'],sp.inputs['Selection']); L.new(c2.outputs[0],sp.inputs['Offset'])
    L.new(sp.outputs[0],go.inputs[0]); md=T.modifiers.new(MODN,'NODES'); md.node_group=ng
    dg=bpy.context.evaluated_depsgraph_get(); bt2=BVHTree.FromObject(T,dg)
    # fill cells
    Te=T.evaluated_get(dg); em=Te.to_mesh(); MW=T.matrix_world
    vs=[MW@v.co for v in em.vertices]; uvl=em.uv_layers['ortho'].data; A_=[];B_=[]
    for pi_ in range(0,len(em.polygons),997):
        p=em.polygons[pi_]
        for li in p.loop_indices:
            v=vs[em.loops[li].vertex_index]; A_.append((v.x,v.y,1)); B_.append(tuple(uvl[li].uv))
    sol=np.linalg.lstsq(np.array(A_),np.array(B_),rcond=None)[0]
    mats=[p.material_index for p in em.polygons]; Te.to_mesh_clear()
    gx=np.arange(205.0,240.0,0.5); gy=np.arange(140.0,252.0,0.5); cell=np.zeros((len(gy),len(gx)),bool); mi=[]
    for j,y in enumerate(gy):
        for i,x in enumerate(gx):
            for ox,oy in ((.25,.25),(.05,.05),(.45,.05),(.05,.45),(.45,.45)):
                q=Vector((x+ox,y+oy,500))
                if bt2.ray_cast(q,DN)[0] is None and bs.ray_cast(q,DN)[0] is None: cell[j,i]=True; break
    nc=int(cell.sum()); c2_=cell.copy(); c2_[1:,:]|=cell[:-1,:]; c2_[:-1,:]|=cell[1:,:]; c2_[:,1:]|=cell[:,:-1]; c2_[:,:-1]|=cell[:,1:]; cell=c2_
    for j,y in enumerate(gy):
        for i,x in enumerate(gx):
            if cell[j,i]:
                h=bt2.ray_cast(Vector((x-1.5,y+.25,500)),DN)
                if h[0] is None:
                    for dx in np.arange(2,8,0.5):
                        h=bt2.ray_cast(Vector((x-dx,y+.25,500)),DN)
                        if h[0] is not None: break
                if h[0] is not None: mi.append(mats[h[2]]) if h[2] is not None and h[2]<len(mats) else None
    common=int(np.bincount(mi).argmax()) if mi else 0
    bm=bmesh.new(); uvL=bm.loops.layers.uv.new('ortho'); fv={}
    def fz(x,y):
        q=Vector((x,y,500)); h=bt2.ray_cast(q,DN)[0]
        if h is not None: return h.z-0.03
        h=bs.ray_cast(q,DN)[0]
        if h is not None: return h.z-0.03
        k=int(np.clip(round((y-140.0)/0.5),0,len(Y)-1)); return float(ZSf[k]+SBf[k]*(x-XEf[k]))-0.03
    def vert(i,j):
        if (i,j) not in fv: x=205.0+0.5*i; y=140.0+0.5*j; fv[(i,j)]=bm.verts.new((x,y,fz(x,y)))
        return fv[(i,j)]
    for j in range(len(gy)):
        for i in range(len(gx)):
            if not cell[j,i]: continue
            f=bm.faces.new([vert(i,j),vert(i+1,j),vert(i+1,j+1),vert(i,j+1)]); f.material_index=common; f.smooth=True
            for l in f.loops:
                co=l.vert.co; l[uvL].uv=(sol[0,0]*co.x+sol[1,0]*co.y+sol[2,0], sol[0,1]*co.x+sol[1,1]*co.y+sol[2,1])
    me=bpy.data.meshes.new(FN); bm.to_mesh(me); bm.free()
    for m in T.data.materials: me.materials.append(m)
    F=bpy.data.objects.new(FN,me); F['qj']=1; T.users_collection[0].objects.link(F)
    print('FILL cells raw',nc,'with margin',int(cell.sum()),'mat',common)
    dg=bpy.context.evaluated_depsgraph_get(); bt3=BVHTree.FromObject(T,dg); bf=BVHTree.FromObject(F,dg)
    n1=0
    for y in np.arange(140.25,252,0.5):
        for x in np.arange(205.25,240,0.5):
            q=Vector((x,y,500))
            if bt3.ray_cast(q,DN)[0] is None and bs.ray_cast(q,DN)[0] is None and bf.ray_cast(q,DN)[0] is None: n1+=1
    print('HOLES after',n1)
    # edge step after: terrain z at edge minus skirt z just outside
    st=[]
    for k in range(0,len(Y),4):
        y=Y[k]; xe=XEf[k]; a=bt3.ray_cast(Vector((xe-0.5,y,500)),DN)[0]; b=bs.ray_cast(Vector((xe+2.5,y,500)),DN)[0]
        if a is not None and b is not None: st.append(round(a.z-b.z,2))
    print('EDGE step terrain-skirt(2.5m out) after',st)
    # reseat objects
    moved=[]; bak={}; dr=[]
    for o in bpy.data.objects:
        if o.parent or o.name.startswith(('Terrain','Context_','QJ_')): continue
        x,y,z=o.matrix_world.translation
        if not(190<=x<=240 and 138<=y<=253): continue
        if o.name.startswith(('T_','Lamp_','Bench_')) and not o.hide_render:
            d=dz_at(x,y)
            if abs(d)>=0.02: o.location.z+=d; o['qj_dz']=d; moved.append((o.name,round(d,2)))
    for o in bpy.data.objects:
        if o.type!='MESH' or o.parent or not (o.name.startswith('PC_') or o.name.startswith('Furniture contact')): continue
        n=len(o.data.vertices)
        if n==0: continue
        co=np.zeros(n*3,np.float32); o.data.vertices.foreach_get('co',co); co=co.reshape(n,3); M=np.array(o.matrix_world)
        if abs(np.linalg.det(M[:3,:3])-1)>1e-3: continue
        W=co@M[:3,:3].T+M[:3,3]; sel=np.nonzero((W[:,0]>=190)&(W[:,0]<=240)&(W[:,1]>=138)&(W[:,1]<=253))[0]
        if len(sel)==0: continue
        d=np.array([dz_at(W[i,0],W[i,1]) for i in sel])
        if not np.any(np.abs(d)>0.02): continue
        bak[o.name]=co.copy(); W[sel,2]+=d; co2=(W-M[:3,3])@np.linalg.inv(M[:3,:3]).T
        o.data.vertices.foreach_set('co',co2.astype(np.float32).ravel()); o.data.update(); o['qj_drape']=1; dr.append((o.name,len(sel)))
    if bak: np.savez(BAK,**bak)
    print('MOVED',len(moved),moved[:30]); print('DRAPED',dr)

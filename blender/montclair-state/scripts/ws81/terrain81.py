# ws78: lower-only pull of the RHD/Sprague lot pocket (x -252..-216, y -126..-83; terrain 1.0-1.9 m ABOVE the 1 m DTM, both north grid and main dtm agree) onto the DTM. Derived from ws67/terrain67_base.py.
# ws64: pull the big-triangle terrain north of Kasser (x -238..-208, y 2..36; +2..3.3 m and -1.5..-2.3 m off the 2023 1 m DTM, bare ground) onto the DTM; same method as ws63
# onto the DTM with a feathered, boxed GN modifier at the end of the terrain stack (like QM_terrain_band_to_DTM). Pavement re-drapes.
# Idempotent. SAVE=1 saves. REVERT=1 removes modifier + helper.
import bpy, bmesh, numpy as np, os
from mathutils import Vector
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; MN='WS81_grandstand_lawn_band_to_DTM_lower_only'; HN='WS81_grandstand_lawn_DTM_target'
CX0,CX1,CY0,CY1=-252.0,-233.5,-136.0,-123.0; F=3.0; OX0,OX1,OY0,OY1=CX0-F-2,CX1+F+2,CY0-F-2,CY1+F+2
if os.environ.get('REVERT81')=='1':
    m=T.modifiers.get(MN); 
    if m: T.modifiers.remove(m)
    h=bpy.data.objects.get(HN)
    if h: bpy.data.objects.remove(h)
    g=bpy.data.node_groups.get(MN)
    if g: bpy.data.node_groups.remove(g)
    print('R78 reverted'); 
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('R78 saved')
    raise SystemExit
done=T.modifiers.get(MN) is not None
if not done:
    D=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy').astype(np.float64)
    # v2: soften 1 m DTM facets (2x 3x3 box blur, ~1 m sigma) so the real step reads as a bank, not a faceted berm
    for _ in range(int(os.environ.get('BLUR','2'))):
        P=np.pad(D,1,mode='edge'); D=sum(P[1+a:P.shape[0]-1+a,1+b:P.shape[1]-1+b] for a in (-1,0,1) for b in (-1,0,1))/9.0
    xs=list(range(int(OX0)-1,int(OX1)+2)); ys=list(range(int(OY0)-1,int(OY1)+2))
    me=bpy.data.meshes.new(HN); verts=[(x,y,float(D[y+250,max(x,-250)+250])) for y in ys for x in xs]; nx=len(xs)
    faces=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(len(ys)-1) for i in range(nx-1)]
    me.from_pydata(verts,[],faces); h=bpy.data.objects.new(HN,me)
    probe=bpy.data.objects.get('QI_east_edge_delete_probe'); (probe.users_collection[0] if (probe and probe.users_collection) else bpy.context.scene.collection).objects.link(h)
    h.hide_render=True; h.hide_viewport=False; h.display_type='WIRE'; h.visible_camera=False; h.visible_shadow=False; h.visible_diffuse=False; h.visible_glossy=False; h.visible_transmission=False; h.visible_volume_scatter=False
    g=bpy.data.node_groups.new(MN,'GeometryNodeTree')
    g.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); g.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=g.nodes; L=g.links
    gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sep.inputs[0])
    def cmp(sock,val,op):
        c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L.new(sock,c.inputs[0]); c.inputs[1].default_value=val; return c.outputs[0]
    def band(a,b):
        n=N.new('FunctionNodeBooleanMath'); n.operation='AND'; L.new(a,n.inputs[0]); L.new(b,n.inputs[1]); return n.outputs[0]
    insel=band(band(cmp(sep.outputs[0],OX0,'GREATER_THAN'),cmp(sep.outputs[0],OX1,'LESS_THAN')),band(cmp(sep.outputs[1],OY0,'GREATER_THAN'),cmp(sep.outputs[1],OY1,'LESS_THAN')))
    # the band is spanned by a few huge base triangles (only 2 eval verts in the core) -> also take big faces near the core and densify them
    fa=N.new('GeometryNodeInputMeshFaceArea'); big=cmp(fa.outputs[0],20.0,'GREATER_THAN')
    dxy=N.new('ShaderNodeVectorMath'); dxy.operation='SUBTRACT'; L.new(pos.outputs[0],dxy.inputs[0]); dxy.inputs[1].default_value=((CX0+CX1)/2,(CY0+CY1)/2,0)
    sx2=N.new('ShaderNodeSeparateXYZ'); L.new(dxy.outputs[0],sx2.inputs[0])
    cxy=N.new('ShaderNodeCombineXYZ'); L.new(sx2.outputs[0],cxy.inputs[0]); L.new(sx2.outputs[1],cxy.inputs[1])
    ln=N.new('ShaderNodeVectorMath'); ln.operation='LENGTH'; L.new(cxy.outputs[0],ln.inputs[0])
    near=cmp(ln.outputs['Value'],float(os.environ.get('NEAR','35')),'LESS_THAN')
    orr=N.new('FunctionNodeBooleanMath'); orr.operation='OR'; L.new(insel,orr.inputs[0]); L.new(band(big,near),orr.inputs[1])
    sg=N.new('GeometryNodeSeparateGeometry'); sg.domain='FACE'; L.new(gi.outputs[0],sg.inputs['Geometry']); L.new(orr.outputs[0],sg.inputs['Selection'])
    sg2=N.new('GeometryNodeSeparateGeometry'); sg2.domain='FACE'; L.new(sg.outputs['Selection'],sg2.inputs['Geometry']); L.new(big,sg2.inputs['Selection'])
    sb=N.new('GeometryNodeSubdivideMesh'); sb.inputs['Level'].default_value=int(os.environ.get('LV','6')); L.new(sg2.outputs['Selection'],sb.inputs['Mesh'])
    j0=N.new('GeometryNodeJoinGeometry'); L.new(sg2.outputs['Inverted'],j0.inputs[0]); L.new(sb.outputs[0],j0.inputs[0])
    class _S: pass
    sub=_S(); sub.outputs=[j0.outputs[0]]
    # weight: distance to core rect -> smoothstep 1..0 over F
    def m2(op,a,b=None,bv=None):
        n=N.new('ShaderNodeMath'); n.operation=op; L.new(a,n.inputs[0])
        if b is not None: L.new(b,n.inputs[1])
        elif bv is not None: n.inputs[1].default_value=bv
        return n.outputs[0]
    def neg(a): return m2('MULTIPLY',a,bv=-1.0)
    dx=m2('MAXIMUM',m2('MAXIMUM',m2('SUBTRACT',sep.outputs[0],bv=CX1),neg(m2('SUBTRACT',sep.outputs[0],bv=CX0))),bv=0.0)
    dy=m2('MAXIMUM',m2('MAXIMUM',m2('SUBTRACT',sep.outputs[1],bv=CY1),neg(m2('SUBTRACT',sep.outputs[1],bv=CY0))),bv=0.0)
    d=m2('SQRT',m2('ADD',m2('MULTIPLY',dx,dx),m2('MULTIPLY',dy,dy)))
    mr=N.new('ShaderNodeMapRange'); mr.interpolation_type='SMOOTHSTEP'; L.new(d,mr.inputs['Value']); mr.inputs['From Min'].default_value=0; mr.inputs['From Max'].default_value=F; mr.inputs['To Min'].default_value=1; mr.inputs['To Max'].default_value=0
    oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; oi.inputs['Object'].default_value=h
    rc=N.new('GeometryNodeRaycast'); L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry'])
    up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; L.new(pos.outputs[0],up.inputs[0]); up.inputs[1].default_value=(0,0,200)
    L.new(up.outputs[0],rc.inputs['Source Position']); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=500
    hs=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],hs.inputs[0])
    w=m2('MULTIPLY',mr.outputs['Result'],rc.outputs['Is Hit'])
    mix=N.new('ShaderNodeMix'); mix.data_type='FLOAT'; L.new(w,mix.inputs['Factor']); L.new(sep.outputs[2],mix.inputs['A']); L.new(hs.outputs[2],mix.inputs['B'])
    mn=m2('MINIMUM',mix.outputs['Result'],sep.outputs[2]); cb=N.new('ShaderNodeCombineXYZ'); L.new(sep.outputs[0],cb.inputs[0]); L.new(sep.outputs[1],cb.inputs[1]); L.new(mn,cb.inputs[2])
    sp=N.new('GeometryNodeSetPosition'); L.new(sub.outputs[0],sp.inputs['Geometry']); L.new(cb.outputs[0],sp.inputs['Position'])
    j=N.new('GeometryNodeJoinGeometry'); L.new(sg.outputs['Inverted'],j.inputs[0]); L.new(sp.outputs[0],j.inputs[0])
    mg=N.new('GeometryNodeMergeByDistance'); mg.inputs['Distance'].default_value=0.0005; L.new(j.outputs[0],mg.inputs['Geometry'])
    L.new(mg.outputs[0],go.inputs[0])
    mod=T.modifiers.new(MN,'NODES'); mod.node_group=g
    print('A78 applied')
else: print('A78 already')
# verify: evaluated terrain vs DTM on a 2 m grid in the core, and band trees in the box
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
from mathutils.bvhtree import BVHTree
m=T.evaluated_get(dg).to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(T.matrix_world); BV=BVHTree.FromBMesh(bm)
D=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy'); diffs=[]; core=[]
for y in range(int(OY0)+1,int(OY1),2):
    for x in range(int(OX0)+1,int(OX1),2):
        hh=BV.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0]
        dd=abs(hh.z-D[y+250,max(x,-250)+250]) if hh else 99
        diffs.append(dd)
        if CX0<=x<=CX1 and CY0<=y<=CY1: core.append(dd)
diffs=np.array(diffs); print('V78 cells',len(diffs),'>0.3m',int((diffs>0.3).sum()),'>1m',int((diffs>1).sum()),'miss',int((diffs==99).sum()),'max',round(float(diffs[diffs<99].max()),2))
core=np.array(core); print('V78 core',len(core),'>0.3',int((core>0.3).sum()),'max',round(float(core.max()),2),'mean',round(float(core.mean()),3)); print('V78 polys',len(m.polygons)); import time

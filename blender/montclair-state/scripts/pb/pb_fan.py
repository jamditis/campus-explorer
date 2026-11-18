# pb (UNVERIFIED, removable; REVERT=1 undoes): smooth the stair-stepped LiDAR-edge 'fan' in the north strip (CELS/Calcia lawn bank).
# Cause (pa): outside the LiDAR disc Terrain_LiDAR_DTM_1m is a fan of 1 m-wide x ~270 m sliver triangles from the stair-stepped disc
# edge to a tile-corner hub (216.4,248.5); the slivers form radial ridges -> stair steps at eye level.
# Fix ON THE TERRAIN ITSELF: GN modifier PB_terrain_fan_regrid (group PB_terrain_fan_regrid_GN): fan faces (mean edge > AMIN) are split off,
# subdivided (LEVEL), and their vertices moved toward a smooth height field (0.5 m grid ray-cast onto the original terrain, hit-weighted
# blur BI iterations) by w*clamp(dz,+-CLAMP); w = 0 on the fan's own boundary (no cracks: boundary verts stay on the original edges)
# and outside the BOX (feathered FW m). Rejoined + merged at the seam. Walks/roads/skirt GNs that ray-cast the terrain follow it.
# Terrain mesh, material and UV data unedited; dz stored in point attr 'pb_dz' (evaluated only).
import bpy, os, sys
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
MN='PB_terrain_fan_regrid'; NG='PB_terrain_fan_regrid_GN'
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
if MN in T.modifiers: T.modifiers.remove(T.modifiers[MN])
if NG in bpy.data.node_groups: bpy.data.node_groups.remove(bpy.data.node_groups[NG])
for k in ('pb_fan_regrid',):
    if k in T: del T[k]
CC='PB_cams_20261101pb'
c=bpy.data.collections.get(CC)
if c:
    for o in list(c.objects):
        d=o.data; bpy.data.objects.remove(o)
        if d and d.users==0: bpy.data.cameras.remove(d)
    bpy.data.collections.remove(c)
if REV:
    print('REVERTED_PB_FAN')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
E=os.environ.get
X0,X1,Y0,Y1=[float(q) for q in E('BOX','80,205,120,262').split(',')]
RES=float(E('RES_G','0.5')); BI=int(E('BI','40')); AMIN=float(E('AMIN','2.0')); FW=float(E('FW','5.0')); FB=float(E('FB','6.0'))
CL=float(E('CLAMP','0.15')); LEVEL=int(E('LEVEL','5'))
ng=bpy.data.node_groups.new(NG,'GeometryNodeTree'); I=ng.interface
I.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); I.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
G=gi.outputs[0]
def FM(op,a=None,b=None,c=None,clamp=False):
    n=N.new('ShaderNodeMath'); n.operation=op; n.use_clamp=clamp
    for i,vv in ((0,a),(1,b),(2,c)):
        if vv is None: continue
        if isinstance(vv,(int,float)): n.inputs[i].default_value=vv
        else: L(vv,n.inputs[i])
    return n.outputs[0]
def store(geo,name,val,dt='FLOAT',dom='POINT'):
    s=N.new('GeometryNodeStoreNamedAttribute'); s.data_type=dt; s.domain=dom; s.inputs['Name'].default_value=name; L(geo,s.inputs['Geometry']); L(val,s.inputs['Value']); return s.outputs['Geometry']
def named(name,dt='FLOAT'):
    n=N.new('GeometryNodeInputNamedAttribute'); n.data_type=dt; n.inputs['Name'].default_value=name; return n.outputs['Attribute']
def sstep(v,a,b):
    m=N.new('ShaderNodeMapRange'); m.interpolation_type='SMOOTHSTEP'; L(v,m.inputs['Value']); m.inputs['From Min'].default_value=a; m.inputs['From Max'].default_value=b; return m.outputs['Result']
def xyz(): 
    p=N.new('GeometryNodeInputPosition'); s=N.new('ShaderNodeSeparateXYZ'); L(p.outputs[0],s.inputs[0]); return s
# fan face mask: mean edge length > AMIN
ev=N.new('GeometryNodeInputMeshEdgeVertices'); el=N.new('ShaderNodeVectorMath'); el.operation='DISTANCE'; L(ev.outputs['Position 1'],el.inputs[0]); L(ev.outputs['Position 2'],el.inputs[1])
fd=N.new('GeometryNodeFieldOnDomain'); fd.domain='FACE'; fd.data_type='FLOAT'; L(el.outputs['Value'],fd.inputs[0])
fan=FM('GREATER_THAN',fd.outputs[0],AMIN)
# only fan faces touching the box (+2 m): keeps the subdivision local
sv=xyz(); inb=FM('MULTIPLY',FM('MULTIPLY',FM('GREATER_THAN',sv.outputs['X'],X0-2),FM('LESS_THAN',sv.outputs['X'],X1+2)),FM('MULTIPLY',FM('GREATER_THAN',sv.outputs['Y'],Y0-2),FM('LESS_THAN',sv.outputs['Y'],Y1+2)))
fb=N.new('GeometryNodeFieldOnDomain'); fb.domain='FACE'; fb.data_type='FLOAT'; L(inb,fb.inputs[0])
fan=FM('MULTIPLY',fan,FM('GREATER_THAN',fb.outputs[0],0.01))
sep=N.new('GeometryNodeSeparateGeometry'); sep.domain='FACE'; L(G,sep.inputs['Geometry']); L(fan,sep.inputs['Selection'])
A=sep.outputs['Selection']; B=sep.outputs['Inverted']
sd=N.new('GeometryNodeSubdivideMesh'); L(A,sd.inputs['Mesh']); sd.inputs['Level'].default_value=LEVEL
A=sd.outputs['Mesh']
# boundary of the fan region
en=N.new('GeometryNodeInputMeshEdgeNeighbors'); eb=FM('LESS_THAN',en.outputs['Face Count'],1.5)
sb=N.new('GeometryNodeSeparateGeometry'); sb.domain='EDGE'; L(A,sb.inputs['Geometry']); L(eb,sb.inputs['Selection'])
pd=N.new('GeometryNodeProximity'); pd.target_element='EDGES'; L(sb.outputs['Selection'],pd.inputs[0])
# smooth height field: grid ray-cast onto the ORIGINAL terrain, hit-weighted blur
gr=N.new('GeometryNodeMeshGrid'); gr.inputs['Size X'].default_value=X1-X0; gr.inputs['Size Y'].default_value=Y1-Y0
gr.inputs['Vertices X'].default_value=int((X1-X0)/RES)+1; gr.inputs['Vertices Y'].default_value=int((Y1-Y0)/RES)+1
tf=N.new('GeometryNodeTransform'); L(gr.outputs['Mesh'],tf.inputs['Geometry']); tf.inputs['Translation'].default_value=((X0+X1)/2,(Y0+Y1)/2,0)
s0=xyz(); src=N.new('ShaderNodeCombineXYZ'); L(FM('ADD',s0.outputs['X'],0.0131),src.inputs['X']); L(FM('ADD',s0.outputs['Y'],0.0077),src.inputs['Y']); src.inputs['Z'].default_value=400
rc=N.new('GeometryNodeRaycast'); L(G,rc.inputs['Target Geometry']); L(src.outputs[0],rc.inputs['Source Position']); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=1000
hz=N.new('ShaderNodeSeparateXYZ'); L(rc.outputs['Hit Position'],hz.inputs[0])
g=store(tf.outputs['Geometry'],'pb_h',rc.outputs['Is Hit'])
g=store(g,'pb_hz',FM('MULTIPLY',hz.outputs['Z'],rc.outputs['Is Hit']))
def blur(v,it):
    b=N.new('GeometryNodeBlurAttribute'); b.data_type='FLOAT'; L(v,b.inputs['Value']); b.inputs['Iterations'].default_value=it; return b.outputs['Value']
g=store(g,'pb_zs',FM('DIVIDE',blur(named('pb_hz'),BI),FM('MAXIMUM',blur(named('pb_h'),BI),1e-4)))
g=store(g,'pb_cov',blur(named('pb_h'),BI))
# sample field at fan verts
s1=xyz(); sp=N.new('ShaderNodeCombineXYZ'); L(s1.outputs['X'],sp.inputs['X']); L(s1.outputs['Y'],sp.inputs['Y'])
ns=N.new('GeometryNodeSampleNearestSurface'); ns.data_type='FLOAT'; L(g,ns.inputs['Mesh']); L(named('pb_zs'),ns.inputs['Value']); L(sp.outputs[0],ns.inputs['Sample Position'])
nc=N.new('GeometryNodeSampleNearestSurface'); nc.data_type='FLOAT'; L(g,nc.inputs['Mesh']); L(named('pb_cov'),nc.inputs['Value']); L(sp.outputs[0],nc.inputs['Sample Position'])
bx=FM('MULTIPLY',FM('MULTIPLY',sstep(s1.outputs['X'],X0,X0+FB),sstep(FM('SUBTRACT',X1,s1.outputs['X']),0,FB)),FM('MULTIPLY',sstep(s1.outputs['Y'],Y0,Y0+FB),sstep(FM('SUBTRACT',Y1,s1.outputs['Y']),0,FB)))
w=FM('MULTIPLY',FM('MULTIPLY',bx,sstep(pd.outputs['Distance'],0.0,FW)),FM('GREATER_THAN',nc.outputs[0],0.9))
# keep the ground unchanged within SK0 m of the static OO context-wall skirts (base course, sill drips, gap fillers sit on the old DTM)
SK0=float(E('SK0','2.0')); SK1=float(E('SK1','7.0'))
for on_ in [o.name for o in bpy.data.objects if o.name.startswith('OO_skirt_') and o.type=='MESH']:
    oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; oi.inputs['Object'].default_value=bpy.data.objects[on_]
    px=N.new('GeometryNodeProximity'); px.target_element='FACES'; L(oi.outputs['Geometry'],px.inputs[0])
    w=FM('MULTIPLY',w,sstep(px.outputs['Distance'],SK0,SK1))
dz=FM('MULTIPLY',w,FM('MINIMUM',FM('MAXIMUM',FM('SUBTRACT',ns.outputs[0],s1.outputs['Z']),-CL),CL))
A=store(A,'pb_dz',dz)
spn=N.new('GeometryNodeSetPosition'); L(A,spn.inputs['Geometry']); off=N.new('ShaderNodeCombineXYZ'); L(named('pb_dz'),off.inputs['Z']); L(off.outputs[0],spn.inputs['Offset'])
A=store(spn.outputs['Geometry'],'pb_seam',FM('GREATER_THAN',N.new('GeometryNodeInputIndex').outputs[0],-1.0))  # placeholder 1 on A
B=store(B,'pb_seam',FM('MULTIPLY',N.new('GeometryNodeInputIndex').outputs[0],0.0))
j=N.new('GeometryNodeJoinGeometry'); L(B,j.inputs[0]); L(A,j.inputs[0])
md=N.new('GeometryNodeMergeByDistance'); L(j.outputs[0],md.inputs['Geometry']); md.inputs['Distance'].default_value=0.0005
ss=N.new('GeometryNodeSetShadeSmooth'); L(md.outputs[0],ss.inputs['Geometry'])
L(ss.outputs[0],go.inputs[0])
m=T.modifiers.new(MN,'NODES'); m.node_group=ng
T['pb_fan_regrid']='UNVERIFIED pb: fan faces subdivided L%d, smoothed (grid %.2f m, blur %d, clamp %.2f m) in box %s'%(LEVEL,RES,BI,CL,(X0,X1,Y0,Y1))
import math
src_=bpy.data.objects['OZ_CAM_closeup_auto_walk_joints_CELS_south']
c=bpy.data.collections.new(CC); bpy.context.scene.collection.children.link(c)
cd=src_.data.copy(); cd.name='PB_CAM_closeup_CELS_south_lawn_bank_regrid'
co_=bpy.data.objects.new('PB_CAM_closeup_CELS_south_lawn_bank_regrid',cd); c.objects.link(co_)
co_.matrix_world=src_.matrix_world.copy(); co_.rotation_mode='XYZ'
co_.rotation_euler.z+=math.radians(float(E('YAW','-28'))); co_.rotation_euler.x+=math.radians(-3)
print('PB_FAN_ADDED')
if '--diag' in sys.argv:
    import numpy as np
    dg=bpy.context.evaluated_depsgraph_get(); te=T.evaluated_get(dg); me=te.to_mesh()
    print('PB_DIAG verts',len(me.vertices),'faces',len(me.polygons))
    a=me.attributes.get('pb_dz')
    if a:
        v=np.zeros(len(me.vertices)); a.data.foreach_get('value',v); nz=v[np.abs(v)>1e-4]
        print('PB_DIAG moved',len(nz),'abs mean %.3f max %.3f at clamp %d'%(np.abs(nz).mean() if len(nz) else 0,np.abs(nz).max() if len(nz) else 0,(np.abs(nz)>CL-1e-3).sum()))
    te.to_mesh_clear()
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

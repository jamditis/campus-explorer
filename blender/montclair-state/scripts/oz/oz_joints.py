# oz (UNVERIFIED, removable; REVERT=1 undoes): reusable per-walk scoring-joint grid for ALL remaining campus walks.
# One overlay object OZ_walk_joints_auto_GN_UNVERIFIED whose GN modifier (node group OZ_walk_joints_auto_GN, reusable on any
# walk object via its 'Walk' input) reads the EVALUATED Footpaths_OSM, lifts it 4 mm and stores per face 'oz_ang' = the local
# walk direction (nearest walk-edge direction mod 90, blurred over faces, quantised to QD deg so a straight walk keeps one grid).
# Material OZ_walk_joint_grid_auto_UNVERIFIED draws 1.6 cm dark joints every 1.524 m along/across that direction and is
# transparent elsewhere AND inside the ox/oy hand-cut boxes (exact box test in the shader, so no doubled joints there).
# Footpaths_OSM mesh/modifiers and the shared walk material are untouched.
import bpy, os, sys, math
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CN='OZ_walk_joints_auto_20261101oz_UNVERIFIED'; ON='OZ_walk_joints_auto_GN_UNVERIFIED'; NG='OZ_walk_joints_auto_GN'; MN='OZ_walk_joint_grid_auto_UNVERIFIED'
c=bpy.data.collections.get(CN)
if c:
    for o in list(c.objects):
        d=o.data; bpy.data.objects.remove(o)
        if d and d.users==0: (bpy.data.meshes if isinstance(d,bpy.types.Mesh) else bpy.data.cameras).remove(d)
    bpy.data.collections.remove(c)
if NG in bpy.data.node_groups: bpy.data.node_groups.remove(bpy.data.node_groups[NG])
m=bpy.data.materials.get(MN)
if m: bpy.data.materials.remove(m)
if REV:
    print('REVERTED_OZ_JOINTS')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
QD=float(os.environ.get('QD','3')); BI=int(os.environ.get('BI','6')); JW=float(os.environ.get('JW','0.016')); JS=1.524
BOXES=[(121,141,201,218),(118,145,183,201),(108,121,201,250),(-134,-102,193,228)]  # ox + oy boxes
F=bpy.data.objects['Footpaths_OSM']
# ---- material
mt=bpy.data.materials.new(MN); mt.use_nodes=True; nt=mt.node_tree; NN=nt.nodes; LL=nt.links.new
bs=NN['Principled BSDF']; out=NN['Material Output']; bs.inputs['Base Color'].default_value=(0.08,0.077,0.072,1); bs.inputs['Roughness'].default_value=0.95
geo=NN.new('ShaderNodeNewGeometry'); sx=NN.new('ShaderNodeSeparateXYZ'); LL(geo.outputs['Position'],sx.inputs[0])
at=NN.new('ShaderNodeAttribute'); at.attribute_name='oz_ang'; at.attribute_type='GEOMETRY'
def M(op,a=None,b=None,clamp=False):
    n=NN.new('ShaderNodeMath'); n.operation=op; n.use_clamp=clamp
    for i,v in ((0,a),(1,b)):
        if v is None: continue
        if isinstance(v,(int,float)): n.inputs[i].default_value=v
        else: LL(v,n.inputs[i])
    return n.outputs[0]
co=M('COSINE',at.outputs['Fac']); si=M('SINE',at.outputs['Fac'])
u=M('ADD',M('MULTIPLY',sx.outputs['X'],co),M('MULTIPLY',sx.outputs['Y'],si))
v=M('SUBTRACT',M('MULTIPLY',sx.outputs['Y'],co),M('MULTIPLY',sx.outputs['X'],si))
def dist(w): return M('MULTIPLY',M('ABSOLUTE',M('SUBTRACT',M('FRACT',M('ADD',M('DIVIDE',w,JS),0.5)),0.5)),JS)
line=M('LESS_THAN',M('MINIMUM',dist(u),dist(v)),JW/2)
mask=None
for (x0,x1,y0,y1) in BOXES:
    b=M('MULTIPLY',M('MULTIPLY',M('GREATER_THAN',sx.outputs['X'],x0),M('LESS_THAN',sx.outputs['X'],x1)),M('MULTIPLY',M('GREATER_THAN',sx.outputs['Y'],y0),M('LESS_THAN',sx.outputs['Y'],y1)))
    mask=b if mask is None else M('MAXIMUM',mask,b)
fac=M('MULTIPLY',line,M('SUBTRACT',1.0,mask))
tr=NN.new('ShaderNodeBsdfTransparent'); mx=NN.new('ShaderNodeMixShader'); LL(fac,mx.inputs['Fac']); LL(tr.outputs[0],mx.inputs[1]); LL(bs.outputs[0],mx.inputs[2]); LL(mx.outputs[0],out.inputs['Surface'])
# ---- node group
ng=bpy.data.node_groups.new(NG,'GeometryNodeTree'); I=ng.interface
I.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); I.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
I.new_socket('Walk',in_out='INPUT',socket_type='NodeSocketObject'); I.new_socket('Material',in_out='INPUT',socket_type='NodeSocketMaterial')
s=I.new_socket('Lift',in_out='INPUT',socket_type='NodeSocketFloat'); s.default_value=0.004
s=I.new_socket('Blur iterations',in_out='INPUT',socket_type='NodeSocketInt'); s.default_value=BI
s=I.new_socket('Quantise deg',in_out='INPUT',socket_type='NodeSocketFloat'); s.default_value=QD
N=ng.nodes; L=ng.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; L(gi.outputs['Walk'],oi.inputs['Object'])
g=oi.outputs['Geometry']
# boundary edges + their direction as (cos4t, sin4t)
en=N.new('GeometryNodeInputMeshEdgeNeighbors'); c1=N.new('FunctionNodeCompare'); c1.data_type='INT'; c1.operation='EQUAL'; L(en.outputs['Face Count'],c1.inputs[2]); c1.inputs[3].default_value=1
ev=N.new('GeometryNodeInputMeshEdgeVertices'); d=N.new('ShaderNodeVectorMath'); d.operation='SUBTRACT'; L(ev.outputs['Position 2'],d.inputs[0]); L(ev.outputs['Position 1'],d.inputs[1])
sd=N.new('ShaderNodeSeparateXYZ'); L(d.outputs[0],sd.inputs[0])
def FM(op,a=None,b=None):
    n=N.new('ShaderNodeMath'); n.operation=op
    for i,vv in ((0,a),(1,b)):
        if vv is None: continue
        if isinstance(vv,(int,float)): n.inputs[i].default_value=vv
        else: L(vv,n.inputs[i])
    return n.outputs[0]
t4=FM('MULTIPLY',FM('ARCTAN2',sd.outputs['Y'],sd.outputs['X']),4.0)
cv=N.new('ShaderNodeCombineXYZ'); L(FM('COSINE',t4),cv.inputs['X']); L(FM('SINE',t4),cv.inputs['Y'])
ste=N.new('GeometryNodeStoreNamedAttribute'); ste.data_type='FLOAT_VECTOR'; ste.domain='EDGE'; ste.inputs['Name'].default_value='oz_v4e'
L(g,ste.inputs['Geometry']); L(cv.outputs[0],ste.inputs['Value'])
sep=N.new('GeometryNodeSeparateGeometry'); sep.domain='EDGE'; L(ste.outputs['Geometry'],sep.inputs['Geometry']); L(c1.outputs['Result'],sep.inputs['Selection'])
pos=N.new('GeometryNodeInputPosition')
sn=N.new('GeometryNodeSampleNearest'); sn.domain='EDGE'; L(sep.outputs['Selection'],sn.inputs['Geometry']); L(pos.outputs[0],sn.inputs['Sample Position'])
nav=N.new('GeometryNodeInputNamedAttribute'); nav.data_type='FLOAT_VECTOR'; nav.inputs['Name'].default_value='oz_v4e'
si2=N.new('GeometryNodeSampleIndex'); si2.data_type='FLOAT_VECTOR'; si2.domain='EDGE'; L(sep.outputs['Selection'],si2.inputs['Geometry']); L(nav.outputs['Attribute'],si2.inputs['Value']); L(sn.outputs['Index'],si2.inputs['Index'])
stf=N.new('GeometryNodeStoreNamedAttribute'); stf.data_type='FLOAT_VECTOR'; stf.domain='FACE'; stf.inputs['Name'].default_value='oz_v4'
L(g,stf.inputs['Geometry']); L(si2.outputs['Value'],stf.inputs['Value'])
nav2=N.new('GeometryNodeInputNamedAttribute'); nav2.data_type='FLOAT_VECTOR'; nav2.inputs['Name'].default_value='oz_v4'
bl=N.new('GeometryNodeBlurAttribute'); bl.data_type='FLOAT_VECTOR'; L(nav2.outputs['Attribute'],bl.inputs['Value']); L(gi.outputs['Blur iterations'],bl.inputs['Iterations'])
sb=N.new('ShaderNodeSeparateXYZ'); L(bl.outputs['Value'],sb.inputs[0])
ang=FM('DIVIDE',FM('ARCTAN2',sb.outputs['Y'],sb.outputs['X']),4.0)
qr=FM('RADIANS',gi.outputs['Quantise deg'])
angq=FM('MULTIPLY',FM('ROUND',FM('DIVIDE',ang,qr)),qr)
sta=N.new('GeometryNodeStoreNamedAttribute'); sta.data_type='FLOAT'; sta.domain='FACE'; sta.inputs['Name'].default_value='oz_ang'
L(stf.outputs['Geometry'],sta.inputs['Geometry']); L(angq,sta.inputs['Value'])
rm=N.new('GeometryNodeRemoveAttribute'); L(sta.outputs['Geometry'],rm.inputs['Geometry']); rm.inputs['Name'].default_value='oz_v4'
rm2=N.new('GeometryNodeRemoveAttribute'); L(rm.outputs['Geometry'],rm2.inputs['Geometry']); rm2.inputs['Name'].default_value='oz_v4e'
cz=N.new('ShaderNodeCombineXYZ'); L(gi.outputs['Lift'],cz.inputs['Z'])
sp=N.new('GeometryNodeSetPosition'); L(rm2.outputs['Geometry'],sp.inputs['Geometry']); L(cz.outputs[0],sp.inputs['Offset'])
sm=N.new('GeometryNodeSetMaterial'); L(sp.outputs['Geometry'],sm.inputs['Geometry']); L(gi.outputs['Material'],sm.inputs['Material'])
ss=N.new('GeometryNodeSetShadeSmooth'); L(sm.outputs['Geometry'],ss.inputs['Geometry'])
L(ss.outputs['Geometry'],go.inputs[0])
# ---- object
col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
me=bpy.data.meshes.new(ON); o=bpy.data.objects.new(ON,me); col.objects.link(o)
md=o.modifiers.new('OZ_walk_joints_auto','NODES'); md.node_group=ng
for it in ng.interface.items_tree:
    if it.in_out!='INPUT' or it.socket_type=='NodeSocketGeometry': continue
    if it.name=='Walk': md[it.identifier]=F
    if it.name=='Material': md[it.identifier]=mt
o.visible_shadow=False; o['UNVERIFIED_oz']='no photo of these walks; 5-ft grid is the US default; grid direction = nearest walk edge'
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); mm=e.to_mesh()
a=mm.attributes.get('oz_ang'); vals=[0.0]*len(a.data); a.data.foreach_get('value',vals)
import collections; h=collections.Counter(round(math.degrees(x)) for x in vals)
print('OZ_JOINTS faces',len(mm.polygons),'distinct angles',len(h),'top',h.most_common(8)); e.to_mesh_clear()
# close-up cam: the walk running NNE into the oy CELS_S box (auto joints meet the hand-cut ones at the y=183 expansion joint)
from mathutils import Vector
FE2=F.evaluated_get(dg); FI=F.matrix_world.inverted()
def wz(x,y):
    ok,loc,n,i=FE2.ray_cast(FI@Vector((x,y,300)),Vector((0,0,-1)))
    return (F.matrix_world@loc).z if ok else None
CX,CY,TX,TY=[float(q) for q in os.environ.get('OZCAM','119.5,160.5,125,179').split(',')]
cz0=wz(CX,CY) or wz(TX,TY); tz0=wz(TX,TY) or cz0
CAMN='OZ_CAM_closeup_auto_walk_joints_CELS_south'
cd=bpy.data.cameras.new(CAMN); cd.lens=28; cam=bpy.data.objects.new(CAMN,cd); col.objects.link(cam)
cam.location=Vector((CX,CY,cz0+1.3)); cam.rotation_euler=(Vector((TX,TY,tz0))-cam.location).to_track_quat('-Z','Y').to_euler()
print('OZCAM',tuple(round(x,2) for x in cam.location),cz0,tz0)
if os.environ.get('TESTCAM')=='1':
    from mathutils import Vector
    for nm,(cx,cy,cz2,tx,ty,tz) in {'OZT_CAM_joints_aerial':(20,60,175,20,140,135),'OZT_CAM_joints_eye':(60,150,140,75,175,137)}.items():
        cd=bpy.data.cameras.new(nm); cd.lens=30; c2=bpy.data.objects.new(nm,cd); bpy.context.scene.collection.objects.link(c2)
        c2.location=(cx,cy,cz2); c2.rotation_euler=(Vector((tx,ty,tz))-c2.location).to_track_quat('-Z','Y').to_euler()
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

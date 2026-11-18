# pa (UNVERIFIED, removable; REVERT=1 undoes): smooth lawn over the stair-step 'bank' in the north strip.
# Cause (found in pa): the north strip (CELS/Calcia/Schmitt area) lies OUTSIDE the LiDAR terrain disc; Terrain_LiDAR_DTM_1m there
# is only a fan of ~160 m2 sliver triangles from the disc edge to the tile-corner hubs. Smooth-shaded slivers read as terraced
# ridges at eye level (OZ close-up). Fix: overlay object PA_north_strip_lawn_smooth_UNVERIFIED with a GN modifier (node group
# PA_north_strip_lawn_smooth_GN): 0.5 m grid over the box, z ray-cast onto the evaluated terrain, kept ONLY where the hit face is
# a fan sliver (mean edge length > AMIN = 2 m), z = terrain + LIFT(3.5 cm) + w*(max(blur(z)+RAISE(6 cm), z+LIFT) - (z+LIFT)) with w feathered to 0 within FW of walks/roads and at
# the fan edge, cut 0.3 m short of walks/roads; ortho UV + material slot copied from the terrain. Terrain/walk/road meshes untouched.
import bpy, os, sys
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CN='PA_north_strip_lawn_smooth_20261101pa_UNVERIFIED'; ON='PA_north_strip_lawn_smooth_UNVERIFIED'; NG='PA_north_strip_lawn_smooth_GN'
c=bpy.data.collections.get(CN)
if c:
    for o in list(c.objects):
        d=o.data; bpy.data.objects.remove(o)
        if d and d.users==0: (bpy.data.meshes if isinstance(d,bpy.types.Mesh) else bpy.data.cameras).remove(d)
    bpy.data.collections.remove(c)
if NG in bpy.data.node_groups: bpy.data.node_groups.remove(bpy.data.node_groups[NG])
MC='PA_Ground_ortho_grass_attrUV'
if MC in bpy.data.materials: bpy.data.materials.remove(bpy.data.materials[MC])
if REV:
    print('REVERTED_PA_BANK')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
X0,X1,Y0,Y1=[float(q) for q in os.environ.get('BOX','80,180,130,240').split(',')]
RES=float(os.environ.get('RES_G','0.35')); BI=int(os.environ.get('BI','60')); LIFT=float(os.environ.get('LIFT','0.035')); RAISE=float(os.environ.get('RAISE','0.06')); AMIN=float(os.environ.get('AMIN','2.0')); FW=float(os.environ.get('FW','0.9')); CUT=0.3
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; FP=bpy.data.objects['Footpaths_OSM']; RD=bpy.data.objects['Roads_OSM']
ng=bpy.data.node_groups.new(NG,'GeometryNodeTree'); I=ng.interface
I.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); I.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
def OI(ob):
    n=N.new('GeometryNodeObjectInfo'); n.transform_space='RELATIVE'; n.inputs['Object'].default_value=ob; return n.outputs['Geometry']
def FM(op,a=None,b=None,c=None,clamp=False):
    n=N.new('ShaderNodeMath'); n.operation=op; n.use_clamp=clamp
    for i,vv in ((0,a),(1,b),(2,c)):
        if vv is None: continue
        if isinstance(vv,(int,float)): n.inputs[i].default_value=vv
        else: L(vv,n.inputs[i])
    return n.outputs[0]
gr=N.new('GeometryNodeMeshGrid'); gr.inputs['Size X'].default_value=X1-X0; gr.inputs['Size Y'].default_value=Y1-Y0
gr.inputs['Vertices X'].default_value=int((X1-X0)/RES)+1; gr.inputs['Vertices Y'].default_value=int((Y1-Y0)/RES)+1
tf=N.new('GeometryNodeTransform'); L(gr.outputs['Mesh'],tf.inputs['Geometry']); tf.inputs['Translation'].default_value=((X0+X1)/2,(Y0+Y1)/2,0)
pos=N.new('GeometryNodeInputPosition'); sp0=N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0],sp0.inputs[0])
src=N.new('ShaderNodeCombineXYZ'); L(FM('ADD',sp0.outputs['X'],0.0131),src.inputs['X']); L(FM('ADD',sp0.outputs['Y'],0.0077),src.inputs['Y']); src.inputs['Z'].default_value=400
tg=OI(T)
ev_=N.new('GeometryNodeInputMeshEdgeVertices'); el_=N.new('ShaderNodeVectorMath'); el_.operation='DISTANCE'; L(ev_.outputs['Position 1'],el_.inputs[0]); L(ev_.outputs['Position 2'],el_.inputs[1])
eod=N.new('GeometryNodeFieldOnDomain'); eod.domain='FACE'; eod.data_type='FLOAT'; L(el_.outputs['Value'],eod.inputs[0])
class _A: pass
farea=_A(); farea.outputs={'Area':eod.outputs[0]}
rc=N.new('GeometryNodeRaycast'); rc.data_type='FLOAT'; L(tg,rc.inputs['Target Geometry']); L(farea.outputs['Area'],rc.inputs['Attribute']); L(src.outputs[0],rc.inputs['Source Position']); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=1000
uvn=N.new('GeometryNodeInputNamedAttribute'); uvn.data_type='FLOAT_VECTOR'; uvn.inputs['Name'].default_value='ortho'
rc2=N.new('GeometryNodeRaycast'); rc2.data_type='FLOAT_VECTOR'; L(tg,rc2.inputs['Target Geometry']); L(uvn.outputs['Attribute'],rc2.inputs['Attribute']); L(src.outputs[0],rc2.inputs['Source Position']); rc2.inputs['Ray Direction'].default_value=(0,0,-1); rc2.inputs['Ray Length'].default_value=1000
hz=N.new('ShaderNodeSeparateXYZ'); L(rc.outputs['Hit Position'],hz.inputs[0])
fan=FM('MULTIPLY',FM('GREATER_THAN',rc.outputs['Attribute'],AMIN),rc.outputs['Is Hit'])
def store(geo,name,val,dt='FLOAT',dom='POINT'):
    s=N.new('GeometryNodeStoreNamedAttribute'); s.data_type=dt; s.domain=dom; s.inputs['Name'].default_value=name; L(geo,s.inputs['Geometry']); L(val,s.inputs['Value']); return s.outputs['Geometry']
def named(name,dt='FLOAT'):
    n=N.new('GeometryNodeInputNamedAttribute'); n.data_type=dt; n.inputs['Name'].default_value=name; return n.outputs['Attribute']
g=store(tf.outputs['Geometry'],'pa_z0',hz.outputs['Z'])
g=store(g,'pa_fan',fan)
g=store(g,'ortho',rc2.outputs['Attribute'],'FLOAT2','CORNER')
# rays that slip through a shared sliver edge miss: fill z0/fan at those points from hit neighbours
g=store(g,'pa_hit',rc.outputs['Is Hit'])
def blurv(val,it=4):
    b=N.new('GeometryNodeBlurAttribute'); b.data_type='FLOAT'; L(val,b.inputs['Value']); b.inputs['Iterations'].default_value=it; return b.outputs['Value']
hb=FM('MAXIMUM',blurv(named('pa_hit')),0.01)
def fill(nm):
    sw=N.new('GeometryNodeSwitch'); sw.input_type='FLOAT'; L(FM('GREATER_THAN',named('pa_hit'),0.5),sw.inputs['Switch'])
    L(FM('DIVIDE',blurv(FM('MULTIPLY',named(nm),named('pa_hit'))),hb),sw.inputs['False']); L(named(nm),sw.inputs['True']); return sw.outputs['Output']
g=store(g,'pa_z0',fill('pa_z0'))
g=store(g,'pa_fan',FM('GREATER_THAN',fill('pa_fan'),0.5))
# distance to walks/roads (evaluated)
def prox(ob):
    # ignore walk/road faces buried >10 cm under the terrain sample (sunk OSM pieces left holes in the first pass)
    p=N.new('GeometryNodeProximity'); p.target_element='FACES'; L(OI(ob),p.inputs['Target'])
    pz=N.new('ShaderNodeSeparateXYZ'); L(p.outputs['Position'],pz.inputs[0])
    return FM('ADD',p.outputs['Distance'],FM('MULTIPLY',FM('LESS_THAN',pz.outputs['Z'],FM('SUBTRACT',named('pa_z0'),0.10)),100.0))
dwr=FM('MINIMUM',prox(FP),prox(RD))
sp1=N.new('ShaderNodeCombineXYZ'); L(sp0.outputs['X'],sp1.inputs['X']); L(sp0.outputs['Y'],sp1.inputs['Y']); L(named('pa_z0'),sp1.inputs['Z'])
st1=N.new('GeometryNodeSetPosition'); L(g,st1.inputs['Geometry']); L(sp1.outputs[0],st1.inputs['Position'])
g=store(st1.outputs['Geometry'],'pa_d',dwr)
b1=N.new('GeometryNodeBlurAttribute'); b1.data_type='FLOAT'; L(named('pa_z0'),b1.inputs['Value']); b1.inputs['Iterations'].default_value=BI
b2=N.new('GeometryNodeBlurAttribute'); b2.data_type='FLOAT'; L(named('pa_fan'),b2.inputs['Value']); b2.inputs['Iterations'].default_value=8
z0=named('pa_z0')
wd=FM('DIVIDE',FM('SUBTRACT',named('pa_d'),CUT),FW-CUT,clamp=True) if True else None
wf=FM('DIVIDE',FM('SUBTRACT',b2.outputs['Value'],0.6),0.4,clamp=True)
w=FM('MULTIPLY',wd,wf)
zl=FM('ADD',z0,FM('ADD',-0.02,FM('MULTIPLY',w,LIFT+0.02)))
zn=FM('ADD',zl,FM('MULTIPLY',w,FM('SUBTRACT',FM('MAXIMUM',FM('ADD',b1.outputs['Value'],RAISE),zl),zl)))
spz=N.new('ShaderNodeCombineXYZ'); L(sp0.outputs['X'],spz.inputs['X']); L(sp0.outputs['Y'],spz.inputs['Y']); L(zn,spz.inputs['Z'])
st=N.new('GeometryNodeSetPosition'); L(g,st.inputs['Geometry']); L(spz.outputs[0],st.inputs['Position'])
# delete non-fan / near walks+roads
dele=FM('MAXIMUM',FM('LESS_THAN',named('pa_fan'),0.5),FM('LESS_THAN',named('pa_d'),CUT))
dg_=N.new('GeometryNodeDeleteGeometry'); dg_.domain='POINT'; L(st.outputs['Geometry'],dg_.inputs['Geometry']); L(dele,dg_.inputs['Selection'])
cl=g
for nm in ('pa_z0','pa_fan','pa_d','pa_hit'):
    r=N.new('GeometryNodeRemoveAttribute'); L(dg_.outputs['Geometry'] if nm=='pa_z0' else prev,r.inputs['Geometry']); r.inputs['Name'].default_value=nm; prev=r.outputs['Geometry']
mi=N.new('GeometryNodeSetMaterialIndex'); L(prev,mi.inputs['Geometry']); mi.inputs['Material Index'].default_value=0
ss=N.new('GeometryNodeSetShadeSmooth'); L(mi.outputs['Geometry'],ss.inputs['Geometry'])
L(ss.outputs['Geometry'],go.inputs[0])
col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
me=bpy.data.meshes.new(ON+'_gn'); me.materials.append(T.data.materials[0]); o=bpy.data.objects.new(ON,me); col.objects.link(o)
md=o.modifiers.new('PA_north_strip_lawn_smooth','NODES'); md.node_group=ng
o['UNVERIFIED_pa']='north strip is outside the LiDAR terrain disc; this smooths the sliver-fan ground only, real grade not measured'
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); mm=e.to_mesh()
import statistics
print('PA_BANK verts',len(mm.vertices),'faces',len(mm.polygons),'attrs',[a.name for a in mm.attributes if not a.name.startswith('.')], 'uv',[u.name for u in mm.uv_layers])
e.to_mesh_clear()
# bake to a real mesh (Cycles did not pick up the GN-stored 'ortho' UV on a generated mesh) and drop the GN modifier/group
mb=bpy.data.meshes.new_from_object(e); mb.name=ON
o.modifiers.clear(); old=o.data; o.data=mb; bpy.data.meshes.remove(old); bpy.data.node_groups.remove(ng)
mb.materials.clear(); mb.materials.append(T.data.materials[0])
print('PA_BANK baked',len(mb.vertices),'uv',[u.name for u in mb.uv_layers],'mats',[m.name for m in mb.materials])
if os.environ.get('TESTCAM')=='1':
    from mathutils import Vector
    for nm,(cx,cy,cz2,tx,ty,tz) in {'PAT_CAM_bank_top':(128,172,175,128,172.01,130)}.items():
        cd=bpy.data.cameras.new(nm); cd.lens=24; c2=bpy.data.objects.new(nm,cd); bpy.context.scene.collection.objects.link(c2)
        c2.location=(cx,cy,cz2); c2.rotation_euler=(Vector((tx,ty,tz))-c2.location).to_track_quat('-Z','Y').to_euler()
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

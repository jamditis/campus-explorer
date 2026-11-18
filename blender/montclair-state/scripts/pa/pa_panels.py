# pa (UNVERIFIED, removable; REVERT=1 undoes): per-panel tone + subtle edge/corner chipping on ALL walks outside the ox/oy boxes.
# New overlay object PA_walk_panel_tone_chips_UNVERIFIED (collection PA_walk_panel_tone_20261101pa_UNVERIFIED) whose GN modifier
# reuses the oz node group OZ_walk_joints_auto_GN (Walk=Footpaths_OSM, Lift 3.5 mm, Material=PA material) so it gets the same
# per-face grid direction 'oz_ang'. The PA material hashes each 5-ft panel (floor(u/1.524), floor(v/1.524), oz_ang) into a light
# or dark tone (alpha <= TA) and darkens noisy chips along panel edges and at corners; transparent elsewhere and inside the boxes.
# Footpaths_OSM, the oz overlay and all shared materials are untouched. Depends on oz (revert pa before oz).
import bpy, os, sys
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CN='PA_walk_panel_tone_20261101pa_UNVERIFIED'; ON='PA_walk_panel_tone_chips_UNVERIFIED'; MN='PA_walk_panel_tone_chips_UNVERIFIED'
c=bpy.data.collections.get(CN)
if c:
    for o in list(c.objects):
        d=o.data; bpy.data.objects.remove(o)
        if d and d.users==0: (bpy.data.meshes if isinstance(d,bpy.types.Mesh) else bpy.data.cameras).remove(d)
    bpy.data.collections.remove(c)
m=bpy.data.materials.get(MN)
if m: bpy.data.materials.remove(m)
if REV:
    print('REVERTED_PA_PANELS')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
TA=float(os.environ.get('TA','0.20')); CH=float(os.environ.get('CH','0.62')); JS=1.524
BOXES=[(121,141,201,218),(118,145,183,201),(108,121,201,250),(-134,-102,193,228)]
F=bpy.data.objects['Footpaths_OSM']; ng=bpy.data.node_groups['OZ_walk_joints_auto_GN']
mt=bpy.data.materials.new(MN); mt.use_nodes=True; nt=mt.node_tree; NN=nt.nodes; LL=nt.links.new
bs=NN['Principled BSDF']; out=NN['Material Output']; bs.inputs['Roughness'].default_value=0.92
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
du=dist(u); dv=dist(v)
# panel hash
iu=M('FLOOR',M('DIVIDE',u,JS)); iv=M('FLOOR',M('DIVIDE',v,JS))
cv=NN.new('ShaderNodeCombineXYZ'); LL(iu,cv.inputs['X']); LL(iv,cv.inputs['Y']); LL(M('MULTIPLY',at.outputs['Fac'],37.0),cv.inputs['Z'])
wn=NN.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions='3D'; LL(cv.outputs[0],wn.inputs['Vector'])
h=wn.outputs['Value']
# in-panel cloudiness
nz=NN.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=1.3; nz.inputs['Detail'].default_value=3; LL(geo.outputs['Position'],nz.inputs['Vector'])
tone=M('ADD',M('MULTIPLY',M('SUBTRACT',h,0.5),2.0),M('MULTIPLY',M('SUBTRACT',nz.outputs['Fac'],0.5),0.6))   # -1..1
ta=M('MULTIPLY',M('ABSOLUTE',tone),TA,clamp=True)
light=M('GREATER_THAN',tone,0.0)
# chips: noisy bites within 4 cm of a joint, bigger at corners
cn=NN.new('ShaderNodeTexNoise'); cn.inputs['Scale'].default_value=9.0; cn.inputs['Detail'].default_value=4; cn.inputs['Roughness'].default_value=0.65; LL(geo.outputs['Position'],cn.inputs['Vector'])
dmin=M('MINIMUM',du,dv); dmax=M('MAXIMUM',du,dv)
edge=M('LESS_THAN',dmin,M('ADD',0.012,M('MULTIPLY',cn.outputs['Fac'],0.05)))
corner=M('LESS_THAN',dmax,M('ADD',0.03,M('MULTIPLY',cn.outputs['Fac'],0.09)))
chipsel=M('MULTIPLY',M('MAXIMUM',M('MULTIPLY',edge,M('GREATER_THAN',cn.outputs['Fac'],CH)),M('MULTIPLY',corner,M('GREATER_THAN',cn.outputs['Fac'],CH-0.1))),M('GREATER_THAN',dmin,0.008))
# colour: chip dark grey > tone light/dark
mxc=NN.new('ShaderNodeMix'); mxc.data_type='RGBA'; LL(light,mxc.inputs['Factor']); mxc.inputs['A'].default_value=(0.20,0.195,0.185,1); mxc.inputs['B'].default_value=(0.80,0.79,0.76,1)
mxk=NN.new('ShaderNodeMix'); mxk.data_type='RGBA'; LL(chipsel,mxk.inputs['Factor']); LL(mxc.outputs['Result'],mxk.inputs['A']); mxk.inputs['B'].default_value=(0.30,0.29,0.27,1)
LL(mxk.outputs['Result'],bs.inputs['Base Color'])
alpha=M('MAXIMUM',ta,M('MULTIPLY',chipsel,0.55))
mask=None
for (x0,x1,y0,y1) in BOXES:
    b=M('MULTIPLY',M('MULTIPLY',M('GREATER_THAN',sx.outputs['X'],x0),M('LESS_THAN',sx.outputs['X'],x1)),M('MULTIPLY',M('GREATER_THAN',sx.outputs['Y'],y0),M('LESS_THAN',sx.outputs['Y'],y1)))
    mask=b if mask is None else M('MAXIMUM',mask,b)
fac=M('MULTIPLY',alpha,M('SUBTRACT',1.0,mask))
tr=NN.new('ShaderNodeBsdfTransparent'); mx=NN.new('ShaderNodeMixShader'); LL(fac,mx.inputs['Fac']); LL(tr.outputs[0],mx.inputs[1]); LL(bs.outputs[0],mx.inputs[2]); LL(mx.outputs[0],out.inputs['Surface'])
col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
me=bpy.data.meshes.new(ON); o=bpy.data.objects.new(ON,me); col.objects.link(o)
md=o.modifiers.new('PA_walk_panel_tone','NODES'); md.node_group=ng
for it in ng.interface.items_tree:
    if it.in_out!='INPUT' or it.socket_type=='NodeSocketGeometry': continue
    if it.name=='Walk': md[it.identifier]=F
    if it.name=='Material': md[it.identifier]=mt
    if it.name=='Lift': md[it.identifier]=0.0035
o.visible_shadow=False; o['UNVERIFIED_pa']='no photo of these walks; per-panel tone and chips are a generic poured-concrete look'
print('PA_PANELS ok', TA, CH)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

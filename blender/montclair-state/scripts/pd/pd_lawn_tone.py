# pd (UNVERIFIED, removable; REVERT=1 undoes): north-strip lawn base too pale (near-white under the pc grass blades).
# GN modifier PD_north_strip_lawn_mask (last) stores point attr 'pd_lawn' (1 inside BOX, fading to 0 over FADE m) on Terrain_LiDAR_DTM_1m and on
# PB2_walk_lawn_fillet_UNVERIFIED; their slot 0 (Ground_ortho_grass) swapped to a copy that multiplies PALE texels only (luma gate) toward a lawn green.
# Ground_ortho_grass itself untouched (other users unaffected).
import bpy, os, sys
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
OBJS=[bpy.data.objects['Terrain_LiDAR_DTM_1m'], bpy.data.objects['PB2_walk_lawn_fillet_UNVERIFIED']]
MN='PD_north_strip_lawn_mask'; NEWM='PD_Ground_ortho_grass_north_strip_tone_UNVERIFIED'; SRC='Ground_ortho_grass'
for o in OBJS:
    if MN in o.modifiers: o.modifiers.remove(o.modifiers[MN])
    if 'pd_prev_slot0' in o.keys():
        n=o['pd_prev_slot0']
        if n in bpy.data.materials: o.material_slots[0].material=bpy.data.materials[n]
        del o['pd_prev_slot0']
    if 'UNVERIFIED_pd' in o.keys(): del o['UNVERIFIED_pd']
if MN+'_GN' in bpy.data.node_groups: bpy.data.node_groups.remove(bpy.data.node_groups[MN+'_GN'])
if NEWM in bpy.data.materials and bpy.data.materials[NEWM].users==0: bpy.data.materials.remove(bpy.data.materials[NEWM])
if REV:
    print('REVERTED_PD')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
X0,X1,Y0,Y1=[float(v) for v in os.environ.get('BOX','-160,160,125,265').split(',')]; FADE=float(os.environ.get('FADE','12'))
L0=float(os.environ.get('LUM0','0.30')); L1=float(os.environ.get('LUM1','0.60')); STR=float(os.environ.get('STR','0.85'))
TC=[float(v) for v in os.environ.get('TONE','0.42,0.50,0.30').split(',')]
ng=bpy.data.node_groups.new(MN+'_GN','GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput'); pos=N.new('GeometryNodeInputPosition')
def m(op,a=None,b=None,va=0.0,vb=0.0):
    n=N.new('ShaderNodeMath'); n.operation=op; n.inputs[0].default_value=va; n.inputs[1].default_value=vb
    if a is not None: L(a,n.inputs[0])
    if b is not None: L(b,n.inputs[1])
    return n.outputs[0]
s=N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0],s.inputs[0])
def ax(c,a0,a1):
    w=m('MINIMUM',m('DIVIDE',m('SUBTRACT',c,vb=a0),vb=FADE),m('DIVIDE',m('SUBTRACT',None,c,va=a1),vb=FADE))
    return m('MINIMUM',m('MAXIMUM',w,vb=0.0),vb=1.0)
w=m('MULTIPLY',ax(s.outputs['X'],X0,X1),ax(s.outputs['Y'],Y0,Y1))
st=N.new('GeometryNodeStoreNamedAttribute'); st.data_type='FLOAT'; st.domain='POINT'; st.inputs['Name'].default_value='pd_lawn'
L(gi.outputs[0],st.inputs['Geometry']); L(w,st.inputs['Value']); L(st.outputs[0],go.inputs[0])
src=bpy.data.materials[SRC]; nm=src.copy(); nm.name=NEWM; nt=nm.node_tree
bsdf=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]; fs=bsdf.inputs['Base Color'].links[0].from_socket
at=nt.nodes.new('ShaderNodeAttribute'); at.attribute_name='pd_lawn'
bw=nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(fs,bw.inputs[0])
mr=nt.nodes.new('ShaderNodeMapRange'); nt.links.new(bw.outputs[0],mr.inputs[0]); mr.inputs[1].default_value=L0; mr.inputs[2].default_value=L1
f1=nt.nodes.new('ShaderNodeMath'); f1.operation='MULTIPLY'; nt.links.new(mr.outputs[0],f1.inputs[0]); nt.links.new(at.outputs['Fac'],f1.inputs[1])
f2=nt.nodes.new('ShaderNodeMath'); f2.operation='MULTIPLY'; nt.links.new(f1.outputs[0],f2.inputs[0]); f2.inputs[1].default_value=STR
mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MIX'; nt.links.new(f2.outputs[0],mx.inputs['Factor'])
# target = texel luma-preserving-ish green: tone * (0.6 + 0.6*luma)
sc=nt.nodes.new('ShaderNodeMath'); sc.operation='MULTIPLY_ADD'; nt.links.new(bw.outputs[0],sc.inputs[0]); sc.inputs[1].default_value=0.6; sc.inputs[2].default_value=0.6
tg=nt.nodes.new('ShaderNodeMix'); tg.data_type='RGBA'; tg.blend_type='MULTIPLY'; tg.inputs['Factor'].default_value=1.0
tg.inputs[6].default_value=(*TC,1); cs=nt.nodes.new('ShaderNodeCombineXYZ')
for k in 'XYZ': nt.links.new(sc.outputs[0],cs.inputs[k])
nt.links.new(cs.outputs[0],tg.inputs[7])
nt.links.new(fs,mx.inputs[6]); nt.links.new(tg.outputs[2],mx.inputs[7]); nt.links.new(mx.outputs[2],bsdf.inputs['Base Color'])
nm['UNVERIFIED']='pd north-strip lawn base tone (luma-gated toward green, BOX %s)'%((X0,X1,Y0,Y1),)
for o in OBJS:
    o.modifiers.new(MN,'NODES').node_group=ng
    o['pd_prev_slot0']=o.material_slots[0].material.name; o.material_slots[0].material=nm
    o['UNVERIFIED_pd']='lawn tone box %s fade %.0f lum %.2f-%.2f str %.2f'%((X0,X1,Y0,Y1),FADE,L0,L1,STR)
print('BUILT_PD', [ (o.name,o.data.users) for o in OBJS])
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

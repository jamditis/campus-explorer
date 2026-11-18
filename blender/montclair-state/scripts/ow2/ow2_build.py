# ow2 (UNVERIFIED, all removable; REVERT=1 undoes):
# (A) CELS walk-edge fold by the road (x~125-137, y~205-214): long skinny Footpaths_OSM triangles bridge uneven DTM, so the walk dips under / rides over the
#     terrain and folds against the road. GN modifier OW2_walk_fold_fix (last on Footpaths_OSM): faces whose centre is in the box are split off, subdivided (3 levels),
#     their z set to DTM+5 cm (raycast down onto Terrain_LiDAR_DTM_1m) with a weight that is 1 in the inner box and fades to 0 at the outer box (so the boundary
#     edges stay on the original straight edges -> no cracks), then re-joined. Mesh unedited.
# (B) Pale skirt ortho strip beside the north-edge footway (y~247-262, x~-120..30): GN modifier OW2_skirt_strip_mask stores 'ow2_strip' on Context_skirt_3DEP_ortho_4km;
#     slot swapped to a copy OW2_Context_skirt_ortho_strip_tone_UNVERIFIED that multiplies PALE texels only (luma gate) toward the OU grass tone. OU material kept (fake user).
import bpy, os, sys
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
F=bpy.data.objects['Footpaths_OSM']; S=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
MA='OW2_walk_fold_fix'; MB='OW2_skirt_strip_mask'; NEWM='OW2_Context_skirt_ortho_strip_tone_UNVERIFIED'
for o,mn in ((F,MA),(S,MB)):
    if mn in o.modifiers: o.modifiers.remove(o.modifiers[mn])
    if mn+'_GN' in bpy.data.node_groups: bpy.data.node_groups.remove(bpy.data.node_groups[mn+'_GN'])
for o in (F,S):
    for k in [k for k in o.keys() if k.startswith(('UNVERIFIED_ow2','ow2_'))]:
        if k=='ow2_prev_slots':
            for i,n in enumerate(o[k]):
                if n and n in bpy.data.materials: o.material_slots[i].material=bpy.data.materials[n]
        del o[k]
if NEWM in bpy.data.materials:
    m=bpy.data.materials[NEWM]
    if m.users==0 or (m.users==1 and m.use_fake_user): bpy.data.materials.remove(m)
for n in ('OU_Context_skirt_ortho_edge_tone_UNVERIFIED',):
    m=bpy.data.materials.get(n)
    if m and 'ow2_set_fake' in m: m.use_fake_user=bool(m['ow2_set_fake']); del m['ow2_set_fake']
CC='OW2_cams_20261101ow2'; c=bpy.data.collections.get(CC)
if c:
    for o in list(c.objects):
        d=o.data; bpy.data.objects.remove(o)
        if d and d.users==0: bpy.data.cameras.remove(d)
    bpy.data.collections.remove(c)
if REV:
    print('REVERTED_OW2')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
X0,X1,Y0,Y1=[float(v) for v in os.environ.get('BOX','121,141,201,218').split(',')]; FADE=float(os.environ.get('FADE','3.0')); LIFT=float(os.environ.get('LIFT','0.05'))
def gn(name):
    ng=bpy.data.node_groups.new(name,'GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    return ng,ng.nodes,ng.links.new
def mth(N,L,op,a=None,b=None,va=0.0,vb=0.0):
    n=N.new('ShaderNodeMath'); n.operation=op; n.inputs[0].default_value=va; n.inputs[1].default_value=vb
    if a is not None: L(a,n.inputs[0])
    if b is not None: L(b,n.inputs[1])
    return n.outputs[0]
def boxw(N,L,pos,x0,x1,y0,y1,fade):
    s=N.new('ShaderNodeSeparateXYZ'); L(pos,s.inputs[0])
    def ax(c,a0,a1):
        lo=mth(N,L,'DIVIDE',mth(N,L,'SUBTRACT',c,va=0,vb=a0),vb=fade); hi=mth(N,L,'DIVIDE',mth(N,L,'SUBTRACT',None,c,va=a1),vb=fade)
        w=mth(N,L,'MINIMUM',lo,hi); w=mth(N,L,'MINIMUM',mth(N,L,'MAXIMUM',w,vb=0.0),vb=1.0); return w
    return mth(N,L,'MULTIPLY',ax(s.outputs['X'],x0,x1),ax(s.outputs['Y'],y0,y1)), s
# (A)
ng,N,L=gn(MA+'_GN'); gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
pos=N.new('GeometryNodeInputPosition')
wbox,s=boxw(N,L,pos.outputs[0],X0-FADE,X1+FADE,Y0-FADE,Y1+FADE,0.001)  # hard outer box for face selection
cap=N.new('GeometryNodeCaptureAttribute'); cap.domain='FACE'
try: cap.capture_items.new('FLOAT','w')
except Exception: cap.data_type='FLOAT'
L(gi.outputs[0],cap.inputs[0]); L(wbox,cap.inputs[1])
sel=mth(N,L,'GREATER_THAN',cap.outputs[1],vb=0.5)
sep=N.new('GeometryNodeSeparateGeometry'); sep.domain='FACE'; L(cap.outputs[0],sep.inputs['Geometry']); L(sel,sep.inputs['Selection'])
sub=N.new('GeometryNodeSubdivideMesh'); sub.inputs['Level'].default_value=3; L(sep.outputs['Selection'],sub.inputs['Mesh'])
oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=T; oi.transform_space='RELATIVE'
pos2=N.new('GeometryNodeInputPosition')
up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; L(pos2.outputs[0],up.inputs[0]); up.inputs[1].default_value=(0,0,30.0)
rc=N.new('GeometryNodeRaycast'); L(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L(up.outputs[0],rc.inputs['Source Position']); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=80.0
w2,s2=boxw(N,L,pos2.outputs[0],X0,X1,Y0,Y1,FADE)  # 1 inside inner box -> 0 at outer box edge
hs=N.new('ShaderNodeSeparateXYZ'); L(rc.outputs['Hit Position'],hs.inputs[0])
tz=mth(N,L,'ADD',hs.outputs['Z'],vb=LIFT)
dz=mth(N,L,'MULTIPLY',mth(N,L,'SUBTRACT',tz,s2.outputs['Z']),mth(N,L,'MULTIPLY',w2,rc.outputs['Is Hit']))
cx=N.new('ShaderNodeCombineXYZ'); L(dz,cx.inputs['Z'])
sp=N.new('GeometryNodeSetPosition'); L(sub.outputs[0],sp.inputs['Geometry']); L(cx.outputs[0],sp.inputs['Offset'])
BLUR=int(os.environ.get('BLUR','0')); last=sp.outputs[0]
if BLUR>0:
    p3=N.new('GeometryNodeInputPosition'); bl=N.new('GeometryNodeBlurAttribute'); bl.data_type='FLOAT_VECTOR'; L(p3.outputs[0],bl.inputs[0]); bl.inputs['Iterations'].default_value=BLUR
    w3,s3=boxw(N,L,p3.outputs[0],X0,X1,Y0,Y1,FADE)
    sp2=N.new('GeometryNodeSetPosition'); L(last,sp2.inputs['Geometry']); L(bl.outputs[0],sp2.inputs['Position']); L(mth(N,L,'GREATER_THAN',w3,vb=0.999),sp2.inputs['Selection'])
    p4=N.new('GeometryNodeInputPosition'); up4=N.new('ShaderNodeVectorMath'); up4.operation='ADD'; L(p4.outputs[0],up4.inputs[0]); up4.inputs[1].default_value=(0,0,30.0)
    rc4=N.new('GeometryNodeRaycast'); L(oi.outputs['Geometry'],rc4.inputs['Target Geometry']); L(up4.outputs[0],rc4.inputs['Source Position']); rc4.inputs['Ray Direction'].default_value=(0,0,-1); rc4.inputs['Ray Length'].default_value=80.0
    h4=N.new('ShaderNodeSeparateXYZ'); L(rc4.outputs['Hit Position'],h4.inputs[0]); s4=N.new('ShaderNodeSeparateXYZ'); L(p4.outputs[0],s4.inputs[0])
    zc=mth(N,L,'MAXIMUM',s4.outputs['Z'],mth(N,L,'ADD',h4.outputs['Z'],vb=0.03))
    c4=N.new('ShaderNodeCombineXYZ'); L(s4.outputs['X'],c4.inputs['X']); L(s4.outputs['Y'],c4.inputs['Y']); L(zc,c4.inputs['Z'])
    sp3=N.new('GeometryNodeSetPosition'); L(sp2.outputs[0],sp3.inputs['Geometry']); L(c4.outputs[0],sp3.inputs['Position']); L(rc4.outputs['Is Hit'],sp3.inputs['Selection'])
    last=sp3.outputs[0]
jn=N.new('GeometryNodeJoinGeometry'); L(sep.outputs['Inverted'],jn.inputs[0]); L(last,jn.inputs[0])
mg=N.new('GeometryNodeMergeByDistance'); mg.inputs['Distance'].default_value=0.0005; L(jn.outputs[0],mg.inputs['Geometry'])
sm=N.new('GeometryNodeSetShadeSmooth'); L(mg.outputs[0],sm.inputs['Geometry'])
L(sm.outputs[0],go.inputs[0])
F.modifiers.new(MA,'NODES').node_group=ng
F['UNVERIFIED_ow2_fold']='box %s fade %.1f lift %.2f subdiv 3 blur %d (>=DTM+3cm)'%((X0,X1,Y0,Y1),FADE,LIFT,BLUR)
# (B)
SX0,SX1,SY0,SY1=[float(v) for v in os.environ.get('SBOX','-130,35,243,268').split(',')]
ng,N,L=gn(MB+'_GN'); gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput'); pos=N.new('GeometryNodeInputPosition')
w,_=boxw(N,L,pos.outputs[0],SX0,SX1,SY0,SY1,float(os.environ.get('SFADE','4.0')))
st=N.new('GeometryNodeStoreNamedAttribute'); st.data_type='FLOAT'; st.domain='POINT'; st.inputs['Name'].default_value='ow2_strip'
L(gi.outputs[0],st.inputs['Geometry']); L(w,st.inputs['Value']); L(st.outputs[0],go.inputs[0])
S.modifiers.new(MB,'NODES').node_group=ng
old=[sl.material.name if sl.material else '' for sl in S.material_slots]; S['ow2_prev_slots']=old
src=bpy.data.materials['OU_Context_skirt_ortho_edge_tone_UNVERIFIED']; src['ow2_set_fake']=int(src.use_fake_user); src.use_fake_user=True
nm=src.copy(); nm.name=NEWM; nt=nm.node_tree
bsdf=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]; lk=bsdf.inputs['Base Color'].links[0]; fs=lk.from_socket
at=nt.nodes.new('ShaderNodeAttribute'); at.attribute_name='ow2_strip'
rgbbw=nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(fs,rgbbw.inputs[0])
mr=nt.nodes.new('ShaderNodeMapRange'); nt.links.new(rgbbw.outputs[0],mr.inputs[0]); mr.inputs[1].default_value=float(os.environ.get('LUM0','0.12')); mr.inputs[2].default_value=float(os.environ.get('LUM1','0.30'))
fac=nt.nodes.new('ShaderNodeMath'); fac.operation='MULTIPLY'; nt.links.new(mr.outputs[0],fac.inputs[0]); nt.links.new(at.outputs['Fac'],fac.inputs[1])
mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; nt.links.new(fac.outputs[0],mx.inputs['Factor'])
nt.links.new(fs,mx.inputs[6]); mx.inputs[7].default_value=(0.55,0.64,0.44,1)
nt.links.new(mx.outputs[2],bsdf.inputs['Base Color'])
nm['UNVERIFIED']='ow2 pale strip tone beside the north-edge footway (luma-gated multiply)'
for i,n in enumerate(old):
    if n=='OU_Context_skirt_ortho_edge_tone_UNVERIFIED': S.material_slots[i].material=nm
S['UNVERIFIED_ow2_strip']='sbox %s'%((SX0,SX1,SY0,SY1),)
# probe result (A)
dg=bpy.context.evaluated_depsgraph_get(); e=F.evaluated_get(dg); me=e.to_mesh()
import mathutils
bv=mathutils.bvhtree.BVHTree.FromObject(T,dg)
cnt=0; dev=[]
for v in me.vertices:
    if X0<v.co.x<X1 and Y0<v.co.y<Y1:
        h=bv.ray_cast(v.co+mathutils.Vector((0,0,30)),mathutils.Vector((0,0,-1)))
        if h[0]: dev.append(v.co.z-h[0].z); cnt+=1
e.to_mesh_clear()
if dev: print('FOLD verts',cnt,'dz min %.3f max %.3f'%(min(dev),max(dev)))
from mathutils import Vector
col=bpy.data.collections.new(CC); bpy.context.scene.collection.children.link(col)
CL=os.environ.get('CLOC','140.5,201.5,129.9'); CT=os.environ.get('CTGT','130.5,209.5,128.2')
cd=bpy.data.cameras.new('OW2_CAM_closeup_CELS_walk_road_edge'); cd.lens=28
cam=bpy.data.objects.new('OW2_CAM_closeup_CELS_walk_road_edge',cd); col.objects.link(cam)
cam.location=Vector([float(x) for x in CL.split(',')]); cam.rotation_euler=(Vector([float(x) for x in CT.split(',')])-cam.location).to_track_quat('-Z','Y').to_euler()
print('BUILT_OW2')
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

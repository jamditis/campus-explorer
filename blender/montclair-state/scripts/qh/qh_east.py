# qh: CCIS east view fixes. (1) the 'dark diagonal fascia' = steep LiDAR roof-drape curtain faces hanging down the NE
# junction (x 28.3-30.0, y 201.5-206.0, z 140-153.2) -> removable GN modifier on the roof deleting steep faces (|nz|<0.6)
# in that box. (2) 'slanted tower panel' = camera keystone (QE_CAM_eye_ccis_east pitched 12.8 deg up): camera levelled
# (rot x 90) with an equivalent lens shift (architectural 2-point view). Originals kept in props; REVERT=1 exact.
import bpy, os, math
REV=os.environ.get('REVERT')=='1'
R=bpy.data.objects['Center for Computing and Information Science roof (LiDAR)']; MN='QH_roof_curtain_trim_NE'
m=R.modifiers.get(MN)
if m:
    ng=m.node_group; R.modifiers.remove(m)
    if ng and ng.users==0: bpy.data.node_groups.remove(ng)
C=bpy.data.objects['QE_CAM_eye_ccis_east']
if 'qh_rot' in C: C.rotation_euler=C['qh_rot']; C.data.shift_y=C['qh_shift']; del C['qh_rot']; del C['qh_shift']
J=bpy.data.objects.get('QH_CCIS_NE_junction_cover_UNVERIFIED')
if J: me=J.data; bpy.data.objects.remove(J,do_unlink=True); bpy.data.meshes.remove(me)
K=bpy.data.objects.get('QH_CAM_closeup_ccis_east_junction')
if K: cd=K.data; bpy.data.objects.remove(K,do_unlink=True); bpy.data.cameras.remove(cd)
CWo=bpy.data.objects['QE_CCIS_drape_cover_wall_east_UNVERIFIED']
if 'qh_bot' in CWo.data:
    for i,z in CWo.data['qh_bot'].items(): CWo.data.vertices[int(i)].co.z=z
    del CWo.data['qh_bot']; CWo.data.update()
if REV: print('QH east reverted')
else:
    if os.environ.get('QH_TRIM','1')=='1':
     ng=bpy.data.node_groups.new(MN+'_GN','GeometryNodeTree')
     ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
     N=ng.nodes; L=ng.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
     pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sep.inputs[0])
     nrm=N.new('GeometryNodeInputNormal'); sn=N.new('ShaderNodeSeparateXYZ'); L.new(nrm.outputs[0],sn.inputs[0])
     W=R.matrix_world.inverted()
     def cmp(sock,lo,hi):
         a=N.new('FunctionNodeCompare'); a.data_type='FLOAT'; a.operation='GREATER_THAN'; L.new(sock,a.inputs[0]); a.inputs[1].default_value=lo
         b=N.new('FunctionNodeCompare'); b.data_type='FLOAT'; b.operation='LESS_THAN'; L.new(sock,b.inputs[0]); b.inputs[1].default_value=hi
         n=N.new('FunctionNodeBooleanMath'); n.operation='AND'; L.new(a.outputs[0],n.inputs[0]); L.new(b.outputs[0],n.inputs[1]); return n.outputs[0]
     lo=W@__import__('mathutils').Vector((28.3,201.5,140.0)); hi=W@__import__('mathutils').Vector((30.0,206.0,153.2))
     ab=N.new('ShaderNodeMath'); ab.operation='ABSOLUTE'; L.new(sn.outputs[2],ab.inputs[0])
     st=N.new('FunctionNodeCompare'); st.data_type='FLOAT'; st.operation='LESS_THAN'; L.new(ab.outputs[0],st.inputs[0]); st.inputs[1].default_value=0.6
     s=[cmp(sep.outputs[0],lo.x,hi.x),cmp(sep.outputs[1],lo.y,hi.y),cmp(sep.outputs[2],lo.z,hi.z),st.outputs[0]]
     acc=s[0]
     for t in s[1:]:
         n=N.new('FunctionNodeBooleanMath'); n.operation='AND'; L.new(acc,n.inputs[0]); L.new(t,n.inputs[1]); acc=n.outputs[0]
     dl=N.new('GeometryNodeDeleteGeometry'); dl.domain='FACE'; L.new(gi.outputs[0],dl.inputs[0]); L.new(acc,dl.inputs['Selection']); L.new(dl.outputs[0],go.inputs[0])
     md=R.modifiers.new(MN,'NODES'); md.node_group=ng
     dg=bpy.context.evaluated_depsgraph_get(); print('QH roof faces',len(R.data.polygons),'->',len(R.evaluated_get(dg).data.polygons))
    CW=bpy.data.objects['QE_CCIS_drape_cover_wall_east_UNVERIFIED']
    me=bpy.data.meshes.new('QH_CCIS_NE_junction_cover_UNVERIFIED')
    v=[(29.25,201.3,140.84),(29.31,205.6,140.84),(29.31,205.6,153.1),(29.25,201.3,153.1)]
    me.from_pydata(v,[],[(0,1,2,3)]); me.update()
    for mm in CW.data.materials: me.materials.append(mm)
    J=bpy.data.objects.new(me.name,me); CW.users_collection[0].objects.link(J)
    sm=J.modifiers.new('solid','SOLIDIFY'); sm.thickness=0.25; sm.offset=-1
    cap=CW.data.polygons[0].material_index if len(CW.data.polygons) else 0
    for p in me.polygons: p.material_index=cap
    print('QH junction cover added')
    C['qh_rot']=tuple(C.rotation_euler); C['qh_shift']=C.data.shift_y
    pitch=C.rotation_euler.x-math.pi/2; C.rotation_euler.x=math.pi/2
    C.data.shift_y=C.data.shift_y+math.tan(pitch)*C.data.lens/C.data.sensor_width
    print('QH cam levelled, shift_y',round(C.data.shift_y,3))

if not REV:
    from mathutils import Vector
    cd=bpy.data.cameras.new('QH_CAM_closeup_ccis_east_junction'); cd.lens=35
    K=bpy.data.objects.new(cd.name,cd); C.users_collection[0].objects.link(K)
    K.location=(46.0,196.0,141.0); d=Vector((29.4,204.0,147.5))-K.location
    K.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); print('QH closeup cam added')

if not REV:
    W=CWo.matrix_world; Wi=W.inverted(); bot={}
    for v in CWo.data.vertices:
        p=W@v.co
        if p.y<207.0 and abs(p.z-145.35)<0.05: bot[str(v.index)]=v.co.z; v.co=Wi@Vector((p.x,p.y,140.84))
    CWo.data['qh_bot']=bot; CWo.data.update(); print('QH cover-wall south-end bottoms lowered',len(bot))

# pl (session pl, Nov 1 2026). ALL UNVERIFIED, removable; REVERT=1 undoes.
# Feliciano LiDAR roof hips/slopes read as stair-stepped, faceted shards (1 m LiDAR triangulation).
# Removable GN modifier PL_feliciano_roof_hip_smooth (after PF_feliciano_roof_tile_ring) on the evaluated mesh only:
#  weight w = 1 only where ALL of a vertex's faces are sloped forced-tile faces (slot 4), 0 on open boundary edges;
#  Z-only weighted Blur Attribute (IT iterations) of the position, mixed by w; tile faces smooth-shaded. Mesh/material untouched.
import bpy, os, sys
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv; OUT=os.environ.get('SAVEAS')
R='Feliciano School of Business roof (LiDAR)'; MOD='PL_feliciano_roof_hip_smooth'; NG='PL_feliciano_roof_hip_smooth_GN'; PR='UNVERIFIED_pl_hip_smooth'
r=bpy.data.objects[R]
if MOD in r.modifiers: r.modifiers.remove(r.modifiers[MOD])
if NG in bpy.data.node_groups: bpy.data.node_groups.remove(bpy.data.node_groups[NG])
if PR in r.keys(): del r[PR]
if not REV:
    IT=int(os.environ.get('IT','12')); SLOT=4
    ng=bpy.data.node_groups.new(NG,'GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    mi=N.new('GeometryNodeInputMaterialIndex'); c0=N.new('FunctionNodeCompare'); c0.data_type='INT'; c0.operation='EQUAL'; L(mi.outputs[0],c0.inputs[2]); c0.inputs[3].default_value=SLOT
    ev=N.new('GeometryNodeFieldOnDomain'); ev.domain='FACE'; ev.data_type='FLOAT'; L(c0.outputs['Result'],ev.inputs[0])
    evp=N.new('GeometryNodeFieldOnDomain'); evp.domain='POINT'; evp.data_type='FLOAT'; L(ev.outputs[0],evp.inputs[0])
    en=N.new('GeometryNodeInputMeshEdgeNeighbors'); c1=N.new('FunctionNodeCompare'); c1.data_type='INT'; c1.operation='EQUAL'; L(en.outputs['Face Count'],c1.inputs[2]); c1.inputs[3].default_value=1
    eve=N.new('GeometryNodeFieldOnDomain'); eve.domain='EDGE'; eve.data_type='FLOAT'; L(c1.outputs['Result'],eve.inputs[0])
    evb=N.new('GeometryNodeFieldOnDomain'); evb.domain='POINT'; evb.data_type='FLOAT'; L(eve.outputs[0],evb.inputs[0])
    gt=N.new('FunctionNodeCompare'); gt.data_type='FLOAT'; gt.operation='GREATER_THAN'; L(evb.outputs[0],gt.inputs[0]); gt.inputs[1].default_value=0.001
    full=N.new('ShaderNodeMath'); full.operation='GREATER_THAN'; L(evp.outputs[0],full.inputs[0]); full.inputs[1].default_value=float(os.environ.get('WT','0.999'))
    sw=N.new('GeometryNodeSwitch'); sw.input_type='FLOAT'; L(gt.outputs['Result'],sw.inputs['Switch']); L(full.outputs[0],sw.inputs['False']); sw.inputs['True'].default_value=0.0
    cap=N.new('GeometryNodeCaptureAttribute')
    try:
        cap.capture_items.new('FLOAT','w'); cap.domain='POINT'
    except Exception: cap.data_type='FLOAT'; cap.domain='POINT'
    L(gi.outputs[0],cap.inputs[0]); L(sw.outputs[0],cap.inputs[1])
    pos=N.new('GeometryNodeInputPosition')
    bl=N.new('GeometryNodeBlurAttribute'); bl.data_type='FLOAT_VECTOR'; L(pos.outputs[0],bl.inputs['Value']); bl.inputs['Iterations'].default_value=IT; L(cap.outputs[1],bl.inputs['Weight'])
    sx=N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0],sx.inputs[0]); sb=N.new('ShaderNodeSeparateXYZ'); L(bl.outputs['Value'],sb.inputs[0])
    mx=N.new('ShaderNodeMix'); mx.data_type='FLOAT'; L(cap.outputs[1],mx.inputs['Factor']); L(sx.outputs['Z'],mx.inputs['A']); L(sb.outputs['Z'],mx.inputs['B'])
    cb=N.new('ShaderNodeCombineXYZ'); L(sx.outputs['X'],cb.inputs['X']); L(sx.outputs['Y'],cb.inputs['Y']); L(mx.outputs['Result'],cb.inputs['Z'])
    sp=N.new('GeometryNodeSetPosition'); L(cap.outputs[0],sp.inputs['Geometry']); L(cb.outputs[0],sp.inputs['Position'])
    sm=N.new('GeometryNodeSetShadeSmooth'); L(sp.outputs[0],sm.inputs['Geometry']); L(c0.outputs['Result'],sm.inputs['Selection'])
    try: sm.domain='FACE'
    except Exception: pass
    L(sm.outputs[0],go.inputs[0])
    md=r.modifiers.new(MOD,'NODES'); md.node_group=ng
    r[PR]='Feliciano sloped tile faces Z-blurred x%d (boundary pinned) + smooth shaded; style fix, no roof survey'%IT
    dg=bpy.context.evaluated_depsgraph_get(); e=r.evaluated_get(dg); m=e.to_mesh(); mw=r.matrix_world
    import statistics
    d=[abs((mw@a.co).z-(mw@b.co).z) for a,b in zip(m.vertices,r.data.vertices)] if len(m.vertices)==len(r.data.vertices) else []
    print('PL_ROOF verts',len(m.vertices),len(r.data.vertices),'moved>2cm',sum(1 for x in d if x>0.02),'max dz',max(d) if d else None,'mods',[x.name for x in r.modifiers])
    e.to_mesh_clear()
else: print('REVERTED_PL_ROOF')
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED_AS',OUT)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

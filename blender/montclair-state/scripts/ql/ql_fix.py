# ql (Nov 2 2026, ~2:45 PM ET) CCIS east upper face, two removable fixes. REVERT=1 removes everything.
# FINDING: 2017/2023 LiDAR roof (in scene) shows the CCIS upper mass east edge running due N-S (high roof xmax 26.17 constant
# for y 204-237; low roof 141.1 from x 29.4), so qe's N-S cover wall at x 29.3 is CONSISTENT with LiDAR; qk's "23.6 deg off"
# was the OSM footprint angle, not the LiDAR edge. Kept the cover wall; fixed the two visible defects instead:
# (1) wedge: rotated OSM-wall / QF-skin / QF-window faces poking 0.05-0.4 m in front of the cover plane at the S junction
#     (x>29.36, y 202.6-206.6, z 141.2-154.6) -> GN QL_ccis_junction_wedge_trim on each host (face-centre box delete).
# (2) vertical slivers: the orphaned jamb islands (y-extent < 0.6 m, y 204-209.6; the rest of that window column is gone) of QF_qe_cover_wall_windows_kept_red in front of the cover
#     wall -> face attr QL_sliver + GN QL_cover_sliver_trim.
import bpy, os, numpy as np
REV=os.environ.get('REVERT')=='1'
HOSTS=['QF_CCIS_stucco_skin_recessed_openings_photo','QF_CCIS_windows_red_frames_spandrels_brackets_photo']
W='QF_qe_cover_wall_windows_kept_red_UNVERIFIED'
def clean(o,mn):
    m=o.modifiers.get(mn)
    if m: o.modifiers.remove(m)
    g=bpy.data.node_groups.get(mn+'_GN')
    if g: bpy.data.node_groups.remove(g)
    if 'UNVERIFIED_ql' in o: del o['UNVERIFIED_ql']
for h in HOSTS+['Center for Computing and Information Science walls']: clean(bpy.data.objects[h],'QL_ccis_junction_wedge_trim')
wo=bpy.data.objects[W]; clean(wo,'QL_cover_sliver_trim')
if 'QL_sliver' in wo.data.attributes: wo.data.attributes.remove(wo.data.attributes['QL_sliver'])
def gn(mn,boxsel=None,attr=None):
    ng=bpy.data.node_groups.new(mn+'_GN','GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    if attr:
        a=N.new('GeometryNodeInputNamedAttribute'); a.data_type='BOOLEAN'; a.inputs['Name'].default_value=attr; sel=a.outputs['Attribute']
    else:
        pos=N.new('GeometryNodeInputPosition'); sp=N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0],sp.inputs[0]); sel=None
        for k,(lo,hi) in enumerate(boxsel):
            for op,v in (('GREATER_THAN',lo),('LESS_THAN',hi)):
                c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L(sp.outputs[k],c.inputs[0]); c.inputs[1].default_value=v
                if sel is None: sel=c.outputs[0]
                else: b=N.new('FunctionNodeBooleanMath'); b.operation='AND'; L(sel,b.inputs[0]); L(c.outputs[0],b.inputs[1]); sel=b.outputs[0]
    dl=N.new('GeometryNodeDeleteGeometry'); dl.domain='FACE'; L(gi.outputs[0],dl.inputs['Geometry']); L(sel,dl.inputs['Selection']); L(dl.outputs[0],go.inputs[0])
    return ng
if REV: print('QL fix reverted')
else:
    dg=bpy.context.evaluated_depsgraph_get()
    for h in HOSTS:
        o=bpy.data.objects[h]; assert np.allclose(np.array(o.matrix_world),np.eye(4),atol=1e-5)
        n0=len(o.evaluated_get(dg).data.polygons)
        md=o.modifiers.new('QL_ccis_junction_wedge_trim','NODES'); md.node_group=gn('QL_ccis_junction_wedge_trim',boxsel=[(29.36,30.6),(202.6,206.6),(141.2,154.6)])
        o['UNVERIFIED_ql']='ql: faces poking in front of the N-S cover plane at the CCIS east S junction deleted (GN)'
        dg=bpy.context.evaluated_depsgraph_get(); print('WEDGE',h,n0,'->',len(o.evaluated_get(dg).data.polygons))
    me=wo.data; M=wo.matrix_world
    import bmesh
    bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    seen=set(); flag=np.zeros(len(me.polygons),bool); isl=0
    for f in bm.faces:
        if f.index in seen: continue
        st=[f]; comp=[]; seen.add(f.index)
        while st:
            g=st.pop(); comp.append(g.index)
            for e in g.edges:
                for g2 in e.link_faces:
                    if g2.index not in seen: seen.add(g2.index); st.append(g2)
        vs=np.array([tuple(M@v.co) for i in comp for v in bm.faces[i].verts])
        if vs[:,0].max()>29.35 and vs[:,0].min()>28.9 and 204<vs[:,1].mean()<209.6 and np.ptp(vs[:,1])<0.6:
            flag[comp]=True; isl+=1; print('  SLIVER y',vs[:,1].min().round(2),vs[:,1].max().round(2),'z',vs[:,2].min().round(2),vs[:,2].max().round(2),len(comp))
    bm.free()
    at=me.attributes.new('QL_sliver','BOOLEAN','FACE'); at.data.foreach_set('value',flag.tolist())
    md=wo.modifiers.new('QL_cover_sliver_trim','NODES'); md.node_group=gn('QL_cover_sliver_trim',attr='QL_sliver')
    wo['UNVERIFIED_ql']='ql: %d sliver window islands (<0.6 m wide) in front of the cover wall removed (attr QL_sliver + GN)'%isl
    print('SLIVERS',isl,'faces',int(flag.sum()))

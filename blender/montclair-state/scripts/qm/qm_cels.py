# qm (CELS): replace MAIN's CELS context massing (OSM walls + pleated LiDAR-roof drape + oo/or/ov/ow skirts) with the Oct 14/15
# north-file hero pass (North_CELS_20261014p massing + 61 au ground/arch windows + 188 at punched windows, linked from
# assets/windows_cels.blend). Same EPSG:6527 frame, so no transform. Context objects are HIDDEN (not deleted). L0 bottom verts
# (flat 137.22) are lowered to 136.6 by GN QM_cels_L0_footing so the base meets the 136.9-137.8 LiDAR ground. ALL UNVERIFIED.
# REVERT=1 removes everything appended (objects/meshes/materials recorded in data/qm/cels_added.json) and unhides.
import bpy, os, json
REV=os.environ.get('REVERT')=='1'; J='data/qm/cels_added.json'; PARENT='QM_CELS_hero_from_north_20261014p_UNVERIFIED'
HIDE=['Center for Environmental and Life Sciences roof (LiDAR)','Center for Environmental and Life Sciences walls']
HIDE+= [o.name for o in bpy.data.objects if 'Environmental and Life Sc' in o.name and o.type=='MESH' and (o.name.startswith(('el coping','OO_skirt','OR_base','OR_skirt_win','OV_gapfill_Center','OW_basefix')))]
if os.path.exists(J) and (REV or bpy.data.collections.get(PARENT)):
    d=json.load(open(J))
    for n in d['objects']:
        o=bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o,do_unlink=True)
    for n in d['collections']:
        c=bpy.data.collections.get(n)
        if c: bpy.data.collections.remove(c)
    for n in d['meshes']:
        m=bpy.data.meshes.get(n)
        if m and m.users==0: bpy.data.meshes.remove(m)
    for n in d['materials']:
        m=bpy.data.materials.get(n)
        if m and m.users==0: bpy.data.materials.remove(m)
    for n in d.get('node_groups',[]):
        g=bpy.data.node_groups.get(n)
        if g and g.users==0: bpy.data.node_groups.remove(g)
    for n in d['libraries']:
        l=bpy.data.libraries.get(n)
        if l and l.users==0: bpy.data.libraries.remove(l)
    for n,(hr,hv) in d['hidden'].items():
        o=bpy.data.objects.get(n)
        if o: o.hide_render=hr; o.hide_viewport=hv
    print('QM_CELS reverted')
if not REV:
    before={k:set(x.name for x in getattr(bpy.data,k)) for k in ('objects','meshes','materials','collections','libraries','node_groups','images')}
    src='north/montclair_north.blend'; CN=['North_CELS_20261014p','CELS_windows_ground_arch_20261015au','CELS_windows_modelled_20261015at']
    with bpy.data.libraries.load(src,link=False) as (a,b): b.collections=[c for c in a.collections if c in CN]
    par=bpy.data.collections.new(PARENT); bpy.context.scene.collection.children.link(par)
    for c in b.collections: par.children.link(c)
    d_new_mats=lambda: set(x.name for x in bpy.data.materials)-before['materials']
    hid={}
    for n in HIDE:
        o=bpy.data.objects.get(n)
        if o: hid[n]=(o.hide_render,o.hide_viewport); o.hide_render=True; o.hide_viewport=True
    # L0 footing GN
    L0=[o for o in bpy.data.collections['North_CELS_20261014p'].objects if o.name.startswith('CELS L0_south_box')][0]
    ng=bpy.data.node_groups.new('QM_cels_L0_footing_GN','GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; Lk=ng.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    pos=N.new('GeometryNodeInputPosition'); sp=N.new('ShaderNodeSeparateXYZ'); Lk(pos.outputs[0],sp.inputs[0])
    c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation='LESS_THAN'; Lk(sp.outputs[2],c.inputs[0]); c.inputs[1].default_value=137.4
    cx=N.new('ShaderNodeCombineXYZ'); Lk(sp.outputs[0],cx.inputs[0]); Lk(sp.outputs[1],cx.inputs[1]); cx.inputs[2].default_value=136.6
    st=N.new('GeometryNodeSetPosition'); Lk(gi.outputs[0],st.inputs['Geometry']); Lk(c.outputs[0],st.inputs['Selection']); Lk(cx.outputs[0],st.inputs['Position']); Lk(st.outputs[0],go.inputs[0])
    md=L0.modifiers.new('QM_cels_L0_footing','NODES'); md.node_group=ng
    # roof units read glowing white from the air: tone the appended (CELS-only) roofbox material copy to weathered light grey
    for o in par.all_objects:
        if o.name.startswith('CELS L_mech'):
            for mt in o.data.materials:
                if mt and mt.use_nodes and mt.name in d_new_mats():
                    b=[n for n in mt.node_tree.nodes if n.type=='BSDF_PRINCIPLED']
                    if b: b[0].inputs['Base Color'].default_value=(0.42,0.43,0.44,1); b[0].inputs['Roughness'].default_value=0.7
    for o in par.all_objects: o['UNVERIFIED_qm']='qm: CELS hero pass appended from north (Oct 14 p / Oct 15 at+au)'
    after={k:set(x.name for x in getattr(bpy.data,k)) for k in before}
    d={k:sorted(after[k]-before[k]) for k in before}; d['hidden']=hid
    json.dump(d,open(J,'w'),indent=0)
    print('QM_CELS appended',{k:len(v) for k,v in d.items()},'hidden',len(hid))

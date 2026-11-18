import bpy
for n in ('WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED','WS27_CollegeAve_carriageway_2020ortho','WS69_CollegeAve_gap_strip_curbs_UNVERIFIED'):
    o=bpy.data.objects[n]; me=o.data
    print('P2',n,'mats',[(m.name,[ (nd.type, tuple(round(v,3) for v in nd.inputs['Base Color'].default_value)) for nd in m.node_tree.nodes if nd.type=='BSDF_PRINCIPLED']) for m in me.materials if m],'mw_ident',o.matrix_world.is_identity)
    vs=[o.matrix_world@v.co for v in me.vertices]
    for xc in (-235,-215):
        sel=sorted([v for v in vs if abs(v.x-xc)<0.6],key=lambda v:v.y)
        print('P2 sec',n[:30],xc,[(round(v.x,2),round(v.y,2),round(v.z,2)) for v in sel][:24])
    print('P2 polys',len(me.polygons),'verts',len(vs))
# what object id order / index for curb_right first 20 verts
o=bpy.data.objects['WS27_CollegeAve_curb_right_UNVERIFIED']
print('P2 first',[tuple(round(c,2) for c in (o.matrix_world@v.co)) for v in o.data.vertices[:16]])
print('P2 poly0',[list(p.vertices) for p in o.data.polygons[:8]])

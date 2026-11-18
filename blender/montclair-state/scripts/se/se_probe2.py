import bpy
for mn in ('North_StudentCenter_membrane_UNVERIFIED','KM_RTU_housing_galv_UNVERIFIED','KM_RTU_curb_dark_UNVERIFIED','RZ2_North_SC_precast_ribbed_white','MH_Annex_coping_red_metal_photo2016'):
    m=bpy.data.materials.get(mn); print('SE_M',mn,m and m.users)
    if m and m.use_nodes:
        for n in m.node_tree.nodes:
            ins={i.name:(tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked and i.name in ('Base Color','Roughness','Metallic','Scale','Color')}
            print('   SE_N',n.type,n.name,ins)
for c in bpy.data.objects:
    if c.type=='CAMERA' and c.name.startswith(('RZ_CAM','SD_CAM','SA_CAM_obl')): print('SE_C',c.name,tuple(round(v,1) for v in c.location),tuple(round(v,2) for v in c.rotation_euler),c.data.lens)
o=bpy.data.objects['StudentCenter L1_high (LiDAR 152.75 m flat; outline UNVERIFIED +-1 m)'] if 'StudentCenter L1_high (LiDAR 152.75 m flat; outline UNVERIFIED +-1 m)' in bpy.data.objects else None
for ob in bpy.data.objects:
    if ob.name.startswith('StudentCenter L'): print('SE_O',repr(ob.name),[c.name for c in ob.users_collection],ob.matrix_world.translation[:], [ (p.material_index,round(p.normal.z,2)) for p in ob.data.polygons][:6])

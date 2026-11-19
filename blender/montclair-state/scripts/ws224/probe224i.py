import bpy
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; M=L.matrix_world; me=L.data
for fi in (0,6,12,171,172):
    p=me.polygons[fi]; print('P224 A f%d nz%+.2f '%(fi,p.normal.z)+' '.join('v%d(%.3f,%.3f,%.3f)'%((v,)+tuple(M@me.vertices[v].co)) for v in p.vertices))
F=bpy.data.objects['WS215_RHD_SE_core_street_level_walk_UNVERIFIED'] if 'WS215_RHD_SE_core_street_level_walk_UNVERIFIED' in bpy.data.objects else [o for o in bpy.data.objects if o.name.startswith('WS215_RHD_SE_core_street_level')][0]
print('P224 F name',F.name,len(F.data.vertices),len(F.data.polygons))
MF=F.matrix_world
for fi in (546,547):
    p=F.data.polygons[fi]; print('P224 F f%d nz%+.2f '%(fi,p.normal.z)+' '.join('v%d(%.3f,%.3f,%.3f)'%((v,)+tuple(MF@F.data.vertices[v].co)) for v in p.vertices))
for nm in ('WS69_CollegeAve_gap_strip_curb','WS67_CollegeAve_gap_asphalt'):
    o=[o for o in bpy.data.objects if o.name.startswith(nm)][0]
    dn=sum(1 for p in o.data.polygons if (o.matrix_world.to_3x3()@p.normal).z<-0.5); up=sum(1 for p in o.data.polygons if (o.matrix_world.to_3x3()@p.normal).z>0.5)
    print('P224',o.name,'down',dn,'up',up,'nf',len(o.data.polygons))

import bpy
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; M=L.matrix_world; me=L.data
print('P224 nv',len(me.vertices),'nf',len(me.polygons),'mods',[m.type+':'+m.name for m in L.modifiers])
for fi in (66,72,78,84,85,157,161,162,163,164,167,168,170):
    p=me.polygons[fi]
    print('P224 f%d n%+.2f '%(fi,p.normal.z)+' '.join('v%d(%.3f,%.3f,%.3f)'%((v,)+tuple(M@me.vertices[v].co)) for v in p.vertices))

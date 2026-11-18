import bpy,resource
print('W74 objs',len(bpy.data.objects),'maxrss MB',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024,flush=True)
for n in ('WS73_curb_back_lawn_verge_UNVERIFIED','gb_cogen_paving','fn_rhd_aisle_asphalt','WS72_Kasser_SW_RHD_core_sidewalk_landing','Terrain_LiDAR_DTM_1m'):
    o=[x for x in bpy.data.objects if x.name.startswith(n)]
    for x in o[:6]: print('W74',x.name,x.type,len(x.data.vertices) if x.type=='MESH' else '',[m.name for m in x.modifiers][:6],tuple(round(v,1) for v in x.location))

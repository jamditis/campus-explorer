import bpy
for n in ('Footpaths_OSM','PA_walk_panel_tone_chips_UNVERIFIED'):
    o=bpy.data.objects[n]; mw=o.matrix_world; me=o.data
    hits=[p for p in me.polygons if any(-256<(mw@me.vertices[v].co).x<-236 and -92<(mw@me.vertices[v].co).y<-68 for v in p.vertices)]
    print('P76',n,len(me.polygons),'in box',len(hits),[tuple(round(c,1) for c in (mw@p.center)) for p in hits[:6]],[m.name+':'+m.type for m in o.modifiers],flush=True)

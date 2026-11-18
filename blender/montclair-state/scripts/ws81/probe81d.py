import bpy
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src) as (fr,to): to.objects=['Footpaths_OSM','Roads_OSM']
R=(-240,-216,-134,-104)
for o in to.objects:
    me=o.data; mw=o.matrix_world
    for p in me.polygons:
        w=mw@p.center
        if R[0]<=w.x<=R[1] and R[2]<=w.y<=R[3]:
            vs=[mw@me.vertices[i].co for i in p.vertices]
            print('F',o.name[:9],p.index,'c',round(w.x,2),round(w.y,2),round(w.z,2),'area',round(p.area,3),'vs',[(round(v.x,2),round(v.y,2)) for v in vs],flush=True)

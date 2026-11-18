import bpy,bmesh
from mathutils import Vector
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
want=['WS27_CollegeAve_carriageway_2020ortho','WS27_CollegeAve_curb_left_UNVERIFIED','WS27_CollegeAve_curb_right_UNVERIFIED','Footpaths_OSM','Roads_OSM','WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges']
with bpy.data.libraries.load(src) as (fr,to):
    allnames=list(fr.objects); to.objects=[n for n in want if n in fr.objects]
print('WS76/79 names',[n for n in allnames if n.startswith(('WS76','WS79','WS77','WS75','WS80'))],flush=True)
R=(-234,-224,-130,-110)
for o in to.objects:
    if not o: continue
    print('MODS',o.name,[(m.type,m.name) for m in o.modifiers],o.hide_render)
    me=o.data; mw=o.matrix_world; c=0; zs=[]; mats={}
    for p in me.polygons:
        w=mw@p.center
        if R[0]<=w.x<=R[1] and R[2]<=w.y<=R[3]:
            c+=1; zs.append(w.z); mn=me.materials[p.material_index].name if me.materials else None; mats[mn]=mats.get(mn,0)+1
    print('INR',o.name,c,(round(min(zs),2),round(max(zs),2)) if zs else None,mats,flush=True)

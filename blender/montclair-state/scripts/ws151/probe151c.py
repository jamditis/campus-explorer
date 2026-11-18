import bpy
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(P, link=False) as (src,dst): dst.objects=['Curbs_granite_OSM']
cu=dst.objects[0]; mw=cu.matrix_world
import json; out={}
for i,s in enumerate(cu.data.splines):
    out[i]=[tuple(round(c,3) for c in (mw@p.co.to_3d())) for p in s.points]
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws151/curbs_osm.json','w'))
print("DONE",{k:len(v) for k,v in out.items()})

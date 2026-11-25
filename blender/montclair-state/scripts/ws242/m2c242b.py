# ws242 M2c slice 4 coherence pass: m2c242 dropped the soccer-stand risers/front walkway, the windscreen posts and the
# JO east walk (overlaps with PK fill / main's JO3/JP stair). Their dependants would float on their own, so they go too
# and wait for the stands/pitch batch (next session, with PK treated as ground): stand entry steps (fr/fse/fst),
# windscreen + hems, and the JS walk joints that sit on the dropped JO walk.
import bpy, json
MS='/workspace/nj-scenes/montclair-state/'
D=['fr_stand_entry_steps','fse_stand_entry_steps','fst_stand_entry_steps','fu_windscreen','fu_windscreen_hems']
D+=[o.name for o in bpy.data.objects if o.name.startswith('JS Walk joints on JO east walk')]
# probe242g seat check (ws242f): North_NEWalkEast_gk floats up to 1.04 m over main's Terrain_LiDAR_DTM_1m (264 of 355
# faces > 0.25 m); the SF north cap walk + curb lie 1.9-2.5 m UNDER WS68's north-DTM ground (all 240 faces buried).
# Both were built on the north file's own terrain; drop them (re-grade later if wanted).
D+=['North_NEWalkEast_gk']+[o.name for o in bpy.data.objects if o.name.startswith(('SF north cap asphalt walk','SF north cap edge curb'))]
k=0
for n in D:
    o=bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o); k+=1
_OFF[:]=[(a,b) for a,b in _OFF if a in bpy.data.objects]  # merge208: drop removed objects from the restore list
j=json.load(open(MS+'scripts/ws242/m2c_new242.json'))
j['kept']=[n for n in j['kept'] if n not in D]; j['dropped_coherence']=D
json.dump(j,open(MS+'scripts/ws242/m2c_new242.json','w'),indent=0)
json.dump(json.load(open(MS+'scripts/ws241/extra241.json'))+j['kept'],open(MS+'scripts/ws242/extra242.json','w'))
print('M2C242B removed',k,'kept',len(j['kept']),flush=True)

# ws238 data prep for ONE-SCENE M2 batch (c) site detail (read-only on north/montclair_north.blend).
# Candidates = north manifest (ws217) APPEND objects that are not trees (NT), lamps (NLamp: Joe's 2026-10-13 placeholder rule),
# University Hall (UH, Wyndle's), or already merged (M2a/M2b). Records north render visibility (hide_render on the object or any
# of its collections) and the ground region of the bbox: M3a (x -266..20, y >= 515), M3b (x -447..-200, y -116..515) or MAIN
# (overlaps main-native ground: needs a per-object decision, main's own design wins).
import bpy, json
MS='/workspace/nj-scenes/montclair-state/'
man=json.load(open(MS+'scripts/ws217/north_manifest217.json'))
done=set(json.load(open(MS+'scripts/ws234/m2b_new234.json')))
bpy.ops.wm.open_mainfile(filepath=MS+'north/montclair_north.blend',load_ui=False)
def colhidden(o):
    return any(c.hide_render for c in o.users_collection)
out={}
for n,(act,t,bb,nv,cols) in man.items():
    if act!='APPEND' or n in done or n.startswith(('NT_','NLamp','UH','University Hall',"Children's",'OF','NJT','Rail','Catenary','Ballast','Contact','Messenger','MH')): continue
    o=bpy.data.objects.get(n)
    if not o: continue
    x0,x1,y0,y1,z0,z1=bb
    if x0>=-266 and x1<=20 and y0>=515: reg='M3a'
    elif x0>=-447 and x1<=-200 and y0>=-116 and y1<=515: reg='M3b'
    else: reg='MAIN'
    out[n]=dict(type=t,bbox=bb,verts=nv,cols=cols,region=reg,hidden=bool(o.hide_render or colhidden(o)))
from collections import Counter
print('M2C cand',len(out),Counter((v['region'],v['hidden']) for v in out.values()),flush=True)
print('M2C top cols',Counter(v['cols'][0] if v['cols'] else '' for v in out.values() if not v['hidden']).most_common(15),flush=True)
json.dump(out,open(MS+'scripts/ws238/m2c_candidates238.json','w'),indent=0)

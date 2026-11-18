import bpy,json
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (s,d): d.objects=['Terrain_LiDAR_DTM_1m']
T=d.objects[0]; bpy.context.scene.collection.objects.link(T)
dg=bpy.context.evaluated_depsgraph_get(); E=T.evaluated_get(dg); me=E.to_mesh(); mw=T.matrix_world
raw={}
for i,v in enumerate(T.data.vertices):
    w=mw@v.co
    if -222<w.x<-200 and -96<w.y<-82: raw[(round(w.x,2),round(w.y,2))]=(i,w.z)
ev=[]
for v in me.vertices:
    w=mw@v.co
    if -222<w.x<-200 and -96<w.y<-82: ev.append((w.x,w.y,w.z))
print("EV",len(me.vertices),len(T.data.vertices),len(ev))
match=0;diffs=[]
for x,y,z in ev:
    k=(round(x,2),round(y,2))
    if k in raw: match+=1; diffs.append(z-raw[k][1])
import statistics
print("MATCH",match, "diff min/max/median", min(diffs) if diffs else None, max(diffs) if diffs else None, statistics.median(diffs) if diffs else None)
json.dump(ev,open('/workspace/nj-scenes/montclair-state/scripts/ws98/teval98.json','w'))

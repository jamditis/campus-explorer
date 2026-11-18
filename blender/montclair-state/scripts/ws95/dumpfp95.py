import bpy,json
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (s,d): d.objects=['Footpaths_OSM']
o=d.objects[0]; bpy.context.scene.collection.objects.link(o)
print("FP mods",[(m.type,m.name,getattr(m,'node_group',None) and m.node_group.name) for m in o.modifiers], o.type, len(o.data.vertices), tuple(o.location), o.data.name, o.data.users)
mw=o.matrix_world
B=(-235,-190,-110,-75)
def inb(v): return B[0]<v.x<B[1] and B[2]<v.y<B[3]
src=[(i,list(mw@v.co)) for i,v in enumerate(o.data.vertices) if inb(mw@v.co)]
fs=[list(p.vertices) for p in o.data.polygons if all(inb(mw@o.data.vertices[k].co) for k in p.vertices)]
ed=[list(e.vertices) for e in o.data.edges if all(inb(mw@o.data.vertices[k].co) for k in e.vertices)]
dg=bpy.context.evaluated_depsgraph_get(); me=o.evaluated_get(dg).to_mesh()
ev=[list(mw@v.co) for v in me.vertices]
evi=[i for i,v in enumerate(ev) if B[0]<v[0]<B[1] and B[2]<v[1]<B[3]]
S=set(evi)
ef=[list(p.vertices) for p in me.polygons if all(k in S for k in p.vertices)]
json.dump({'src':src,'sf':fs,'se':ed,'ev':{i:ev[i] for i in evi},'ef':ef},open('scripts/ws95/fp95.json','w'))
print("FP src",len(src),"sf",len(fs),"se",len(ed),"eval",len(evi),len(ef))

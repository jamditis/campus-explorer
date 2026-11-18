import bpy, numpy as np, json
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['Footpaths_OSM','CCOM_dock_apron']
B=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws205/bbox205.json'))
near=[n for n,v in B.items() if v[0]=='MESH' and not v[1] and not (v[3]<0 or v[2]>11 or v[5]<-40 or v[4]>-28) and v[6]<140]
print('NEAR',near)
with bpy.data.libraries.load(F) as (a,b): b.objects=[n for n in set(names+near) if n in set(a.objects)]
for o in b.objects:
    for m in o.modifiers: m.show_viewport=False
    me=o.data; mw=o.matrix_world
    V=np.array([tuple(mw@v.co) for v in me.vertices]) if len(me.vertices) else np.zeros((0,3))
    sel=(V[:,0]>-1)&(V[:,0]<12)&(V[:,1]>-42)&(V[:,1]<-26) if len(V) else []
    print('OBJ',o.name,len(me.vertices),len(me.polygons),[ (m.type,m.name,m.node_group.name if m.type=='NODES' and m.node_group else '') for m in o.modifiers],[s.material.name if s.material else None for s in o.material_slots][:4],'nsel',int(np.sum(sel)) if len(V) else 0)
    if o.name.startswith(('Footpaths_OSM','CCOM_dock_apron','WS206','Footpath control','Lawn_worn','WS32')):
        P=[[tuple(mw@me.vertices[i].co) for i in p.vertices] for p in me.polygons]
        P=[p for p in P if any(-1<q[0]<12 and -42<q[1]<-26 for q in p)]
        json.dump(P,open('/tmp/p209_'+o.name+'.json','w'))
        if o.name=='Footpaths_OSM':
            for m in o.modifiers:
                if m.type=='NODES':
                    print('GN',m.node_group.name,[ (k,str(m[k])[:40]) for k in m.keys()][:12])

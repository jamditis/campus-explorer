import bpy, collections
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
print('TI mods',[(m.name,m.type,getattr(m,'node_group',None) and m.node_group.name) for m in T.modifiers])
print('TI mw',tuple(T.matrix_world.translation), len(T.data.vertices), len(T.data.polygons))
mw=T.matrix_world
vs=[(mw@v.co) for v in T.data.vertices]
sel=[v for v in vs if 122<v.x<140 and 160<v.y<185]
print('TI n',len(sel))
xs=sorted(set(round(v.x,2) for v in sel)); print('TI xs',xs[:12])
zs=collections.Counter(round(v.z,3) for v in sel); print('TI zdistinct',len(zs), sorted(zs)[:30])
row=sorted([v for v in sel if abs(v.y-172)<0.5],key=lambda v:v.x); print('TI row',[(round(v.x,1),round(v.z,3)) for v in row])
for o in bpy.data.objects:
    for m in o.modifiers:
        if m.type=='NODES' and m.node_group:
            for n in m.node_group.nodes:
                if n.type=='OBJECT_INFO' and n.inputs[0].default_value==T: print('TI ref',o.name,m.name)
            for k in m.keys():
                if m[k] is T: print('TI refsock',o.name,m.name)
        if getattr(m,'target',None)==T: print('TI target',o.name,m.name,m.type)

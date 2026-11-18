import bpy, numpy as np, math
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data
print('PB mw', tuple(T.matrix_world.translation), 'mods',[(m.name,m.type) for m in T.modifiers], 'nv',len(me.vertices),'nf',len(me.polygons), 'smooth', sum(p.use_smooth for p in me.polygons))
print('PB mats',[s.material.name if s.material else None for s in T.material_slots], 'attrs',[(a.name,a.domain,a.data_type) for a in me.attributes])
co=np.zeros(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
X0,X1,Y0,Y1=80,180,130,240
cnt=0; big=0
for p in me.polygons:
    c=p.center
    if X0<=c.x<=X1 and Y0<=c.y<=Y1:
        cnt+=1
        vs=[co[i] for i in p.vertices]; mx=max(np.linalg.norm(vs[i]-vs[(i+1)%len(vs)]) for i in range(len(vs)))
        if mx>2: big+=1
print('PB box faces',cnt,'fan(>2m)',big)
for o in bpy.data.objects:
    for m in o.modifiers:
        if m.type=='NODES' and m.node_group:
            refs=set()
            for n in m.node_group.nodes:
                if n.bl_idname=='GeometryNodeObjectInfo':
                    ob=n.inputs['Object'].default_value
                    if ob: refs.add(ob.name)
            for k in m.keys():
                v=m[k]
                if isinstance(v,bpy.types.Object): refs.add(v.name)
            if 'Terrain_LiDAR_DTM_1m' in refs: print('PB uses terrain:',o.name,m.name)

import bpy, json
R='/workspace/nj-scenes/montclair-state'; rep={}
for on in ['Terrain_LiDAR_DTM_1m']+[o.name for o in bpy.data.objects if o.name.startswith(('QG','QH','QI'))][:12]:
    o=bpy.data.objects.get(on)
    if not o or o.type!='MESH': continue
    rep[on]={'mats':[s.material.name if s.material else None for s in o.material_slots],'mods':[(m.name,m.type) for m in o.modifiers],'nf':len(o.data.polygons)}
mats=set(m for v in rep.values() for m in v['mats'] if m)
md={}
for mn in mats:
    m=bpy.data.materials[mn]
    md[mn]={'users':m.users,'nodes':[(n.name,n.bl_idname,getattr(getattr(n,'image',None),'name',None)) for n in m.node_tree.nodes],
     'links':[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links]}
rep['_mats']=md
wh=bpy.data.materials['WH_east_dorm_patch_tone_UNVERIFIED']
rep['_WH_WM_map']=[(n.name,list(n.inputs['Location'].default_value),list(n.inputs['Scale'].default_value)) for n in wh.node_tree.nodes if n.name=='WM_map']
json.dump(rep,open(R+'/data/wr/inspect.json','w'),indent=1); print('DONE')

import bpy, json
o=bpy.data.objects['ey_rhd_se_crosswalks']; M=o.matrix_world
V=[list((M@v.co)[:]) for v in o.data.vertices]; P=[list(p.vertices) for p in o.data.polygons]
nz=[p.normal.z for p in o.data.polygons]
json.dump({'ey_rhd_se_crosswalks':{'V':V,'P':P,'NZ':nz}},open('/workspace/nj-scenes/montclair-state/scripts/ws219/cw219.json','w'))
print('D219',len(V),len(P),'mats',[s.material.name for s in o.material_slots if s.material],'users',o.data.users,'mods',[m.type for m in o.modifiers],'parent',o.parent,'children',[c.name for c in o.children],flush=True)
print('D219 users of mat',[x.name for x in bpy.data.objects if x.type=='MESH' and any(s.material and s.material.name=='ey_crosswalk_paint' for s in x.material_slots)][:10],flush=True)

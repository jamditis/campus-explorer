import bpy, json
o=[x for x in bpy.data.objects if x.name.startswith('SF_Lot38_stall_stripes')][0]
M=o.matrix_world; R=M.to_3x3()
V=[list((M@v.co)[:]) for v in o.data.vertices]
F=[(list(p.vertices),p.material_index) for p in o.data.polygons if abs((R@p.normal).z)>0.5]
m=o.material_slots[0].material
b=[n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0]
col=list(b.inputs['Base Color'].default_value); lk=bool(b.inputs['Base Color'].links)
a=bpy.data.materials['SF_asphalt_worn_UNVERIFIED']; ab=[n for n in a.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0]
print('P220 stripes faces',len(F),'col',[round(x,3) for x in col],'collinked',lk,'asph basecol linked',bool(ab.inputs['Base Color'].links),'rough linked',bool(ab.inputs['Roughness'].links),ab.inputs['Roughness'].default_value)
json.dump({o.name:{'V':V,'F':F,'mats':[[m.name,col]]}},open('/workspace/nj-scenes/montclair-state/scripts/ws220/paint220.json','w'))

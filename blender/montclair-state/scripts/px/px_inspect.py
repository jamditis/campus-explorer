import bpy, json, collections
w=bpy.data.objects['Dickson Hall walls']; mw=w.matrix_world; me=w.data
print('WALL',len(me.vertices),len(me.polygons),[m.name if m else None for m in me.materials],[u.name for u in me.uv_layers], dict(w.items()).keys())
# boundary edges
ec=collections.Counter()
for p in me.polygons:
    for k in p.edge_keys: ec[k]+=1
top=[]
for k,c in ec.items():
    if c!=1: continue
    a=mw@me.vertices[k[0]].co; b=mw@me.vertices[k[1]].co
    if min(a.z,b.z)>146 and ((a.xy-b.xy).length>0.05): top.append((a,b))
sl=[(a,b) for a,b in top if abs(a.z-b.z)>0.05]
lv=[(a,b) for a,b in top if abs(a.z-b.z)<=0.05]
print('TOPB',len(top),'sloped',len(sl),'level',len(lv))
for a,b in sorted(sl,key=lambda t:(round(t[0].x),t[0].y))[:400]:
    print('S %.2f %.2f %.2f -> %.2f %.2f %.2f'%(a.x,a.y,a.z,b.x,b.y,b.z))
zs=collections.Counter(round(a.z,1) for a,b in lv); print('LEVELZ',zs.most_common(10))
for n in ['Roof_coping','Dickson Hall roof (LiDAR)','PV_Dickson_clipped_slot_frames_UNVERIFIED']:
    o=bpy.data.objects.get(n); 
    if o: print(n,o.type,len(o.data.vertices),[m.name for m in o.data.materials if m][:6])
m=bpy.data.materials['PE_Dickson_brick_buff_no_red_spandrel_UNVERIFIED']; print('MATUSERS',m.users)
print([ (o.name) for o in bpy.data.objects if 'coping' in o.name.lower()][:20])

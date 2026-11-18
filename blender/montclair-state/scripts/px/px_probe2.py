import bpy, collections
w=bpy.data.objects['Dickson Hall walls']; me=w.data; mw=w.matrix_world
inf=bpy.data.objects['PX_Dickson_wing_parapet_infill_UNVERIFIED']
IV=set((round(c.x,2),round(c.y,2)) for c in (inf.matrix_world@v.co for v in inf.data.vertices))
ec=collections.Counter()
for p in me.polygons:
    for k in p.edge_keys: ec[k]+=1
for k,c in ec.items():
    if c!=1: continue
    a=mw@me.vertices[k[0]].co; b=mw@me.vertices[k[1]].co; m=(a+b)/2
    if (a.xy-b.xy).length<0.05 or min(a.z,b.z)<147.5 or not (m.x<-157.5 and 77<m.y<160.5): continue
    cov=(round(a.x,2),round(a.y,2)) in IV and (round(b.x,2),round(b.y,2)) in IV
    if max(a.z,b.z)<151.29 and not cov: print('UNCOV %.2f %.2f %.2f -> %.2f %.2f %.2f'%(a.x,a.y,a.z,b.x,b.y,b.z))

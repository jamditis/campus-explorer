import bpy, json
out={}
for o in bpy.data.objects:
    if 'Environmental and Life' in o.name or 'CELS' in o.name:
        out.setdefault('names',[]).append((o.name,o.type,o.hide_render, len(o.data.vertices) if o.type=='MESH' else 0, [m.name for m in o.modifiers] if o.type=='MESH' else []))
w=bpy.data.objects['Center for Environmental and Life Sciences walls']; me=w.data; M=w.matrix_world
segs=[]
for p in me.polygons:
    if abs(p.normal.z)<0.2:
        vs=[M@me.vertices[i].co for i in p.vertices]
        zs=[v.z for v in vs]
        xy=sorted({(round(v.x,2),round(v.y,2)) for v in vs})
        segs.append([xy, min(zs), max(zs), list(p.normal)])
out['segs']=segs
for n in [x[0] for x in out['names']]:
    o=bpy.data.objects[n]
    if o.type=='MESH' and 'roof' in n.lower():
        out.setdefault('roofs',{})[n]=[[ (M2:=o.matrix_world)@v.co for v in o.data.vertices][i][:] for i in range(0,len(o.data.vertices),max(1,len(o.data.vertices)//400))]
json.dump(out,open('data/ov/cels_walls.json','w'),default=list)
print('DONE',len(segs)); [print('N',x) for x in out['names']]

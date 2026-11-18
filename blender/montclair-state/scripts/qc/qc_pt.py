import bpy
o=bpy.data.objects['PT_Calcia_wall_top_infill_UNVERIFIED']; me=o.data; mw=o.matrix_world
print('PTM',[m.name for m in me.materials],len(me.vertices),len(me.polygons),[l.name for l in me.uv_layers])
vs=sorted([mw@v.co for v in me.vertices if (mw@v.co).y>195 and (mw@v.co).x<-104 and (mw@v.co).y<199],key=lambda v:(v.y,v.z))
for v in vs: print('PTV',tuple(round(x,3) for x in v))
for p in me.polygons:
    c=mw@p.center
    if c.y>195.5 and c.y<199 and c.x<-104: print('PTF',p.index,tuple(round(x,2) for x in c),tuple(round(x,2) for x in p.normal),len(p.vertices),p.material_index)
w=bpy.data.objects['Calcia Hall walls']
for i in (66,487,488,67):
    p=w.data.polygons[i]; print('WV',i,[tuple(round(x,3) for x in (w.matrix_world@w.data.vertices[v].co)) for v in p.vertices])

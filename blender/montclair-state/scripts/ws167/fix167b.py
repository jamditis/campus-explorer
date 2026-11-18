# ws167b: (a) WS162 W shoulder bank (S of y -199) hung 1.5 m above the LiDAR toe once the skirt dropped -> clamp its verts to DTM+0.02
# (b) N of the WS166 bank (y > -171.5, s 27..34) the skirt still sat ~0.9 m above the bank -> lawn DTM patch t 0.3..8.3 + add to the skirt target
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws167/hdr167.py').read())
n=0
for o in [o for o in OB if o.name.startswith('WS162_Lot3_W_shoulder_lawn_bank')]:
    mw=o.matrix_world; mi=mw.inverted()
    for v in o.data.vertices:
        w=mw@v.co
        if tW(w.x,w.y)>2.0:
            z=dz(w.x,w.y)+0.02
            if w.z>z: w.z=z; v.co=mi@w; n+=1
    o.data.update()
print('B clamp WS162 verts',n,flush=True)
for o in [o for o in OB if o.name.startswith('WS167b_')]: OB.remove(o)
bm=bmesh.new(); G={}; SS=list(np.arange(27.0,34.01,1.0)); TT=list(np.arange(0.3,8.31,1.0))
for s in SS:
    for t in TT:
        x,y=P2(s,t); G[(s,t)]=bm.verts.new((x,y,dz(x,y)-0.02))
for i in range(len(SS)-1):
    for j in range(len(TT)-1): bm.faces.new((G[(SS[i],TT[j])],G[(SS[i],TT[j+1])],G[(SS[i+1],TT[j+1])],G[(SS[i+1],TT[j])]))
gp=mk('WS167b_bank_N_of_Lot3_curb_end_LiDAR2023_1m',bm,[lawn])
tgt=OB['WS167_skirt_target_hidden']; tb=bmesh.new(); tb.from_mesh(tgt.data)
for p in gp.data.polygons: tb.faces.new([tb.verts.new(gp.data.vertices[i].co) for i in p.vertices])
tb.to_mesh(tgt.data); tb.free()
a=tgt.data.attributes.get('wv_in') or tgt.data.attributes.new('wv_in','FLOAT','POINT'); a.data.foreach_set('value',[0.10]*len(tgt.data.vertices))
tgt.data.update(); print('B target faces',len(tgt.data.polygons),flush=True)
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for s,t in ((0,9),(-2,12),(30,4),(32,2),(28,6)):
    x,y=P2(s,t); r=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1))); print('PROBE s%d t%d'%(s,t),r[4].name[:40] if r[0] else None,round(r[1].z,2) if r[0] else None,'dtm',round(dz(x,y),2),flush=True)


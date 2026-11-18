import bpy,bmesh,os
o=bpy.data.objects['Susan A. Cole Hall roof (LiDAR)']
me=o.data; mw=o.matrix_world
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
flat=set(f.index for f in bm.faces if f.material_index==0 and (mw.to_3x3()@f.normal).normalized().z>0.95)
seen=set(); isl=[]
for fi in flat:
    if fi in seen: continue
    st=[fi]; comp=[]; seen.add(fi)
    while st:
        i=st.pop(); comp.append(i)
        for e in bm.faces[i].edges:
            for g in e.link_faces:
                if g.index in flat and g.index not in seen: seen.add(g.index); st.append(g.index)
    a=sum(bm.faces[i].calc_area() for i in comp); c=sum((mw@bm.faces[i].calc_center_median() for i in comp),__import__('mathutils').Vector())/len(comp)
    isl.append((a,comp,c))
isl.sort(key=lambda x:-x[0])
TH=float(os.environ.get('TH','30'))
force=[]
for a,comp,c in isl:
    print('ISL area %.1f n %d c %s %s'%(a,len(comp),[round(x,1) for x in c],'FORCE' if a<TH else 'keep'))
    if a<TH: force+=comp
print('total flat',len(flat),'force',len(force))
bm.free()
if os.environ.get('APPLY')=='1':
    at=me.attributes.get('em_ringforce') or me.attributes.new('em_ringforce','FLOAT','FACE')
    vals=[0.0]*len(me.polygons)
    for i in force: vals[i]=1.0
    at.data.foreach_set('value',vals)
    bpy.ops.wm.save_mainfile()
    print('SAVED')

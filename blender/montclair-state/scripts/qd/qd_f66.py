import bpy, math
o=bpy.data.objects['Calcia Hall walls']; me=o.data; uv=me.uv_layers.get('facade') or me.uv_layers.active
print('UVL',[l.name for l in me.uv_layers],'slots',[m.name if m else None for m in me.materials])
for fi in (66,67,488,68):
    p=me.polygons[fi]; us=[uv.data[li].uv for li in p.loop_indices]
    U=[u.x for u in us]; V=[u.y for u in us]; W=[o.matrix_world@me.vertices[v].co for v in p.vertices]
    print('F',fi,'slot',p.material_index,'nverts',len(p.vertices),'U %.3f..%.3f V %.3f..%.3f'%(min(U),max(U),min(V),max(V)),'area %.2f'%p.area,
      'x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f'%(min(w.x for w in W),max(w.x for w in W),min(w.y for w in W),max(w.y for w in W),min(w.z for w in W),max(w.z for w in W)))
    # full painted windows: columns k with [2.4k+0.75, 2.4k+1.65] inside U range
    k0=math.floor(min(U)/2.4)-1; cols=[k for k in range(k0,k0+int((max(U)-min(U))/2.4)+4) if 2.4*k+0.75>=min(U)-1e-3 and 2.4*k+1.65<=max(U)+1e-3]
    part=[k for k in range(k0,k0+int((max(U)-min(U))/2.4)+4) if (2.4*k+1.65>min(U) and 2.4*k+0.75<max(U)) and k not in cols]
    print('   full cols',cols,'partial cols',part)
